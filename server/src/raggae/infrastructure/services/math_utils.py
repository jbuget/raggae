"""Shared math utilities for the RAG pipeline."""

from __future__ import annotations

from math import sqrt


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """Compute cosine similarity between two vectors.

    Returns 0.0 when inputs are empty, mismatched, or zero-norm.
    """
    if not left or not right or len(left) != len(right):
        return 0.0
    dot_product = sum(a * b for a, b in zip(left, right, strict=False))
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot_product / (left_norm * right_norm)

