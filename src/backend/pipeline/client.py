"""Entrypoints to trigger the pipeline locally or via Modal."""

from __future__ import annotations

from typing import Any, Dict

from django.db import transaction

from pipeline.adapters import MockProvider, OpenAIProvider
from pipeline.steps import PipelineResult, run_analysis
from video.models import (
    Market,
    Product,
    ProductMarket,
    Video,
    VideoProduct,
    VideoProductSource,
    VideoStatus,
)


def trigger_analysis(video_id: int, use_mock: bool = True) -> Dict[str, Any]:
    """Trigger analysis. If Modal is available, it could be plugged here; otherwise run sync."""
    video = Video.objects.select_related("user").get(pk=video_id)
    provider = MockProvider() if use_mock else OpenAIProvider()
    return _run_and_persist(video, provider)


def _run_and_persist(video: Video, provider) -> Dict[str, Any]:
    with transaction.atomic():
        video.status = VideoStatus.PROCESSING
        video.save(update_fields=["status"])

    try:
        result = run_analysis(video.youtube_url, provider)
        _persist_products(video, result)
        with transaction.atomic():
            video.status = VideoStatus.COMPLETED
            video.save(update_fields=["status"])
        return {"status": video.status, "found": len(result.found)}
    except Exception:  # pragma: no cover - defensive for production
        with transaction.atomic():
            video.status = VideoStatus.FAILED
            video.save(update_fields=["status"])
        raise


def _persist_products(video: Video, result: PipelineResult) -> None:
    for index, item in enumerate(result.found):
        product = None
        if asin := item.get("asin"):
            product, _ = Product.objects.get_or_create(name=item.get("name", asin))
            ProductMarket.objects.get_or_create(
                product=product, market=Market.AMAZON, market_product_id=asin
            )
        elif name := item.get("name"):
            product, _ = Product.objects.get_or_create(name=name)

        VideoProduct.objects.create(
            video=video,
            product=product,
            name=item.get("name", ""),
            timestamp=item.get("timestamp", ""),
            source=VideoProductSource.MANUAL,
            is_reviewed=False,
            is_found=True,
            sort_order=index,
        )
