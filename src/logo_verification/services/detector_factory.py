from __future__ import annotations

from logo_verification.config import Settings
from logo_verification.services.content_understanding_service import ContentUnderstandingService
from logo_verification.services.detector_protocol import LogoDetector
from logo_verification.services.hybrid_detector import HybridDetector
from logo_verification.services.reference_logo_matcher import ReferenceLogoMatcher


def build_detector(settings: Settings) -> LogoDetector:
    primary: LogoDetector = ContentUnderstandingService(
        endpoint=settings.content_understanding_endpoint,
        api_key=settings.content_understanding_api_key,
        analyzer_id=settings.content_understanding_analyzer_id,
        api_version=settings.content_understanding_api_version,
    )

    if not settings.enable_reference_logo_matcher:
        return primary

    fallback = ReferenceLogoMatcher(
        reference_dir=settings.reference_logos_dir,
        min_good_matches=settings.reference_match_min_good_matches,
        ratio_test_threshold=settings.reference_match_ratio_test_threshold,
        template_match_threshold=settings.reference_match_template_threshold,
        min_inliers=settings.reference_match_min_inliers,
        min_inlier_ratio=settings.reference_match_min_inlier_ratio,
    )
    return HybridDetector(primary=primary, fallback=fallback)
