from __future__ import annotations

from pathlib import Path

from logo_verification.models.schemas import LogoDetection
from logo_verification.services.detector_protocol import LogoDetector


class HybridDetector:
    def __init__(self, primary: LogoDetector, fallback: LogoDetector) -> None:
        self.primary = primary
        self.fallback = fallback

    def detect_logos(self, image_path: Path) -> list[LogoDetection]:
        primary_detections = self.primary.detect_logos(image_path)
        fallback_detections = self.fallback.detect_logos(image_path)

        merged: dict[str, LogoDetection] = {}
        for detection in primary_detections + fallback_detections:
            existing = merged.get(detection.tag_name)
            if existing is None or detection.probability > existing.probability:
                merged[detection.tag_name] = detection

        return list(merged.values())
