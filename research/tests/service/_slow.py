"""Module-level helpers for execution tests (spawned workers import them by name)."""
import time


def sleep_forever() -> None:
    while True:
        time.sleep(0.05)


def busy_forever() -> None:
    x = 0
    while True:  # pure-Python loop: cannot be interrupted from inside
        x += 1


def add(a: int, b: int) -> int:
    return a + b


def boom() -> None:
    raise ValueError("planted failure")


def ignore_sigterm_forever() -> None:
    import signal
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    while True:
        time.sleep(0.05)
