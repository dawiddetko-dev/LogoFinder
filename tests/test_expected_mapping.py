from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from logo_verification.services.verification_pipeline import VerificationPipeline


def test_load_reference_logo_names(tmp_path: Path) -> None:
    (tmp_path / "logo_b.png").write_bytes(b"x")
    (tmp_path / "logo_a.jpg").write_bytes(b"x")
    (tmp_path / "notes.txt").write_text("ignore", encoding="utf-8")

    names = VerificationPipeline._load_reference_logo_names(tmp_path)

    assert names == ["logo_a", "logo_b"]
