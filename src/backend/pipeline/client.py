"""Entrypoints to trigger the pipeline locally or via Modal.

This module provides the interface between Django and the pipeline.
It handles provider configuration from settings and result persistence.
"""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.db import transaction

from pipeline.adapters import (
    MockLLMProvider,
    MockProductSearchProvider,
    MockTranscriptionProvider,
    MockVisionProvider,
    ProviderRegistry,
)
from pipeline.steps import PipelineProviders, PipelineResult, run_pipeline
from video.models import (
    Market,
    Product,
    ProductMarket,
    Video,
    VideoProduct,
    VideoProductSource,
    VideoStatus,
)


def _get_providers_from_settings(use_mock: bool = False) -> PipelineProviders:
    """Create providers from Django settings.

    Args:
        use_mock: If True, use mock providers regardless of settings

    Returns:
        PipelineProviders instance configured from settings
    """
    if use_mock:
        return PipelineProviders(
            transcription=MockTranscriptionProvider(),
            vision=MockVisionProvider(),
            llm=MockLLMProvider(),
            product_search=MockProductSearchProvider(),
        )

    provider_config = getattr(settings, "PIPELINE_PROVIDERS", {})

    # Transcription provider
    trans_name = provider_config.get("transcription", "mock")
    trans_kwargs = {}
    if trans_name in ("whisper", "gemini"):
        model = getattr(settings, "PIPELINE_TRANSCRIPTION_MODEL", None)
        if model:
            trans_kwargs["model"] = model
    transcription = ProviderRegistry.get_transcription(
        trans_name, **trans_kwargs
    )

    # Vision provider
    vision_name = provider_config.get("vision", "mock")
    vision_kwargs = {}
    if vision_name in ("openai", "gemini"):
        model = getattr(settings, "PIPELINE_VISION_MODEL", None)
        if model:
            vision_kwargs["model"] = model
    vision = ProviderRegistry.get_vision(vision_name, **vision_kwargs)

    # LLM provider
    llm_name = provider_config.get("llm", "mock")
    llm_kwargs = {}
    if llm_name in ("openai", "gemini"):
        model = getattr(settings, "PIPELINE_LLM_MODEL", None)
        if model:
            llm_kwargs["model"] = model
    llm = ProviderRegistry.get_llm(llm_name, **llm_kwargs)

    # Product search provider
    search_name = provider_config.get("product_search", "mock")
    search_kwargs = {}
    if search_name == "amazon":
        search_kwargs = {
            "access_key": getattr(settings, "AMAZON_ACCESS_KEY", ""),
            "secret_key": getattr(settings, "AMAZON_SECRET_KEY", ""),
            "partner_tag": getattr(settings, "AMAZON_PARTNER_TAG", ""),
        }
    product_search = ProviderRegistry.get_product_search(
        search_name, **search_kwargs
    )

    return PipelineProviders(
        transcription=transcription,
        vision=vision,
        llm=llm,
        product_search=product_search,
    )


def trigger_analysis(
    video_id: int, use_mock: bool = True
) -> dict[str, Any]:
    """Trigger video analysis pipeline.

    Args:
        video_id: ID of the Video to analyze
        use_mock: If True, use mock providers for testing

    Returns:
        Dict with status and found product count
    """
    video = Video.objects.select_related("user").get(pk=video_id)
    providers = _get_providers_from_settings(use_mock=use_mock)
    return _run_and_persist(video, providers)


def _run_and_persist(
    video: Video, providers: PipelineProviders
) -> dict[str, Any]:
    """Run pipeline and persist results to database."""
    with transaction.atomic():
        video.status = VideoStatus.PROCESSING
        video.save(update_fields=["status"])

    try:
        result = run_pipeline(video.youtube_url, providers)
        _persist_products(video, result)
        with transaction.atomic():
            video.status = VideoStatus.COMPLETED
            video.save(update_fields=["status"])
        return {"status": video.status, "found": len(result.found)}
    except Exception:  # pragma: no cover
        with transaction.atomic():
            video.status = VideoStatus.FAILED
            video.save(update_fields=["status"])
        raise


def _determine_source(sources: list[str]) -> str:
    """Determine VideoProductSource from pipeline sources list."""
    if not sources:
        return VideoProductSource.AUDIO
    # Priority: video > audio > subtitle
    if "video" in sources:
        return VideoProductSource.VIDEO
    if "audio" in sources:
        return VideoProductSource.AUDIO
    if "subtitle" in sources:
        return VideoProductSource.SUBTITLE
    return VideoProductSource.AUDIO


def _persist_products(video: Video, result: PipelineResult) -> None:
    """Persist pipeline results to database."""
    for index, item in enumerate(result.found):
        product = None
        if asin := item.get("asin"):
            product, _ = Product.objects.get_or_create(
                name=item.get("name", asin)
            )
            ProductMarket.objects.get_or_create(
                product=product, market=Market.AMAZON, market_product_id=asin
            )
        elif name := item.get("name"):
            product, _ = Product.objects.get_or_create(name=name)

        source = _determine_source(item.get("sources", []))
        VideoProduct.objects.create(
            video=video,
            product=product,
            name=item.get("name", ""),
            timestamp=item.get("timestamp", ""),
            source=source,
            is_reviewed=False,
            is_found=True,
            sort_order=index,
        )

    # Also persist lost items
    for index, item in enumerate(result.lost, start=len(result.found)):
        VideoProduct.objects.create(
            video=video,
            product=None,
            name=item.get("name", "Unknown"),
            timestamp=item.get("timestamp", ""),
            source=_determine_source(item.get("sources", [])),
            is_reviewed=False,
            is_found=False,
            sort_order=index,
        )
