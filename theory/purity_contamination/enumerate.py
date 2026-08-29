"""Exact small-tree enumerator for label-dependent purity frontiers.

This is a counterexample finder, not a substitute for a proof.  Trees are full
ordered binary trees; leaf positions are their left-to-right sample identities.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product


@dataclass(frozen=True)
class Tree:
    left: "Tree | None" = None
    right: "Tree | None" = None
    leaf: int | None = None

    @property
    def is_leaf(self) -> bool:
        return self.leaf is not None


def relabel(tree: Tree, start: int = 0) -> tuple[Tree, int]:
    if tree.is_leaf:
        return Tree(leaf=start), start + 1
    left, next_id = relabel(tree.left, start)  # type: ignore[arg-type]
    right, next_id = relabel(tree.right, next_id)  # type: ignore[arg-type]
    return Tree(left, right), next_id


@lru_cache(maxsize=None)
def shapes(n_leaves: int) -> tuple[Tree, ...]:
    if n_leaves == 1:
        return (Tree(leaf=0),)
    result = []
    for left_size in range(1, n_leaves):
        for left in shapes(left_size):
            for right in shapes(n_leaves - left_size):
                tree, _ = relabel(Tree(left, right))
                result.append(tree)
    return tuple(result)


def complete_tree(height: int) -> Tree:
    if height == 0:
        return Tree(leaf=0)
    tree, _ = relabel(Tree(complete_tree(height - 1), complete_tree(height - 1)))
    return tree


def leaves(tree: Tree) -> tuple[int, ...]:
    if tree.is_leaf:
        return (int(tree.leaf),)
    return leaves(tree.left) + leaves(tree.right)  # type: ignore[arg-type]


def depth_of(tree: Tree, target: int, depth: int = 0) -> int | None:
    if tree.is_leaf:
        return depth if tree.leaf == target else None
    return depth_of(tree.left, target, depth + 1) or depth_of(tree.right, target, depth + 1)  # type: ignore[arg-type]


def purity(tree: Tree, labels: tuple[int, ...]) -> Fraction:
    values = [labels[index] for index in leaves(tree)]
    return Fraction(max(values.count(label) for label in set(values)), len(values))


def frontier(tree: Tree, labels: tuple[int, ...], tau: Fraction) -> tuple[Tree, ...]:
    if tree.is_leaf or purity(tree, labels) >= tau:
        return (tree,)
    return frontier(tree.left, labels, tau) + frontier(tree.right, labels, tau)  # type: ignore[arg-type]


def ball_count(tree: Tree, labels: tuple[int, ...], tau: Fraction) -> int:
    return len(frontier(tree, labels, tau))


def exact_balanced_upper(n: int, m: int) -> int:
    """Candidate maximum activated internal nodes for n=2^h, tau=1, m<=n/2."""
    height = n.bit_length() - 1
    return sum(min(2 ** depth, m) for depth in range(height))


def verify_single_flip(max_leaves: int = 7) -> list[dict[str, object]]:
    failures = []
    for n in range(2, max_leaves + 1):
        labels = (0,) * n
        for tree_id, tree in enumerate(shapes(n)):
            for leaf in leaves(tree):
                flipped = list(labels)
                flipped[leaf] = 1
                expected = depth_of(tree, leaf)
                actual = ball_count(tree, tuple(flipped), Fraction(1))
                if actual != expected + 1:
                    failures.append({"n": n, "tree_id": tree_id, "leaf": leaf, "expected_terminal_balls": expected + 1, "actual_terminal_balls": actual})
    return failures


def verify_balanced_max(max_height: int = 5) -> list[dict[str, object]]:
    failures = []
    for height in range(1, max_height + 1):
        tree = complete_tree(height)
        n = 2 ** height
        base = (0,) * n
        for m in range(1, n // 2 + 1):
            observed = -1
            witnesses = []
            for marked in combinations(range(n), m):
                labels = list(base)
                for index in marked:
                    labels[index] = 1
                value = ball_count(tree, tuple(labels), Fraction(1)) - 1
                if value > observed:
                    observed, witnesses = value, [marked]
                elif value == observed:
                    witnesses.append(marked)
            expected = exact_balanced_upper(n, m)
            if observed != expected:
                failures.append({"height": height, "n": n, "m": m, "expected_amplification": expected, "observed_amplification": observed, "witness": witnesses[0] if witnesses else None})
    return failures


def tau_examples(max_leaves: int = 6) -> list[dict[str, object]]:
    """Record small non-unit threshold cascades, including multi-target flips."""
    rows = []
    thresholds = (Fraction(1, 2), Fraction(2, 3), Fraction(3, 4), Fraction(1))
    for n in range(2, max_leaves + 1):
        tree = shapes(n)[0]
        for tau in thresholds:
            for labels in product((0, 1), repeat=n):
                if labels == (0,) * n:
                    continue
                rows.append({"n": n, "tau": str(tau), "labels": "".join(map(str, labels)), "terminal_balls": ball_count(tree, labels, tau)})
    return rows


def run(max_general_leaves: int = 7, max_balanced_height: int = 4) -> dict[str, object]:
    single_failures = verify_single_flip(max_general_leaves)
    balanced_failures = verify_balanced_max(max_balanced_height)
    return {
        "max_general_leaves": max_general_leaves,
        "max_balanced_height": max_balanced_height,
        "single_flip_exact_formula_failures": single_failures,
        "balanced_max_candidate_failures": balanced_failures,
        "tau_example_count": len(tau_examples()),
    }
