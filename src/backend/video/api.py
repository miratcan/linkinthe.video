"""Video, product, and association APIs using Django Ninja (Shinobi)."""

from __future__ import annotations

from typing import Optional

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ninja import Router, Schema

from .models import Market, Product, ProductMarket, Video, VideoProduct, VideoProductSource, VideoStatus

router = Router(tags=["videos"])
User = get_user_model()


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


class VideoUpdateSchema(Schema):
    user_id: Optional[int] = None
    youtube_url: Optional[str] = None
    slug: Optional[str] = None
    status: Optional[str] = None


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
    video_id: int
    product_id: Optional[int] = None
    name: Optional[str] = ""
    timestamp: Optional[str] = ""
    source: str
    is_reviewed: Optional[bool] = False
    is_found: Optional[bool] = True
    sort_order: Optional[int] = 0


class VideoProductUpdateSchema(Schema):
    video_id: Optional[int] = None
    product_id: Optional[int] = None
    name: Optional[str] = None
    timestamp: Optional[str] = None
    source: Optional[str] = None
    is_reviewed: Optional[bool] = None
    is_found: Optional[bool] = None
    sort_order: Optional[int] = None


@router.get("videos/", response=list[VideoSchema])
def list_videos(request):
    return Video.objects.all().order_by("id")


@router.post("videos/", response={201: VideoSchema})
def create_video(request, payload: VideoCreateSchema):
    user = get_object_or_404(User, pk=payload.user_id)
    video = Video.objects.create(
        user=user,
        youtube_url=payload.youtube_url,
        slug=payload.slug,
        status=payload.status or Video._meta.get_field("status").default,
    )
    return 201, video


@router.get("videos/{video_id}/", response=VideoSchema)
def get_video(request, video_id: int):
    return get_object_or_404(Video, pk=video_id)


@router.patch("videos/{video_id}/", response=VideoSchema)
def update_video(request, video_id: int, payload: VideoUpdateSchema):
    video = get_object_or_404(Video, pk=video_id)
    if payload.user_id is not None:
        video.user = get_object_or_404(User, pk=payload.user_id)
    if payload.youtube_url is not None:
        video.youtube_url = payload.youtube_url
    if payload.slug is not None:
        video.slug = payload.slug
    if payload.status is not None:
        video.status = payload.status
    video.save()
    return video


@router.delete("videos/{video_id}/", response={204: None})
def delete_video(request, video_id: int):
    video = get_object_or_404(Video, pk=video_id)
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
    return ProductMarket.objects.all().order_by("id")


@router.post("product-markets/", response={201: ProductMarketSchema, 400: dict})
def create_product_market(request, payload: ProductMarketCreateSchema):
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
    mapping = get_object_or_404(ProductMarket, pk=product_market_id)
    mapping.delete()
    return 204, None


@router.get("video-products/", response=list[VideoProductSchema])
def list_video_products(request):
    return VideoProduct.objects.all().order_by("id")


@router.post("video-products/", response={201: VideoProductSchema})
def create_video_product(request, payload: VideoProductCreateSchema):
    video = get_object_or_404(Video, pk=payload.video_id)
    product = None
    if payload.product_id is not None:
        product = get_object_or_404(Product, pk=payload.product_id)
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
    return get_object_or_404(VideoProduct, pk=video_product_id)


@router.patch("video-products/{video_product_id}/", response=VideoProductSchema)
def update_video_product(
    request, video_product_id: int, payload: VideoProductUpdateSchema
):
    video_product = get_object_or_404(VideoProduct, pk=video_product_id)
    if payload.video_id is not None:
        video_product.video = get_object_or_404(Video, pk=payload.video_id)
    if payload.product_id is not None:
        video_product.product = get_object_or_404(Product, pk=payload.product_id)
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
    video_product = get_object_or_404(VideoProduct, pk=video_product_id)
    video_product.delete()
    return 204, None
