import logging
import sys

from src.schemas.enums import LogLevel


def setup_logging(level: LogLevel = LogLevel.INFO) -> None:
    log_level = getattr(logging, level.value)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger("medassist")
    root.setLevel(log_level)
    root.addHandler(handler)
    root.propagate = False


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"medassist.{name}")
