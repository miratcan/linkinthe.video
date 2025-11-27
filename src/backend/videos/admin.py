"""Admin registrations for video and product models."""

from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Product, ProductMarket, User, Video, VideoProduct


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (("Credits", {"fields": ("credits",)}),)
    list_display = DjangoUserAdmin.list_display + ("credits",)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "slug", "status")
    list_filter = ("status",)
    search_fields = ("slug", "youtube_url", "user__email", "user__username")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(ProductMarket)
class ProductMarketAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "market", "market_product_id")
    list_filter = ("market",)
    search_fields = ("product__name", "market_product_id")


@admin.register(VideoProduct)
class VideoProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "video",
        "product",
        "name",
        "timestamp",
        "source",
        "is_reviewed",
        "is_found",
        "sort_order",
    )
    list_filter = ("source", "is_reviewed", "is_found")
    search_fields = ("name", "product__name", "video__slug")
    ordering = ("sort_order", "id")

