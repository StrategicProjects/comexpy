"""Lightweight console messages, mirroring the R package's cli alerts.

Messages go to stderr and can be silenced with :func:`set_verbose`.
"""
from __future__ import annotations

import sys

_VERBOSE = True


def set_verbose(verbose: bool) -> None:
    """Enable or disable informational messages (success/step/info).

    Warnings are always shown. Errors are raised as exceptions.

    Parameters
    ----------
    verbose : bool
        If ``False``, suppress progress and success messages.
    """
    global _VERBOSE
    _VERBOSE = bool(verbose)


def is_verbose() -> bool:
    return _VERBOSE


def info(message: str) -> None:
    if _VERBOSE:
        print(f"ℹ {message}", file=sys.stderr)


def step(message: str) -> None:
    if _VERBOSE:
        print(f"→ {message}", file=sys.stderr)


def success(message: str) -> None:
    if _VERBOSE:
        print(f"✔ {message}", file=sys.stderr)


def warn(message: str) -> None:
    # Warnings are always shown, regardless of verbosity.
    print(f"! {message}", file=sys.stderr)
