"""User preferences kept between launches (QSettings): image conversion formats."""
from PySide6.QtCore import QSettings

from fog import CONVERTIBLE_FORMATS

_settings = QSettings("FogProject", "Fog")

FORMAT_LABELS = {"jpg": "JPG / JPEG", "tiff": "TIFF", "bmp": "BMP", "webp": "WEBP"}


def conversion_formats() -> list:
    """Formats converted to PNG when "non-native images" is on (all of them by default)."""
    return [f for f in CONVERTIBLE_FORMATS
            if _settings.value(f"conversion/{f}", True, type=bool)]


def set_conversion_format(fmt: str, enabled: bool):
    _settings.setValue(f"conversion/{fmt}", bool(enabled))
