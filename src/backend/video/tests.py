from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from .models import Market, Product, ProductMarket, Video, VideoProduct, VideoProductSource, VideoStatus


class VideoModelTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="creator", email="creator@example.com", password="testpass"
        )

    def test_video_creation_and_status_default(self):
        video = Video.objects.create(
            user=self.user, youtube_url="https://youtu.be/test", slug="intro-video"
        )

        self.assertEqual(video.status, VideoStatus.PROCESSING)
        self.assertEqual(str(video), "creator@example.com - intro-video")

    def test_video_slug_uniqueness(self):
        Video.objects.create(user=self.user, youtube_url="https://youtu.be/one", slug="unique")
        with self.assertRaises(IntegrityError):
            Video.objects.create(
                user=self.user, youtube_url="https://youtu.be/two", slug="unique"
            )


class ProductModelTests(TestCase):
    def setUp(self) -> None:
        self.product = Product.objects.create(name="Camera")

    def test_product_market_unique_combo(self):
        ProductMarket.objects.create(
            product=self.product, market=Market.AMAZON, market_product_id="B00TEST"
        )
        with self.assertRaises(IntegrityError):
            ProductMarket.objects.create(
                product=self.product, market=Market.AMAZON, market_product_id="B00TEST"
            )

    def test_product_market_str(self):
        mapping = ProductMarket.objects.create(
            product=self.product, market=Market.TRENDYOL, market_product_id="12345"
        )
        self.assertIn("Trendyol", str(mapping))


class VideoProductModelTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="creator", email="creator@example.com", password="testpass"
        )
        self.video = Video.objects.create(
            user=self.user, youtube_url="https://youtu.be/test", slug="primary"
        )
        self.product = Product.objects.create(name="Microphone")

    def test_video_product_relations_and_defaults(self):
        vp = VideoProduct.objects.create(
            video=self.video,
            product=self.product,
            name="Desk Mic",
            timestamp="01:23",
            source=VideoProductSource.AUDIO,
            sort_order=5,
        )
        self.assertTrue(vp.is_found)
        self.assertFalse(vp.is_reviewed)
        self.assertEqual(vp.video, self.video)
        self.assertEqual(vp.product, self.product)
        self.assertEqual(str(vp), "Desk Mic")

    def test_video_product_null_product_for_lost_items(self):
        vp = VideoProduct.objects.create(
            video=self.video,
            product=None,
            name="Unknown cable",
            timestamp="02:00",
            source=VideoProductSource.MANUAL,
            is_found=False,
        )
        self.assertIsNone(vp.product)
        self.assertEqual(vp.name, "Unknown cable")
