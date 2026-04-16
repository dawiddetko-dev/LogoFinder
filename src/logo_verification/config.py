from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    content_understanding_endpoint: str
    content_understanding_api_key: str
    content_understanding_analyzer_id: str
    content_understanding_api_version: str
    enable_reference_logo_matcher: bool
    reference_match_min_good_matches: int
    reference_match_ratio_test_threshold: float
    reference_match_template_threshold: float
    reference_match_min_inliers: int
    reference_match_min_inlier_ratio: float
    detection_threshold: float
    min_matches_required: int
    reference_logos_dir: Path
    product_images_dir: Path
    output_report_path: Path


def load_settings() -> Settings:
    load_dotenv()

    content_understanding_endpoint = os.getenv("CONTENT_UNDERSTANDING_ENDPOINT", "")
    content_understanding_api_key = os.getenv("CONTENT_UNDERSTANDING_API_KEY", "")
    content_understanding_analyzer_id = os.getenv("CONTENT_UNDERSTANDING_ANALYZER_ID", "")

    _validate_required(
        {
            "CONTENT_UNDERSTANDING_ENDPOINT": content_understanding_endpoint,
            "CONTENT_UNDERSTANDING_API_KEY": content_understanding_api_key,
            "CONTENT_UNDERSTANDING_ANALYZER_ID": content_understanding_analyzer_id,
        }
    )

    return Settings(
        content_understanding_endpoint=content_understanding_endpoint,
        content_understanding_api_key=content_understanding_api_key,
        content_understanding_analyzer_id=content_understanding_analyzer_id,
        content_understanding_api_version=os.getenv("CONTENT_UNDERSTANDING_API_VERSION", "2024-12-01-preview"),
        enable_reference_logo_matcher=os.getenv("ENABLE_REFERENCE_LOGO_MATCHER", "true").strip().lower() == "true",
        reference_match_min_good_matches=int(os.getenv("REFERENCE_MATCH_MIN_GOOD_MATCHES", "10")),
        reference_match_ratio_test_threshold=float(os.getenv("REFERENCE_MATCH_RATIO_TEST_THRESHOLD", "0.8")),
        reference_match_template_threshold=float(os.getenv("REFERENCE_MATCH_TEMPLATE_THRESHOLD", "0.72")),
        reference_match_min_inliers=int(os.getenv("REFERENCE_MATCH_MIN_INLIERS", "8")),
        reference_match_min_inlier_ratio=float(os.getenv("REFERENCE_MATCH_MIN_INLIER_RATIO", "0.4")),
        detection_threshold=float(os.getenv("DETECTION_THRESHOLD", "0.65")),
        min_matches_required=int(os.getenv("MIN_MATCHES_REQUIRED", "1")),
        reference_logos_dir=Path(os.getenv("REFERENCE_LOGOS_DIR", "data/logos_reference")),
        product_images_dir=Path(os.getenv("PRODUCT_IMAGES_DIR", "data/products_to_verify")),
        output_report_path=Path(os.getenv("OUTPUT_REPORT_PATH", "outputs/verification_report.json")),
    )


def _validate_required(values: dict[str, str]) -> None:
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
