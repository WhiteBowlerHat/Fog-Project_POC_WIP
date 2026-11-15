"""Device details: Android / mobile layout, and Android file access.

* MOBILE: one-column layout for phones. On by default on Android; on a PC it can
  be tried with `python -m gui --mobile` (or FOG_MOBILE=1): the window then has
  the size of a Pixel 7 screen.
* Android file pickers return "content://" addresses, not file paths, while the
  engine (Pillow, open()) needs real files. Picked files are copied into the
  application cache (to_local_path); results are written to a folder of the
  phone's storage (default_output_folder).
"""
import os
import sys
import uuid

IS_ANDROID = hasattr(sys, "getandroidapilevel") or "ANDROID_ARGUMENT" in os.environ
MOBILE = IS_ANDROID or os.environ.get("FOG_MOBILE") == "1" or "--mobile" in sys.argv

# Pixel 7: 1080 x 2400 pixels at a 2.625 scale -> about 412 x 915 logical pixels
PHONE_SIZE = (412, 915)


def screen_width() -> int:
    """Usable width in logical pixels (the simulated phone width on a PC in mobile mode)."""
    if MOBILE and not IS_ANDROID:
        return PHONE_SIZE[0]
    from PySide6.QtGui import QGuiApplication
    screen = QGuiApplication.primaryScreen()
    return screen.availableGeometry().width() if screen else PHONE_SIZE[0]


def fit_width(width: int, margin: int = 32) -> int:
    """`width`, reduced if needed so that a dialog fits on a phone screen."""
    return min(width, screen_width() - margin) if MOBILE else width


def is_content_uri(path: str) -> bool:
    return bool(path) and path.startswith("content://")


def to_local_path(path: str) -> str:
    """A real file path for `path`: unchanged, or for an Android "content://"
    address, a copy in the application cache (keeping the file name)."""
    if not is_content_uri(path):
        return path
    from PySide6.QtCore import QFile, QFileInfo, QStandardPaths
    name = QFileInfo(path).fileName() or "file"
    folder = os.path.join(QStandardPaths.writableLocation(QStandardPaths.CacheLocation),
                          "picked", uuid.uuid4().hex)
    os.makedirs(folder, exist_ok=True)
    local = os.path.join(folder, name)
    if not QFile.copy(path, local):
        raise OSError(f"cannot read the selected file: {name}")
    return local


def default_output_folder(kind: str) -> str:
    """Folder where results are written on Android: Documents/Fog/<kind>, or the
    application's own storage if the shared Documents folder is not writable."""
    from PySide6.QtCore import QStandardPaths
    candidates = [QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation),
                  QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)]
    for base in candidates:
        if not base:
            continue
        folder = os.path.join(base, "Fog", kind)
        try:
            os.makedirs(folder, exist_ok=True)
            probe = os.path.join(folder, ".write_test")
            with open(probe, "w"):
                pass
            os.remove(probe)
            return folder
        except OSError:
            continue
    raise OSError("no writable folder found for the results")
