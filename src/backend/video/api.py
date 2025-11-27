"""Video, product, and association APIs using Django Ninja (Shinobi)."""

from __future__ import annotations

from typing import Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from ninja import Router, Schema
from ninja.security import HttpBearer
from ninja.errors import HttpError

from .models import Market, Product, ProductMarket, Video, VideoProduct, VideoProductSource, VideoStatus


class BearerAuth(HttpBearer):
    def authenticate(self, request, token):
        user = User.objects.filter(api_token=token).first()
        return user


router = Router(tags=["videos"], auth=BearerAuth())
User = get_user_model()

def _extract_amazon_asin(url: str) -> str | None:
    """Naive ASIN extractor from Amazon URLs."""
    parts = url.split("/")
    for idx, part in enumerate(parts):
        if part in {"dp", "product"} and idx + 1 < len(parts):
            candidate = parts[idx + 1]
            if len(candidate) >= 10:
                return candidate[:10]
    return None

class VideoSchema(Schema):
    id: int
    user_id: int
    youtube_url: str
    status: str
    slug: str


class VideoCreateSchema(Schema):
    user_id: int
    youtube_url: str
    slug: str
    status: Optional[str] = None
    title: Optional[str] = None


class VideoUpdateSchema(Schema):
    user_id: Optional[int] = None
    youtube_url: Optional[str] = None
    slug: Optional[str] = None
    status: Optional[str] = None
    title: Optional[str] = None


class ProductSchema(Schema):
    id: int
    name: str


class ProductCreateSchema(Schema):
    name: str


class ProductUpdateSchema(Schema):
    name: Optional[str] = None


class ProductMarketSchema(Schema):
    id: int
    product_id: int
    market: str
    market_product_id: str


class ProductMarketCreateSchema(Schema):
    product_id: int
    market: str
    market_product_id: str


class ProductMarketUpdateSchema(Schema):
    product_id: Optional[int] = None
    market: Optional[str] = None
    market_product_id: Optional[str] = None


class VideoProductSchema(Schema):
    id: int
    video_id: int
    product_id: Optional[int] = None
    name: str
    timestamp: str
    source: str
    is_reviewed: bool
    is_found: bool
    sort_order: int


class VideoProductCreateSchema(Schema):
    video_id: Optional[int] = None
    product_id: Optional[int] = None
    name: Optional[str] = ""
    timestamp: Optional[str] = ""
    source: str
    is_reviewed: Optional[bool] = False
    is_found: Optional[bool] = True
    sort_order: Optional[int] = 0
    amazon_url: Optional[str] = None


class VideoProductUpdateSchema(Schema):
    video_id: Optional[int] = None
    product_id: Optional[int] = None
    name: Optional[str] = None
    timestamp: Optional[str] = None
    source: Optional[str] = None
    is_reviewed: Optional[bool] = None
    is_found: Optional[bool] = None
    sort_order: Optional[int] = None
    amazon_url: Optional[str] = None


@router.get("videos/", response=list[VideoSchema])
def list_videos(request):
    if not request.auth:
        return 401, {"detail": "Authentication required"}
    return Video.objects.filter(user=request.auth).order_by("-id")


@router.post("videos/", response={201: VideoSchema, 401: dict, 402: dict, 403: dict})
def create_video(request, payload: VideoCreateSchema):
    if not request.auth:
        return 401, {"detail": "Authentication required"}
    if request.auth.credits <= 0:
        return 402, {"detail": "Insufficient credits"}
    user = get_object_or_404(User, pk=payload.user_id)
    if user != request.auth:
        return 403, {"detail": "Cannot create videos for other users"}
    video = Video.objects.create(
        user=user,
        youtube_url=payload.youtube_url,
        slug=payload.slug,
        status=payload.status or Video._meta.get_field("status").default,
    )
    request.auth.credits -= 1
    request.auth.save(update_fields=["credits"])
    return 201, video


@router.get("videos/{video_id}/", response=VideoSchema)
def get_video(request, video_id: int):
    if not request.auth:
        return 401, {"detail": "Authentication required"}
    return get_object_or_404(Video, pk=video_id, user=request.auth)


@router.patch("videos/{video_id}/", response=VideoSchema)
def update_video(request, video_id: int, payload: VideoUpdateSchema):
    if not request.auth:
        return 401, {"detail": "Authentication required"}
    video = get_object_or_404(Video, pk=video_id, user=request.auth)
    if payload.user_id is not None and payload.user_id != request.auth.id:
        return 403, {"detail": "Cannot reassign video user"}
    if payload.youtube_url is not None:
        video.youtube_url = payload.youtube_url
    if payload.slug is not None:
        video.slug = payload.slug
    if payload.status is not None:
        video.status = payload.status
    if payload.title is not None:
        video.title = payload.title
    video.save()
    return video


@router.delete("videos/{video_id}/", response={204: None})
def delete_video(request, video_id: int):
    if not request.auth:
        return 401, {"detail": "Authentication required"}
    video = get_object_or_404(Video, pk=video_id, user=request.auth)
    video.delete()
    return 204, None


@router.get("products/", response=list[ProductSchema])
def list_products(request):
    return Product.objects.all().order_by("id")


@router.post("products/", response={201: ProductSchema})
def create_product(request, payload: ProductCreateSchema):
    product = Product.objects.create(name=payload.name)
    return 201, product


@router.get("products/{product_id}/", response=ProductSchema)
def get_product(request, product_id: int):
    return get_object_or_404(Product, pk=product_id)


@router.patch("products/{product_id}/", response=ProductSchema)
def update_product(request, product_id: int, payload: ProductUpdateSchema):
    product = get_object_or_404(Product, pk=product_id)
    if payload.name is not None:
        product.name = payload.name
    product.save()
    return product


@router.delete("products/{product_id}/", response={204: None})
def delete_product(request, product_id: int):
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    return 204, None


@router.get("product-markets/", response=list[ProductMarketSchema])
def list_product_markets(request):
    if not request.auth:
        return 401, {"detail": "Authentication required"}
    return ProductMarket.objects.all().order_by("id")


@router.post("product-markets/", response={201: ProductMarketSchema, 400: dict})
def create_product_market(request, payload: ProductMarketCreateSchema):
    if not request.auth:
        return 401, {"detail": "Authentication required"}
    if payload.market not in Market.values:
        return 400, {"detail": "invalid market"}
    product = get_object_or_404(Product, pk=payload.product_id)
    mapping = ProductMarket.objects.create(
        product=product,
        market=payload.market,
        market_product_id=payload.market_product_id,
    )
    return 201, mapping


@router.get("product-markets/{product_market_id}/", response=ProductMarketSchema)
def get_product_market(request, product_market_id: int):
    return get_object_or_404(ProductMarket, pk=product_market_id)


@router.patch("product-markets/{product_market_id}/", response=ProductMarketSchema)
def update_product_market(
    request, product_market_id: int, payload: ProductMarketUpdateSchema
):
    if not request.auth:
        return 401, {"detail": "Authentication required"}
    mapping = get_object_or_404(ProductMarket, pk=product_market_id)
    if payload.market is not None:
        if payload.market not in Market.values:
            return 400, {"detail": "invalid market"}
        mapping.market = payload.market
    if payload.market_product_id is not None:
        mapping.market_product_id = payload.market_product_id
    if payload.product_id is not None:
        mapping.product = get_object_or_404(Product, pk=payload.product_id)
    mapping.save()
    return mapping


@router.delete("product-markets/{product_market_id}/", response={204: None})
def delete_product_market(request, product_market_id: int):
    if not request.auth:
        return 401, {"detail": "Authentication required"}
    mapping = get_object_or_404(ProductMarket, pk=product_market_id)
    mapping.delete()
    return 204, None


@router.get("video-products/", response=list[VideoProductSchema])
def list_video_products(request):
    if not request.auth:
        return 401, {"detail": "Authentication required"}
    return VideoProduct.objects.filter(video__user=request.auth).order_by("id")


@router.post("video-products/", response={201: VideoProductSchema})
def create_video_product(request, payload: VideoProductCreateSchema):
    if not request.auth:
        return 401, {"detail": "Authentication required"}
    if not payload.video_id:
        return 422, {"detail": "video_id is required"}
    video = get_object_or_404(Video, pk=payload.video_id)
    if video.user != request.auth:
        return 403, {"detail": "Cannot add products to another user's video"}
    product = None
    if payload.product_id is not None:
        product = get_object_or_404(Product, pk=payload.product_id)
    elif payload.amazon_url:
        asin = _extract_amazon_asin(payload.amazon_url)
        product = Product.objects.create(name=payload.name or asin or "Manual product")
        if asin:
            ProductMarket.objects.get_or_create(
                product=product, market=Market.AMAZON, market_product_id=asin
            )
    video_product = VideoProduct.objects.create(
        video=video,
        product=product,
        name=payload.name or "",
        timestamp=payload.timestamp or "",
        source=payload.source,
        is_reviewed=payload.is_reviewed or False,
        is_found=payload.is_found if payload.is_found is not None else True,
        sort_order=payload.sort_order or 0,
    )
    return 201, video_product


@router.get("video-products/{video_product_id}/", response=VideoProductSchema)
def get_video_product(request, video_product_id: int):
    if not request.auth:
        return 401, {"detail": "Authentication required"}
    return get_object_or_404(VideoProduct, pk=video_product_id, video__user=request.auth)


@router.patch("video-products/{video_product_id}/", response=VideoProductSchema)
def update_video_product(
    request, video_product_id: int, payload: VideoProductUpdateSchema
):
    if not request.auth:
        return 401, {"detail": "Authentication required"}
    video_product = get_object_or_404(VideoProduct, pk=video_product_id, video__user=request.auth)
    if payload.video_id is not None:
        video_product.video = get_object_or_404(Video, pk=payload.video_id)
    if payload.product_id is not None:
        video_product.product = get_object_or_404(Product, pk=payload.product_id)
    if payload.amazon_url:
        asin = _extract_amazon_asin(payload.amazon_url)
        product = video_product.product or Product.objects.create(
            name=payload.name or asin or "Manual product"
        )
        if asin:
            ProductMarket.objects.get_or_create(
                product=product, market=Market.AMAZON, market_product_id=asin
            )
        video_product.product = product
    if payload.name is not None:
        video_product.name = payload.name or video_product.name
    if payload.timestamp is not None:
        video_product.timestamp = payload.timestamp
    if payload.source is not None:
        video_product.source = payload.source
    if payload.is_reviewed is not None:
        video_product.is_reviewed = payload.is_reviewed
    if payload.is_found is not None:
        video_product.is_found = payload.is_found
    if payload.sort_order is not None:
        video_product.sort_order = payload.sort_order
    video_product.save()
    return video_product


@router.delete("video-products/{video_product_id}/", response={204: None})
def delete_video_product(request, video_product_id: int):
    if not request.auth:
        return 401, {"detail": "Authentication required"}
    video_product = get_object_or_404(VideoProduct, pk=video_product_id, video__user=request.auth)
    video_product.delete()
    return 204, None
@router.get("videos/{video_id}/status", response=dict)
def video_status(request, video_id: int):
    if not request.auth:
        return 401, {"detail": "Authentication required"}
    video = get_object_or_404(Video, pk=video_id, user=request.auth)
    return {"id": video.id, "status": video.status}


@router.get("videos/{video_id}/products", response=list[VideoProductSchema])
def video_products(request, video_id: int):
    if not request.auth:
        return 401, {"detail": "Authentication required"}
    video = get_object_or_404(Video, pk=video_id, user=request.auth)
    return list(video.video_products.all())


@router.post("videos/{video_id}/products", response={201: VideoProductSchema})
def video_products_create(request, video_id: int, payload: VideoProductCreateSchema):
    payload.video_id = video_id
    return create_video_product(request, payload)


@router.patch("videos/{video_id}/products/{video_product_id}", response=VideoProductSchema)
def video_products_update(
    request, video_id: int, video_product_id: int, payload: VideoProductUpdateSchema
):
    payload.video_id = video_id
    return update_video_product(request, video_product_id, payload)


@router.delete("videos/{video_id}/products/{video_product_id}", response={204: None})
def video_products_delete(request, video_id: int, video_product_id: int):
    if not request.auth:
        return 401, {"detail": "Authentication required"}
    vp = get_object_or_404(
        VideoProduct, pk=video_product_id, video__user=request.auth, video_id=video_id
    )
    vp.delete()
    return 204, None


@router.post("videos/{video_id}/publish", response=VideoSchema)
def video_publish(request, video_id: int):
    if not request.auth:
        return 401, {"detail": "Authentication required"}
    video = get_object_or_404(Video, pk=video_id, user=request.auth)
    video.status = VideoStatus.COMPLETED
    video.save(update_fields=["status"])
    return video
