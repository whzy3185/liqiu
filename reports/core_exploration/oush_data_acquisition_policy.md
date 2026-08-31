# Oush data-acquisition policy

Effective date: 2026-08-31  
Scope: all new datasets acquired for this branch's experiments and reproductions.

## Source and provenance order

1. Identify the paper/author's official data source, license, expected file
   count, directory structure, version and original split.
2. For large datasets (normally over 1–2 GB), inspect Kaggle only after the
   official source. A Kaggle copy is eligible only when its provenance, file
   inventory, directory structure and split can be checked against the official
   release.
3. An unverified mirror must be recorded as a mirror and cannot be described as
   the official original data in an experiment or manuscript.
4. Do not use a source with unknown origin, image re-encoding, changed labels or
   undocumented split changes as a primary paper dataset.

## Transport policy

| Situation | Required route |
| --- | --- |
| Dataset over 1–2 GB | Prefer Kaggle CLI when the content-equivalence audit passes; otherwise an official persistent downloader. |
| Dataset from tens of MB to 1 GB | Prefer the official URL and Windows BITS (`Start-BitsTransfer -Asynchronous`) on the remote CUDA host. |
| Official source sustained at >=1 MiB/s | Continue the trusted source without changing transport merely for theoretical speed. |
| 300 KiB/s to <1 MiB/s | Use a persistent route such as BITS, resumable curl or a verified range downloader. |
| Below 300 KiB/s for 1–2 minutes | Stop the active transfer and search Kaggle, Hugging Face or an author-provided mirror; verify equivalence before use. |
| Range-supported official source | Use bounded parallel ranges only when persistence and `Content-Range` checks are available; never rely on an SSH-child process surviving disconnection. |

## Windows remote-host rule

An SSH session is an orchestration channel, not a durable download supervisor.
For official medium-size downloads, create a named asynchronous BITS task and
observe it through `Get-BitsTransfer`. BITS may pause when the user truly logs
out, but it persists across ordinary SSH disconnections and resumes after network
recovery. Never leave a long foreground `curl` or Python child attached to SSH
and assume it survives.

## Completion gate

No data-dependent experiment begins until all applicable items are recorded:

- archive checksum when the provider publishes one; otherwise a locally computed
  SHA-256 and the exact source URL;
- archive integrity and successful extraction;
- expected files/images/records count;
- image-mask or feature-label pairing;
- official train/validation/test split, or a preregistered replacement split;
- expected class/defect/non-defect counts;
- license, citation and any non-commercial/share-alike obligations.

## Active KSDD2 record

KSDD2 is acquired from the official ViCoS URL through Windows BITS under the
display name `KSDD2-Official`, destination
`E:\\Codex\\liqiu-adgbc\\data\\KSDD2\\KolektorSDD2.official.zip`.
The official page specifies CC BY-NC-SA 4.0, 3,335 images, 356 defective and
2,979 non-defective examples, with an official train/test split. Completion
verification must establish the archived mask schema before the AD-GBC smoke
run is authorized.
