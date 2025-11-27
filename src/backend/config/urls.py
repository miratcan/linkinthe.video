"""URL configuration for linkinthe.video."""

from __future__ import annotations

from django.contrib import admin
from django.urls import path

from user import api as user_api
from video import api as video_api

urlpatterns = [
    path("control-panel/", admin.site.urls),
    # API endpoints (lightweight CRUD)
    path("api/users/", user_api.users),
    path("api/users/<int:user_id>/", user_api.user_detail),
    path("api/videos/", video_api.videos),
    path("api/videos/<int:video_id>/", video_api.video_detail),
    path("api/products/", video_api.products),
    path("api/products/<int:product_id>/", video_api.product_detail),
    path("api/product-markets/", video_api.product_markets),
    path("api/product-markets/<int:product_market_id>/", video_api.product_market_detail),
    path("api/video-products/", video_api.video_products),
    path("api/video-products/<int:video_product_id>/", video_api.video_product_detail),
]
