"""Resource paths for development and PyInstaller builds."""

from __future__ import annotations

import sys
from pathlib import Path


def app_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def asset_path(*parts: str) -> Path:
    return app_root().joinpath("assets", *parts)
