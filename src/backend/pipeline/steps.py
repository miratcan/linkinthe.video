"""Pipeline steps and orchestration.

Each step uses injected providers for external services.
This allows easy testing and swapping of implementations.
"""

from __future__ import annotations

import tempfile
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from django.conf import settings

from pipeline.adapters import (
    LLMProvider,
    ProductSearchProvider,
    TranscriptionProvider,
    VisionProvider,
)


@dataclass
class PipelineResult:
    """Result from video analysis pipeline."""

    found: list[dict[str, Any]]
    lost: list[dict[str, Any]]


@dataclass
class PipelineProviders:
    """Container for all providers needed by the pipeline."""

    transcription: TranscriptionProvider
    vision: VisionProvider
    llm: LLMProvider
    product_search: ProductSearchProvider


@dataclass
class PipelineContext:
    """Context passed through pipeline steps."""

    youtube_url: str
    providers: PipelineProviders
    video_path: str = ""
    audio_path: str = ""
    transcript: str = ""
    frames: list[str] = field(default_factory=list)
    candidates: list[dict[str, Any]] = field(default_factory=list)
    enriched: list[dict[str, Any]] = field(default_factory=list)


# =============================================================================
# Pipeline Steps
# =============================================================================


def download_video(ctx: PipelineContext) -> PipelineContext:
    """Download video from YouTube URL."""
    if not getattr(settings, "PIPELINE_USE_REAL_DOWNLOAD", False):
        ctx.video_path = (
            f"/tmp/downloads/{ctx.youtube_url.rsplit('/', 1)[-1]}.mp4"
        )
        return ctx

    try:
        from yt_dlp import YoutubeDL  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "yt-dlp is required for real downloads; install it or unset "
            "PIPELINE_USE_REAL_DOWNLOAD."
        ) from exc

    output_dir = Path(tempfile.gettempdir()) / "linkinthe-video" / "downloads"
    output_dir.mkdir(parents=True, exist_ok=True)
    target_template = output_dir / f"{uuid.uuid4().hex}.%(ext)s"

    ydl_opts = {
        "outtmpl": str(target_template),
        "format": "mp4",
        "quiet": True,
        "no_warnings": True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(ctx.youtube_url, download=True)
        ctx.video_path = str(Path(ydl.prepare_filename(info)))

    return ctx


def extract_audio(ctx: PipelineContext) -> PipelineContext:
    """Extract audio track from video file."""
    if not getattr(settings, "PIPELINE_USE_REAL_AUDIO", False):
        ctx.audio_path = str(Path(ctx.video_path).with_suffix(".wav"))
        return ctx

    try:
        import ffmpeg  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "ffmpeg-python is required for real audio extraction; install it "
            "or disable PIPELINE_USE_REAL_AUDIO."
        ) from exc

    output_dir = Path(tempfile.gettempdir()) / "linkinthe-video" / "audio"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{uuid.uuid4().hex}.wav"

    stream = ffmpeg.input(ctx.video_path)
    stream = ffmpeg.output(
        stream,
        str(output_path),
        acodec="pcm_s16le",
        ar=44100,
        ac=2,
    )
    try:
        ffmpeg.run(
            stream,
            overwrite_output=True,
            capture_stdout=True,
            capture_stderr=True,
        )
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "ffmpeg binary is required for audio extraction; ensure it is "
            "installed or disable PIPELINE_USE_REAL_AUDIO."
        ) from exc

    ctx.audio_path = str(output_path)
    return ctx


def transcribe_audio(ctx: PipelineContext) -> PipelineContext:
    """Transcribe audio to text using configured provider."""
    result = ctx.providers.transcription.transcribe(ctx.audio_path)
    ctx.transcript = result.text
    return ctx


def extract_frames(ctx: PipelineContext) -> PipelineContext:
    """Extract key frames from video for visual analysis.

    Currently stubbed - will extract frames at product mention timestamps.
    """
    # TODO: Implement frame extraction at timestamps
    # For now, return empty frames list
    ctx.frames = []
    return ctx


def detect_products_from_audio(ctx: PipelineContext) -> PipelineContext:
    """Extract product mentions from transcript using LLM."""
    products = ctx.providers.llm.extract_products(ctx.transcript)

    # Mark all as found from audio
    for product in products:
        product.setdefault("sources", [])
        if "audio" not in product["sources"]:
            product["sources"].append("audio")

    ctx.candidates = products
    return ctx


def detect_products_from_video(ctx: PipelineContext) -> PipelineContext:
    """Detect products from video frames using vision provider.

    Analyzes frames for products that couldn't be identified from audio.
    """
    if not ctx.frames:
        return ctx

    # Find candidates without clear identification
    unclear = [
        c for c in ctx.candidates
        if not c.get("asin") and c.get("confidence", 1.0) < 0.8
    ]

    for candidate in unclear:
        # TODO: Use timestamp to select correct frame
        # timestamp = candidate.get("timestamp", "")
        if ctx.frames:
            frame_path = ctx.frames[0]
            prompt = (
                f"Identify the product '{candidate.get('name')}' "
                "in this frame. What is the exact product name and brand?"
            )
            result = ctx.providers.vision.analyze_image(frame_path, prompt)

            if result.products:
                # Update candidate with vision results
                best = result.products[0]
                candidate["name"] = best.get("name", candidate.get("name"))
                candidate["confidence"] = best.get("confidence", 0.5)
                if "video" not in candidate.get("sources", []):
                    candidate.setdefault("sources", []).append("video")

    return ctx


def enrich_with_search(ctx: PipelineContext) -> PipelineContext:
    """Enrich products with search results (images, ASINs, etc.)."""
    enriched = []

    for candidate in ctx.candidates:
        if asin := candidate.get("asin"):
            # Already has ASIN - get details
            result = ctx.providers.product_search.get_by_asin(asin)
            if result:
                candidate["image_url"] = result.image_url
                candidate["product_url"] = result.url
        else:
            # Search by name
            name = candidate.get("name", "")
            if name:
                results = ctx.providers.product_search.search(name)
                if results:
                    best = results[0]
                    candidate["asin"] = best.asin
                    candidate["image_url"] = best.image_url
                    candidate["product_url"] = best.url

        enriched.append(candidate)

    ctx.enriched = enriched
    return ctx


def build_result(ctx: PipelineContext) -> PipelineResult:
    """Build final pipeline result from context."""
    found = []
    lost = []

    for item in ctx.enriched:
        result_item = {
            "name": item.get("name", "Unknown"),
            "timestamp": item.get("timestamp", ""),
            "asin": item.get("asin"),
            "sources": item.get("sources", []),
            "image_url": item.get("image_url"),
        }

        # If we have ASIN or high confidence, it's found
        if item.get("asin") or item.get("confidence", 0) >= 0.7:
            found.append(result_item)
        else:
            lost.append(result_item)

    return PipelineResult(found=found, lost=lost)


# =============================================================================
# Pipeline Runner
# =============================================================================


def run_pipeline(
    youtube_url: str,
    providers: PipelineProviders,
) -> PipelineResult:
    """Run the full video analysis pipeline.

    Args:
        youtube_url: URL of the YouTube video to analyze
        providers: Container with all required providers

    Returns:
        PipelineResult with found and lost products
    """
    ctx = PipelineContext(youtube_url=youtube_url, providers=providers)

    # Run pipeline steps
    ctx = download_video(ctx)
    ctx = extract_audio(ctx)
    ctx = transcribe_audio(ctx)
    ctx = extract_frames(ctx)
    ctx = detect_products_from_audio(ctx)
    ctx = detect_products_from_video(ctx)
    ctx = enrich_with_search(ctx)

    return build_result(ctx)


# =============================================================================
# Legacy API (for backward compatibility)
# =============================================================================


def run_analysis(youtube_url: str, llm: LLMProvider) -> PipelineResult:
    """Legacy function for backward compatibility.

    DEPRECATED: Use run_pipeline() with PipelineProviders instead.
    """
    from pipeline.adapters import (
        MockProductSearchProvider,
        MockTranscriptionProvider,
        MockVisionProvider,
    )

    providers = PipelineProviders(
        transcription=MockTranscriptionProvider(),
        vision=MockVisionProvider(),
        llm=llm,
        product_search=MockProductSearchProvider(),
    )

    return run_pipeline(youtube_url, providers)
