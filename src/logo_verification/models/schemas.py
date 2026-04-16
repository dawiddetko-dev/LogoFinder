from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class LogoDetection(BaseModel):
    tag_name: str
    probability: float = Field(ge=0.0, le=1.0)
    bounding_box: Optional[dict[str, float]] = None


class VerificationResult(BaseModel):
    file_name: str
    expected_logos: list[str]
    detected_logos: list[LogoDetection]
    matched_logos: list[str]
    missing_logos: list[str]
    is_verified: bool
