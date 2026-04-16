from __future__ import annotations

import time
from pathlib import Path

import requests

from logo_verification.models.schemas import LogoDetection


class ContentUnderstandingService:
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        analyzer_id: str,
        api_version: str = "2024-12-01-preview",
        timeout_seconds: int = 30,
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.analyzer_id = analyzer_id
        self.api_version = api_version
        self.timeout_seconds = timeout_seconds

    def detect_logos(self, image_path: Path) -> list[LogoDetection]:
        analyze_url = (
            f"{self.endpoint}/contentunderstanding/analyzers/{self.analyzer_id}:analyzeBinary"
            f"?api-version={self.api_version}"
        )

        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": "application/octet-stream",
        }

        response = requests.post(
            analyze_url,
            headers=headers,
            data=image_path.read_bytes(),
            timeout=self.timeout_seconds,
        )

        if response.status_code == 202:
            operation_location = response.headers.get("operation-location") or response.headers.get("Operation-Location")
            if not operation_location:
                response.raise_for_status()
            payload = self._poll_result(operation_location)
        else:
            response.raise_for_status()
            payload = response.json()

        return self._extract_logo_detections(payload)

    def _poll_result(self, operation_location: str) -> dict:
        max_attempts = 20
        for _ in range(max_attempts):
            poll_response = requests.get(
                operation_location,
                headers={"Ocp-Apim-Subscription-Key": self.api_key},
                timeout=self.timeout_seconds,
            )
            poll_response.raise_for_status()
            payload = poll_response.json()
            status = str(payload.get("status", "")).lower()

            if status in {"succeeded", "success", "completed"}:
                return payload
            if status in {"failed", "error", "cancelled"}:
                raise RuntimeError(f"Content Understanding analysis failed: {payload}")

            time.sleep(1)

        raise TimeoutError("Timed out while waiting for Content Understanding analysis result")

    @staticmethod
    def _extract_logo_detections(payload: dict) -> list[LogoDetection]:
        detections: list[LogoDetection] = []

        result = payload.get("result", payload)

        # This parser supports common analyzer outputs. Prefer exposing
        # detected_logos as an array in your analyzer schema.
        candidate_collections = [
            result.get("detected_logos"),
            result.get("logos"),
            result.get("fields", {}).get("detected_logos") if isinstance(result.get("fields"), dict) else None,
        ]

        for collection in candidate_collections:
            if not collection:
                continue
            if isinstance(collection, dict):
                collection = collection.get("value") or collection.get("items") or collection.get("valueArray")
            if not isinstance(collection, list):
                continue

            for item in collection:
                if isinstance(item, dict):
                    # Native CU schema often wraps values in valueObject/valueString/valueNumber.
                    if "valueObject" in item and isinstance(item["valueObject"], dict):
                        value_object = item["valueObject"]
                        name = _extract_string(value_object.get("name")) or _extract_string(value_object.get("tag")) or "unknown"
                        confidence = _extract_number(value_object.get("confidence")) or _extract_number(value_object.get("probability")) or 0.0
                        bbox = _extract_bounding_box(value_object)
                    else:
                        name = str(item.get("name") or item.get("tag") or item.get("logo") or "unknown")
                        confidence = float(item.get("confidence") or item.get("probability") or 0.0)
                        bbox = _extract_bounding_box(item)
                else:
                    name = str(item)
                    confidence = 1.0
                    bbox = None

                detections.append(
                    LogoDetection(
                        tag_name=name,
                        probability=max(0.0, min(1.0, confidence)),
                        bounding_box=bbox,
                    )
                )

            if detections:
                return detections

        return detections


def _extract_string(value: object) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        raw = value.get("valueString") or value.get("value")
        if isinstance(raw, str):
            return raw
    return None


def _extract_number(value: object) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, dict):
        raw = value.get("valueNumber") or value.get("value")
        if isinstance(raw, (int, float)):
            return float(raw)
    return None


def _extract_bounding_box(payload: dict) -> dict[str, float] | None:
    candidate = payload.get("boundingBox") or payload.get("bounding_box")
    if not candidate:
        return None

    if isinstance(candidate, dict):
        # Support direct numeric dict and CU wrapped values.
        left = _extract_number(candidate.get("left"))
        top = _extract_number(candidate.get("top"))
        width = _extract_number(candidate.get("width"))
        height = _extract_number(candidate.get("height"))

        if left is not None and top is not None and width is not None and height is not None:
            return {
                "left": left,
                "top": top,
                "width": width,
                "height": height,
            }

    return None
