from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st
from PIL import Image

from logo_verification.config import load_settings
from logo_verification.services.detector_factory import build_detector
from logo_verification.services.verification_pipeline import VerificationPipeline


def _list_reference_images(reference_dir: Path) -> list[Path]:
    if not reference_dir.exists():
        return []

    return sorted(
        [
            p
            for p in reference_dir.iterdir()
            if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
        ]
    )


def _normalize_logo_name(value: str) -> str:
    return value.strip().lower().replace(" ", "_")

st.set_page_config(page_title="Logo Verification POC", layout="wide")
st.title("Logo / Trademark Verification")
st.caption("Azure AI Content Understanding with optional local reference matcher fallback")

settings = load_settings()
detector = build_detector(settings)
pipeline = VerificationPipeline(
    prediction_service=detector,
    detection_threshold=settings.detection_threshold,
    min_matches_required=settings.min_matches_required,
)

st.subheader("Single Image Test")
uploaded = st.file_uploader("Upload a product image", type=["png", "jpg", "jpeg", "webp"])

if uploaded is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded.name).suffix) as tmp:
        tmp.write(uploaded.getvalue())
        tmp_path = Path(tmp.name)

    detections = detector.detect_logos(tmp_path)
    detections = [d for d in detections if d.probability >= settings.detection_threshold]
    reference_paths = _list_reference_images(settings.reference_logos_dir)
    expected_logos = [path.stem for path in reference_paths]
    detected_map = { _normalize_logo_name(d.tag_name): d.tag_name for d in detections }

    matched_logos = [name for name in expected_logos if _normalize_logo_name(name) in detected_map]
    missing_logos = [name for name in expected_logos if _normalize_logo_name(name) not in detected_map]

    preview_image = Image.open(tmp_path).convert("RGB")
    st.image(preview_image, caption=f"Preview: {uploaded.name}")

    st.markdown("### Detection Summary")
    st.write(f"Detected logos: {', '.join(matched_logos) if matched_logos else 'None'}")
    st.write(f"Not detected: {', '.join(missing_logos) if missing_logos else 'None'}")

    if detections:
        st.success(f"Detected {len(detections)} logos above threshold")
        st.table(
            [
                {
                    "logo": d.tag_name,
                    "probability": round(d.probability, 4),
                }
                for d in detections
            ]
        )
    else:
        st.warning("No logos detected above threshold")

    st.markdown("### Reference Logos")
    if reference_paths:
        columns = st.columns(min(4, len(reference_paths)))
        for idx, ref_path in enumerate(reference_paths):
            ref_name = ref_path.stem
            status = "Detected" if ref_name in matched_logos else "Not detected"
            with columns[idx % len(columns)]:
                st.image(Image.open(ref_path).convert("RGB"), caption=f"{ref_name} | {status}")
    else:
        st.info("No reference logos found in data/logos_reference")

st.subheader("Batch Verification")
if st.button("Run verification for folder"):
    results = pipeline.run(settings.product_images_dir, settings.reference_logos_dir)
    pipeline.save_json_report(results, settings.output_report_path)

    st.write(f"Processed: {len(results)}")
    st.write(f"Verified: {sum(1 for item in results if item.is_verified)}")
    st.write(f"Report saved to: {settings.output_report_path}")

    st.dataframe(
        [
            {
                "file_name": item.file_name,
                "verified": item.is_verified,
                "matched": ", ".join(item.matched_logos),
                "missing": ", ".join(item.missing_logos),
            }
            for item in results
        ]
    )
