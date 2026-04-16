from __future__ import annotations

import json
from pathlib import Path

from logo_verification.models.schemas import VerificationResult
from logo_verification.services.detector_protocol import LogoDetector


class VerificationPipeline:
    def __init__(
        self,
        prediction_service: LogoDetector,
        detection_threshold: float,
        min_matches_required: int,
    ) -> None:
        self.prediction_service = prediction_service
        self.detection_threshold = detection_threshold
        self.min_matches_required = min_matches_required

    def run(
        self,
        images_dir: Path,
        reference_logos_dir: Path,
    ) -> list[VerificationResult]:
        reference_logo_names = self._load_reference_logo_names(reference_logos_dir)
        image_files = sorted(
            [p for p in images_dir.iterdir() if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}]
        )

        results: list[VerificationResult] = []

        for image_path in image_files:
            expected_logos = reference_logo_names
            detections = self.prediction_service.detect_logos(image_path)
            valid_detections = [d for d in detections if d.probability >= self.detection_threshold]

            detected_tag_set = {d.tag_name for d in valid_detections}
            matched = sorted([logo for logo in expected_logos if logo in detected_tag_set])
            missing = sorted([logo for logo in expected_logos if logo not in detected_tag_set])

            is_verified = len(matched) >= max(self.min_matches_required, min(1, len(expected_logos))) and not missing

            results.append(
                VerificationResult(
                    file_name=image_path.name,
                    expected_logos=expected_logos,
                    detected_logos=valid_detections,
                    matched_logos=matched,
                    missing_logos=missing,
                    is_verified=is_verified,
                )
            )

        return results

    @staticmethod
    def save_json_report(results: list[VerificationResult], output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        json_payload = [result.model_dump() for result in results]
        output_path.write_text(json.dumps(json_payload, indent=2), encoding="utf-8")

    @staticmethod
    def _load_reference_logo_names(reference_dir: Path) -> list[str]:
        if not reference_dir.exists():
            return []

        names = []
        for item in sorted(reference_dir.iterdir()):
            if item.is_file() and item.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
                names.append(item.stem)
        return names
