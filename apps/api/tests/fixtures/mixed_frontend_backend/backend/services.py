"""Shared service helpers for the Python API."""


def compute_score(value: int) -> int:
    return value * 2


def format_label(name: str) -> str:
    return name.strip().title()
