from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from logo_verification.models.schemas import LogoDetection


@dataclass(frozen=True)
class _ReferenceLogo:
    name: str
    keypoints: tuple[cv2.KeyPoint, ...]
    descriptors: np.ndarray


class ReferenceLogoMatcher:
    def __init__(
        self,
        reference_dir: Path,
        min_good_matches: int = 10,
        ratio_test_threshold: float = 0.8,
        template_match_threshold: float = 0.72,
        min_inliers: int = 8,
        min_inlier_ratio: float = 0.4,
    ) -> None:
        self.reference_dir = reference_dir
        self.min_good_matches = min_good_matches
        self.ratio_test_threshold = ratio_test_threshold
        self.template_match_threshold = template_match_threshold
        self.min_inliers = min_inliers
        self.min_inlier_ratio = min_inlier_ratio
        self._orb = cv2.ORB_create(nfeatures=2500)
        self._matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        self._references = self._load_references()

    def detect_logos(self, image_path: Path) -> list[LogoDetection]:
        target = _read_grayscale(image_path)
        if target is None:
            return []

        keypoints_target, descriptors_target = self._orb.detectAndCompute(target, None)
        if descriptors_target is None or len(keypoints_target) == 0:
            return []

        detections: list[LogoDetection] = []
        image_h, image_w = target.shape[:2]

        for ref in self._references:
            best_detection: LogoDetection | None = None

            knn = self._matcher.knnMatch(ref.descriptors, descriptors_target, k=2)
            good_matches = []
            for pair in knn:
                if len(pair) < 2:
                    continue
                m, n = pair
                if m.distance < self.ratio_test_threshold * n.distance:
                    good_matches.append(m)

            if len(good_matches) >= self.min_good_matches:
                # Geometric verification: reject accidental feature matches that
                # do not agree on a consistent transformation.
                src_points = np.array([ref.keypoints[m.queryIdx].pt for m in good_matches], dtype=np.float32).reshape(-1, 1, 2)
                dst_points = np.array([keypoints_target[m.trainIdx].pt for m in good_matches], dtype=np.float32).reshape(-1, 1, 2)
                _, mask = cv2.findHomography(src_points, dst_points, cv2.RANSAC, 5.0)

                if mask is not None:
                    inliers = int(mask.ravel().sum())
                    inlier_ratio = inliers / max(len(good_matches), 1)

                    if inliers >= self.min_inliers and inlier_ratio >= self.min_inlier_ratio:
                        inlier_points = np.array(
                            [keypoints_target[m.trainIdx].pt for idx, m in enumerate(good_matches) if mask[idx][0]],
                            dtype=np.float32,
                        )
                        if len(inlier_points) > 0:
                            x, y, w, h = cv2.boundingRect(inlier_points)
                            if w > 0 and h > 0:
                                confidence = min(
                                    0.99,
                                    0.6
                                    + 0.2 * (inliers / max(self.min_inliers, 1))
                                    + 0.2 * inlier_ratio,
                                )
                                bbox = {
                                    "left": float(x / image_w),
                                    "top": float(y / image_h),
                                    "width": float(w / image_w),
                                    "height": float(h / image_h),
                                }
                                best_detection = LogoDetection(
                                    tag_name=ref.name,
                                    probability=confidence,
                                    bounding_box=bbox,
                                )

            template_detection = self._template_match_detection(ref, target, image_w, image_h)
            if template_detection and (
                best_detection is None or template_detection.probability > best_detection.probability
            ):
                best_detection = template_detection

            if best_detection is not None:
                detections.append(best_detection)

        return detections

    def _template_match_detection(
        self,
        ref: _ReferenceLogo,
        target: np.ndarray,
        image_w: int,
        image_h: int,
    ) -> LogoDetection | None:
        reference_path = self.reference_dir / f"{ref.name}.png"
        # Fallback: probe all supported extensions when original extension is unknown.
        if not reference_path.exists():
            for ext in (".png", ".jpg", ".jpeg", ".webp", ".bmp"):
                candidate = self.reference_dir / f"{ref.name}{ext}"
                if candidate.exists():
                    reference_path = candidate
                    break

        template = _read_grayscale(reference_path)
        if template is None:
            return None

        t_h, t_w = template.shape[:2]
        if t_h < 10 or t_w < 10:
            return None

        best_score = -1.0
        best_rect: tuple[int, int, int, int] | None = None
        for scale in (0.5, 0.75, 1.0, 1.25, 1.5):
            resized = cv2.resize(template, (int(t_w * scale), int(t_h * scale)), interpolation=cv2.INTER_AREA)
            r_h, r_w = resized.shape[:2]
            if r_h <= 0 or r_w <= 0 or r_h >= target.shape[0] or r_w >= target.shape[1]:
                continue

            result = cv2.matchTemplate(target, resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            if max_val > best_score:
                best_score = float(max_val)
                best_rect = (max_loc[0], max_loc[1], r_w, r_h)

        if best_rect is None or best_score < self.template_match_threshold:
            return None

        x, y, w, h = best_rect
        bbox = {
            "left": float(x / image_w),
            "top": float(y / image_h),
            "width": float(w / image_w),
            "height": float(h / image_h),
        }

        return LogoDetection(
            tag_name=ref.name,
            probability=min(0.99, max(0.0, best_score)),
            bounding_box=bbox,
        )

    def _load_references(self) -> list[_ReferenceLogo]:
        refs: list[_ReferenceLogo] = []
        if not self.reference_dir.exists():
            return refs

        for path in sorted(self.reference_dir.iterdir()):
            if not path.is_file() or path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
                continue

            image = _read_grayscale(path)
            if image is None:
                continue

            keypoints, descriptors = self._orb.detectAndCompute(image, None)
            if descriptors is None or len(keypoints) == 0:
                continue

            refs.append(
                _ReferenceLogo(
                    name=path.stem,
                    keypoints=tuple(keypoints),
                    descriptors=descriptors,
                )
            )

        return refs


def _read_grayscale(path: Path) -> np.ndarray | None:
    raw = np.fromfile(str(path), dtype=np.uint8)
    if raw.size == 0:
        return None
    return cv2.imdecode(raw, cv2.IMREAD_GRAYSCALE)
