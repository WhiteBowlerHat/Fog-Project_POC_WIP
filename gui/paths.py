"""Locations of the resource files, from the sources or from a PyInstaller build."""
import sys
from pathlib import Path

# PyInstaller unpacks the bundled files into sys._MEIPASS
ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
ASSETS = ROOT / "assets"


def asset(name: str) -> str:
    return str(ASSETS / name)


LOGO = asset("logo.png")
ICON = asset("icon.png")
