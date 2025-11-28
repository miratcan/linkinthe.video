"""Modal app scaffold for video analysis."""

from __future__ import annotations

try:
    import modal  # type: ignore
except ImportError:  # pragma: no cover - modal is optional in CI/tests
    modal = None

from pipeline.client import trigger_analysis

if modal:
    image = (
        modal.Image.debian_slim()
        .apt_install("ffmpeg")
        .pip_install("yt-dlp", "litellm", "PyJWT", "cryptography")
    )

    app = modal.App("linkinthe-video")

    @app.function(
        image=image,
        secrets=[modal.Secret.from_name("linkinthe-video")],
    )  # type: ignore[attr-defined]
    def run_pipeline(video_id: int):
        return trigger_analysis(video_id, use_mock=False)
else:

    def run_pipeline(video_id: int):  # pragma: no cover - fallback
        raise RuntimeError(
            "Modal is not installed; cannot run remote pipeline."
        )
