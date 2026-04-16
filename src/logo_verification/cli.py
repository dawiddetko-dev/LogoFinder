from __future__ import annotations

from logo_verification.config import load_settings
from logo_verification.services.detector_factory import build_detector
from logo_verification.services.verification_pipeline import VerificationPipeline


def main() -> None:
    settings = load_settings()

    prediction_service = build_detector(settings)

    pipeline = VerificationPipeline(
        prediction_service=prediction_service,
        detection_threshold=settings.detection_threshold,
        min_matches_required=settings.min_matches_required,
    )

    results = pipeline.run(settings.product_images_dir, settings.reference_logos_dir)
    pipeline.save_json_report(results, settings.output_report_path)

    verified_count = sum(1 for item in results if item.is_verified)
    print(f"Processed: {len(results)} images")
    print(f"Verified: {verified_count}")
    print(f"Report: {settings.output_report_path}")


if __name__ == "__main__":
    main()
