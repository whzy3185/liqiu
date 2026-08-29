"""Exhaustive falsification checks for fixed-tree tau-one statements."""

from __future__ import annotations

from fractions import Fraction
from itertools import product

from theory.purity_contamination.enumerate import ball_count, leaves, shapes, verify_balanced_max, verify_single_flip


def mixed_internal_count(tree, labels: tuple[int, ...]) -> int:
    if tree.is_leaf:
        return 0
    values = {labels[index] for index in leaves(tree)}
    return int(len(values) > 1) + mixed_internal_count(tree.left, labels) + mixed_internal_count(tree.right, labels)


def verify_frontier_identity(max_leaves: int = 7) -> list[dict[str, object]]:
    failures = []
    for n in range(1, max_leaves + 1):
        for tree_id, tree in enumerate(shapes(n)):
            for labels in product((0, 1), repeat=n):
                expected = mixed_internal_count(tree, labels) + 1
                actual = ball_count(tree, labels, Fraction(1))
                if actual != expected:
                    failures.append({"n": n, "tree_id": tree_id, "labels": labels, "expected": expected, "actual": actual})
    return failures


def verify_local_budget(max_support: int = 32) -> list[dict[str, object]]:
    failures = []
    for support in range(1, max_support + 1):
        for tau in (Fraction(1, 2), Fraction(2, 3), Fraction(3, 4), Fraction(4, 5), Fraction(1)):
            minimum = int((1 - tau) * support) + 1
            for flips in range(0, support // 2 + 1):
                splits = Fraction(support - flips, support) < tau
                if splits != (flips >= minimum):
                    failures.append({"support": support, "tau": str(tau), "flips": flips, "minimum": minimum})
    return failures


def run() -> dict[str, object]:
    return {
        "single_flip_failures": verify_single_flip(),
        "balanced_max_failures": verify_balanced_max(max_height=4),
        "frontier_identity_failures": verify_frontier_identity(),
        "local_budget_failures": verify_local_budget(),
        "coverage": {"ordered_full_binary_trees_through_leaves": 7, "complete_tree_through_leaves": 16, "all_binary_labellings_through_leaves": 7, "local_support_through": 32},
    }
