"""Lightweight JSON API endpoints for video-related models."""

from __future__ import annotations

import json
from typing import Any

from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Market, Product, ProductMarket, Video, VideoProduct


def _parse_json(request: HttpRequest) -> dict[str, Any]:
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode())
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON body")


def _json_error(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"error": message}, status=status)


def _serialize_video(video: Video) -> dict[str, Any]:
    return {
        "id": video.id,
        "user_id": video.user_id,
        "youtube_url": video.youtube_url,
        "status": video.status,
        "slug": video.slug,
    }


def _serialize_product(product: Product) -> dict[str, Any]:
    return {"id": product.id, "name": product.name}


def _serialize_product_market(product_market: ProductMarket) -> dict[str, Any]:
    return {
        "id": product_market.id,
        "product_id": product_market.product_id,
        "market": product_market.market,
        "market_product_id": product_market.market_product_id,
    }


def _serialize_video_product(video_product: VideoProduct) -> dict[str, Any]:
    return {
        "id": video_product.id,
        "video_id": video_product.video_id,
        "product_id": video_product.product_id,
        "name": video_product.name,
        "timestamp": video_product.timestamp,
        "source": video_product.source,
        "is_reviewed": video_product.is_reviewed,
        "is_found": video_product.is_found,
        "sort_order": video_product.sort_order,
    }


@csrf_exempt
@require_http_methods(["GET", "POST"])
def videos(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        data = [_serialize_video(v) for v in Video.objects.all().order_by("id")]
        return JsonResponse({"results": data})

    try:
        body = _parse_json(request)
    except ValueError as exc:
        return _json_error(str(exc))

    user_id = body.get("user_id")
    youtube_url = body.get("youtube_url")
    slug = body.get("slug")
    if not all([user_id, youtube_url, slug]):
        return _json_error("user_id, youtube_url, and slug are required")
    user = get_object_or_404(get_user_model(), pk=user_id)
    video = Video.objects.create(
        user=user,
        youtube_url=youtube_url,
        slug=slug,
        status=body.get("status") or Video._meta.get_field("status").default,
    )
    return JsonResponse(_serialize_video(video), status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def video_detail(request: HttpRequest, video_id: int) -> HttpResponse:
    video = get_object_or_404(Video, pk=video_id)
    if request.method == "GET":
        return JsonResponse(_serialize_video(video))
    if request.method == "DELETE":
        video.delete()
        return HttpResponse(status=204)

    try:
        body = _parse_json(request)
    except ValueError as exc:
        return _json_error(str(exc))

    if "youtube_url" in body:
        video.youtube_url = body["youtube_url"]
    if "status" in body:
        video.status = body["status"]
    if "slug" in body:
        video.slug = body["slug"]
    if "user_id" in body:
        user = get_object_or_404(get_user_model(), pk=body["user_id"])
        video.user = user
    video.save()
    return JsonResponse(_serialize_video(video))


@csrf_exempt
@require_http_methods(["GET", "POST"])
def products(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        data = [_serialize_product(p) for p in Product.objects.all().order_by("id")]
        return JsonResponse({"results": data})

    try:
        body = _parse_json(request)
    except ValueError as exc:
        return _json_error(str(exc))

    name = body.get("name")
    if not name:
        return _json_error("name is required")
    product = Product.objects.create(name=name)
    return JsonResponse(_serialize_product(product), status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def product_detail(request: HttpRequest, product_id: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=product_id)
    if request.method == "GET":
        return JsonResponse(_serialize_product(product))
    if request.method == "DELETE":
        product.delete()
        return HttpResponse(status=204)

    try:
        body = _parse_json(request)
    except ValueError as exc:
        return _json_error(str(exc))

    if "name" in body:
        product.name = body["name"]
    product.save()
    return JsonResponse(_serialize_product(product))


@csrf_exempt
@require_http_methods(["GET", "POST"])
def product_markets(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        data = [_serialize_product_market(pm) for pm in ProductMarket.objects.all().order_by("id")]
        return JsonResponse({"results": data})

    try:
        body = _parse_json(request)
    except ValueError as exc:
        return _json_error(str(exc))

    product_id = body.get("product_id")
    market = body.get("market")
    market_product_id = body.get("market_product_id")
    if not all([product_id, market, market_product_id]):
        return _json_error("product_id, market, and market_product_id are required")
    if market not in Market.values:
        return _json_error("invalid market")
    product = get_object_or_404(Product, pk=product_id)
    product_market = ProductMarket.objects.create(
        product=product, market=market, market_product_id=market_product_id
    )
    return JsonResponse(_serialize_product_market(product_market), status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def product_market_detail(request: HttpRequest, product_market_id: int) -> HttpResponse:
    product_market = get_object_or_404(ProductMarket, pk=product_market_id)
    if request.method == "GET":
        return JsonResponse(_serialize_product_market(product_market))
    if request.method == "DELETE":
        product_market.delete()
        return HttpResponse(status=204)

    try:
        body = _parse_json(request)
    except ValueError as exc:
        return _json_error(str(exc))

    if "market" in body:
        if body["market"] not in Market.values:
            return _json_error("invalid market")
        product_market.market = body["market"]
    if "market_product_id" in body:
        product_market.market_product_id = body["market_product_id"]
    if "product_id" in body:
        product_market.product = get_object_or_404(Product, pk=body["product_id"])
    product_market.save()
    return JsonResponse(_serialize_product_market(product_market))


@csrf_exempt
@require_http_methods(["GET", "POST"])
def video_products(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        data = [_serialize_video_product(vp) for vp in VideoProduct.objects.all().order_by("id")]
        return JsonResponse({"results": data})

    try:
        body = _parse_json(request)
    except ValueError as exc:
        return _json_error(str(exc))

    video_id = body.get("video_id")
    source = body.get("source")
    if not all([video_id, source]):
        return _json_error("video_id and source are required")
    video = get_object_or_404(Video, pk=video_id)
    product = None
    if body.get("product_id"):
        product = get_object_or_404(Product, pk=body["product_id"])

    video_product = VideoProduct.objects.create(
        video=video,
        product=product,
        name=body.get("name") or "",
        timestamp=body.get("timestamp") or "",
        source=source,
        is_reviewed=body.get("is_reviewed", False),
        is_found=body.get("is_found", True),
        sort_order=body.get("sort_order", 0),
    )
    return JsonResponse(_serialize_video_product(video_product), status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def video_product_detail(request: HttpRequest, video_product_id: int) -> HttpResponse:
    video_product = get_object_or_404(VideoProduct, pk=video_product_id)
    if request.method == "GET":
        return JsonResponse(_serialize_video_product(video_product))
    if request.method == "DELETE":
        video_product.delete()
        return HttpResponse(status=204)

    try:
        body = _parse_json(request)
    except ValueError as exc:
        return _json_error(str(exc))

    if "name" in body:
        video_product.name = body["name"]
    if "timestamp" in body:
        video_product.timestamp = body["timestamp"]
    if "source" in body:
        video_product.source = body["source"]
    if "is_reviewed" in body:
        video_product.is_reviewed = bool(body["is_reviewed"])
    if "is_found" in body:
        video_product.is_found = bool(body["is_found"])
    if "sort_order" in body:
        video_product.sort_order = body["sort_order"]
    if "video_id" in body:
        video_product.video = get_object_or_404(Video, pk=body["video_id"])
    if "product_id" in body:
        if body["product_id"] is None:
            video_product.product = None
        else:
            video_product.product = get_object_or_404(Product, pk=body["product_id"])
    video_product.save()
    return JsonResponse(_serialize_video_product(video_product))
