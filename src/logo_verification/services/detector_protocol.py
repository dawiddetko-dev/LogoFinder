from __future__ import annotations

from pathlib import Path
from typing import Protocol

from logo_verification.models.schemas import LogoDetection


class LogoDetector(Protocol):
    def detect_logos(self, image_path: Path) -> list[LogoDetection]:
        ...
