"""External official-split runner for bounded AD-GBC KSDD2 transfer tests.

This adapter imports pinned author architectures unchanged.  It deliberately
does not present itself as author code: its role is to preserve KSDD2's official
test split and emit identical records for the baseline, scalar-scale and
anisotropic arms.
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import random
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import albumentations as A
import cv2
import numpy as np
import torch
from sklearn.metrics import average_precision_score
from sklearn.model_selection import StratifiedShuffleSplit
from torch import nn
from torch.utils.data import DataLoader, Dataset


@dataclass(frozen=True)
class Sample:
    sample_id: str
    image: Path
    mask: Path
    foreground: int


class KSDD2Dataset(Dataset):
    def __init__(self, samples: list[Sample], transform: A.Compose):
        self.samples = samples
        self.transform = transform

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int):
        sample = self.samples[index]
        image = cv2.imread(str(sample.image))
        mask = cv2.imread(str(sample.mask), cv2.IMREAD_GRAYSCALE)[..., None]
        if image is None or mask is None:
            raise RuntimeError(f"Unreadable pair: {sample.sample_id}")
        augmented = self.transform(image=image, mask=mask)
        image = augmented["image"].astype("float32").transpose(2, 0, 1)
        mask = (augmented["mask"].astype("float32") / 255.0).transpose(2, 0, 1)
        return torch.from_numpy(image), torch.from_numpy(mask), sample.sample_id


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=("backbone", "isotropic", "adgbc"), required=True)
    parser.add_argument("--ad-root", type=Path, required=True)
    parser.add_argument("--rolling-root", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--patience", type=int, default=15)
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True


def paired_samples(directory: Path) -> list[Sample]:
    samples: list[Sample] = []
    for image in sorted(directory.glob("*.png")):
        if image.stem.endswith("_GT") or "(copy)" in image.name:
            continue
        mask = directory / f"{image.stem}_GT.png"
        if not mask.exists():
            raise RuntimeError(f"Missing mask for {image.name}")
        raw = cv2.imread(str(mask), cv2.IMREAD_GRAYSCALE)
        if raw is None:
            raise RuntimeError(f"Unreadable mask {mask}")
        samples.append(Sample(image.stem, image, mask, int(np.any(raw > 0))))
    return samples


def split_train(samples: list[Sample], seed: int, smoke: bool) -> tuple[list[Sample], list[Sample]]:
    if smoke:
        positives = [sample for sample in samples if sample.foreground][:5]
        negatives = [sample for sample in samples if not sample.foreground][:5]
        chosen = positives + negatives
        if len(chosen) != 10:
            raise RuntimeError("Smoke set requires five foreground and five background samples")
        return chosen[:8], chosen[8:]
    labels = np.asarray([sample.foreground for sample in samples])
    splitter = StratifiedShuffleSplit(n_splits=1, test_size=.2, random_state=seed)
    train_idx, val_idx = next(splitter.split(np.zeros((len(samples), 1)), labels))
    return [samples[i] for i in train_idx], [samples[i] for i in val_idx]


def import_author_modules(root: Path, arm: str):
    sys.path.insert(0, str(root))
    if arm == "backbone":
        return importlib.import_module("archs"), importlib.import_module("losses")
    return importlib.import_module("archs_GBC"), importlib.import_module("losses")


def build_model(arm: str, ad_root: Path, rolling_root: Path, device: torch.device):
    module, losses = import_author_modules(rolling_root if arm == "backbone" else ad_root, arm)
    if arm == "backbone":
        model = module.Rolling_Unet_S(num_classes=1, input_channels=3).to(device)
        criterion = losses.BCEDiceLoss().to(device)
        geometry = False
    else:
        model = module.GBC_Rolling_Unet_S(
            num_classes=1,
            input_channels=3,
            gbc_num_balls=32,
            use_diag_cov=arm == "adgbc",
            tau=1.0,
        ).to(device)
        criterion = losses.BCEDiceWithGeometryLoss(div_weight=.01, scale_weight=.1).to(device)
        geometry = True
    optimizer = torch.optim.Adam(
        [
            {"params": [p for n, p in model.named_parameters() if p.requires_grad and "centers" not in n.lower() and "gbc" not in n.lower()], "lr": 1e-4, "weight_decay": 1e-4},
            {"params": [p for n, p in model.named_parameters() if p.requires_grad and ("centers" in n.lower() or "gbc" in n.lower())], "lr": 1e-2, "weight_decay": 1e-4},
        ],
    )
    optimizer.param_groups[:] = [group for group in optimizer.param_groups if group["params"]]
    return model, criterion, optimizer, geometry


def loss_and_logits(output, target, model, criterion, geometry: bool):
    if geometry:
        loss = criterion(output, target, model)
        logits = output[0] if isinstance(output, tuple) else output
    else:
        loss = criterion(output, target)
        logits = output
    return loss, logits


def dice_iou(logits: torch.Tensor, target: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    prediction = torch.sigmoid(logits) > .5
    truth = target > .5
    intersection = (prediction & truth).sum(dim=(1, 2, 3)).float()
    union = (prediction | truth).sum(dim=(1, 2, 3)).float()
    total = prediction.sum(dim=(1, 2, 3)).float() + truth.sum(dim=(1, 2, 3)).float()
    return ((2 * intersection + 1e-7) / (total + 1e-7)).mean(), ((intersection + 1e-7) / (union + 1e-7)).mean()


def evaluate(model, loader, criterion, geometry: bool, device: torch.device):
    model.eval()
    losses, dices, ious, scores, targets = [], [], [], [], []
    with torch.no_grad():
        for image, mask, _ in loader:
            image, mask = image.to(device), mask.to(device)
            output = model(image)
            loss, logits = loss_and_logits(output, mask, model, criterion, geometry)
            dice, iou = dice_iou(logits, mask)
            losses.append(float(loss.item()))
            dices.append(float(dice.item()))
            ious.append(float(iou.item()))
            scores.append(torch.sigmoid(logits).cpu().numpy().ravel())
            targets.append(mask.cpu().numpy().ravel())
    score = np.concatenate(scores)
    target = np.concatenate(targets)
    brier = float(np.mean((score - target) ** 2))
    bins = np.linspace(0, 1, 11)
    ece = 0.0
    for lo, hi in zip(bins[:-1], bins[1:]):
        selected = (score >= lo) & (score < hi if hi < 1 else score <= hi)
        if selected.any():
            ece += selected.mean() * abs(score[selected].mean() - target[selected].mean())
    auprc = float(average_precision_score(target, score)) if np.unique(target).size == 2 else float("nan")
    return {
        "loss": float(np.mean(losses)), "dice": float(np.mean(dices)), "iou": float(np.mean(ious)),
        "pixel_auprc": auprc, "brier": brier, "ece": float(ece),
    }


def main() -> None:
    args = parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA required")
    set_seed(args.seed)
    device = torch.device("cuda")
    train_all = paired_samples(args.data_root / "train")
    test_samples = paired_samples(args.data_root / "test")
    if len(train_all) != 2331 or len(test_samples) != 1004:
        raise RuntimeError(f"Unexpected official KSDD2 pairs: {len(train_all)}, {len(test_samples)}")
    train_samples, val_samples = split_train(train_all, args.seed, args.smoke)
    if args.smoke:
        test_for_run = [sample for sample in test_samples if sample.foreground][:5] + [sample for sample in test_samples if not sample.foreground][:5]
    else:
        test_for_run = test_samples
    if args.smoke and len(test_for_run) != 10:
        raise RuntimeError("Smoke test requires five foreground and five background samples")
    train_tf = A.Compose([A.RandomRotate90(), A.HorizontalFlip(), A.Resize(256, 256), A.Normalize()])
    eval_tf = A.Compose([A.Resize(256, 256), A.Normalize()])
    train_loader = DataLoader(KSDD2Dataset(train_samples, train_tf), batch_size=args.batch_size, shuffle=True, num_workers=args.num_workers, drop_last=False)
    val_loader = DataLoader(KSDD2Dataset(val_samples, eval_tf), batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers)
    test_loader = DataLoader(KSDD2Dataset(test_for_run, eval_tf), batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers)
    model, criterion, optimizer, geometry = build_model(args.arm, args.ad_root, args.rolling_root, device)
    run_dir = args.output_root / f"{args.arm}_seed{args.seed}{'_smoke' if args.smoke else ''}"
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "arm": args.arm, "seed": args.seed, "smoke": args.smoke, "train_ids": [s.sample_id for s in train_samples],
        "val_ids": [s.sample_id for s in val_samples], "test_count": len(test_for_run),
        "geometry_loss": geometry, "device": torch.cuda.get_device_name(0),
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    best, stale, started = -1.0, 0, time.perf_counter()
    rows = []
    for epoch in range(args.epochs):
        model.train()
        for image, mask, _ in train_loader:
            image, mask = image.to(device), mask.to(device)
            output = model(image)
            loss, _ = loss_and_logits(output, mask, model, criterion, geometry)
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
        validation = evaluate(model, val_loader, criterion, geometry, device)
        rows.append({"epoch": epoch, **validation})
        if validation["dice"] > best:
            best, stale = validation["dice"], 0
            torch.save(model.state_dict(), run_dir / "model.pt")
        else:
            stale += 1
        if stale >= args.patience:
            break
    model.load_state_dict(torch.load(run_dir / "model.pt", map_location=device, weights_only=True))
    test = evaluate(model, test_loader, criterion, geometry, device)
    peak = int(torch.cuda.max_memory_allocated(device))
    result = {"arm": args.arm, "seed": args.seed, "smoke": args.smoke, "epochs_completed": len(rows), "wall_seconds": time.perf_counter() - started, "peak_cuda_bytes": peak, "test": test, "validation_history": rows}
    (run_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
