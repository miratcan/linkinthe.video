"""Database models for videos and products."""

from __future__ import annotations

from django.conf import settings
from django.db import models


class VideoStatus(models.TextChoices):
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"


class Video(models.Model):
    """Represents a processed or processing video."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="videos"
    )
    youtube_url = models.URLField()
    status = models.CharField(
        max_length=20,
        choices=VideoStatus.choices,
        default=VideoStatus.PROCESSING,
    )
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        return f"{self.user} - {self.slug}"


class Product(models.Model):
    """Global product catalogue entry."""

    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Market(models.TextChoices):
    AMAZON = "amazon", "Amazon"
    TRENDYOL = "trendyol", "Trendyol"
    OTHER = "other", "Other"


class ProductMarket(models.Model):
    """Mapping between a product and a specific market listing."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="markets")
    market = models.CharField(max_length=50, choices=Market.choices)
    market_product_id = models.CharField(max_length=255)

    class Meta:
        unique_together = ("product", "market", "market_product_id")

    def __str__(self) -> str:
        return f"{self.product} @ {self.get_market_display()}"


class VideoProductSource(models.TextChoices):
    AUDIO = "audio", "Audio"
    VIDEO = "video", "Video"
    SUBTITLE = "subtitle", "Subtitle"
    MANUAL = "manual", "Manual"


class VideoProduct(models.Model):
    """Association between a video and a product (found or lost)."""

    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="video_products")
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="video_products",
    )
    name = models.CharField(max_length=255, blank=True)
    timestamp = models.CharField(max_length=10, blank=True)
    source = models.CharField(max_length=20, choices=VideoProductSource.choices)
    is_reviewed = models.BooleanField(default=False)
    is_found = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return self.name or (self.product.name if self.product else "Unnamed Product")
