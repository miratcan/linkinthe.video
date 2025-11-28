import json

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from .models import (
    Market,
    Product,
    ProductMarket,
    Video,
    VideoProduct,
    VideoProductSource,
    VideoStatus,
)


class VideoModelTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="creator",
            email="creator@example.com",
            password="testpass",
        )

    def test_video_creation_and_status_default(self):
        video = Video.objects.create(
            user=self.user,
            youtube_url="https://youtu.be/test",
            slug="intro-video",
        )

        self.assertEqual(video.status, VideoStatus.PROCESSING)
        self.assertEqual(str(video), "creator@example.com - intro-video")

    def test_video_slug_uniqueness(self):
        Video.objects.create(
            user=self.user,
            youtube_url="https://youtu.be/one",
            slug="unique",
        )
        with self.assertRaises(IntegrityError):
            Video.objects.create(
                user=self.user,
                youtube_url="https://youtu.be/two",
                slug="unique",
            )


class ProductModelTests(TestCase):
    def setUp(self) -> None:
        self.product = Product.objects.create(name="Camera")

    def test_product_market_unique_combo(self):
        ProductMarket.objects.create(
            product=self.product,
            market=Market.AMAZON,
            market_product_id="B00TEST",
        )
        with self.assertRaises(IntegrityError):
            ProductMarket.objects.create(
                product=self.product,
                market=Market.AMAZON,
                market_product_id="B00TEST",
            )

    def test_product_market_str(self):
        mapping = ProductMarket.objects.create(
            product=self.product,
            market=Market.TRENDYOL,
            market_product_id="12345",
        )
        self.assertIn("Trendyol", str(mapping))


class VideoProductModelTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="creator",
            email="creator@example.com",
            password="testpass",
        )
        self.video = Video.objects.create(
            user=self.user,
            youtube_url="https://youtu.be/test",
            slug="primary",
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


class VideoApiTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="creator",
            email="creator@example.com",
            password="testpass",
        )
        self.user.credits = 2
        self.user.save()
        self.auth_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.user.api_token}"
        }

    def _post(self, path: str, payload: dict) -> dict:
        response = self.client.post(
            path,
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth_headers,
        )
        self.assertLess(response.status_code, 500)
        return {
            "status": response.status_code,
            "data": response.json() if response.content else {},
        }

    def _patch(self, path: str, payload: dict) -> dict:
        response = self.client.patch(
            path,
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth_headers,
        )
        self.assertLess(response.status_code, 500)
        return {
            "status": response.status_code,
            "data": response.json() if response.content else {},
        }

    def test_video_crud_flow(self):
        create_resp = self._post(
            "/api/videos/",
            {
                "user_id": self.user.id,
                "youtube_url": "https://youtu.be/api",
                "slug": "api-video",
            },
        )
        self.assertEqual(create_resp["status"], 201)
        video_id = create_resp["data"]["id"]

        list_resp = self.client.get("/api/videos/", **self.auth_headers)
        self.assertEqual(list_resp.status_code, 200)
        payload = list_resp.json()
        items = (
            payload["results"]
            if isinstance(payload, dict) and "results" in payload
            else payload
        )
        self.assertGreaterEqual(len(items), 1)

        update_resp = self._patch(
            f"/api/videos/{video_id}/",
            {"status": VideoStatus.COMPLETED, "slug": "api-video"},
        )
        self.assertEqual(update_resp["data"]["status"], VideoStatus.COMPLETED)

        status_resp = self.client.get(
            f"/api/videos/{video_id}/status", **self.auth_headers
        )
        self.assertEqual(status_resp.status_code, 200)

        delete_resp = self.client.delete(
            f"/api/videos/{video_id}/", **self.auth_headers
        )
        self.assertEqual(delete_resp.status_code, 204)

    def test_product_and_market_crud_flow(self):
        product_resp = self._post("/api/products/", {"name": "Camera"})
        self.assertEqual(product_resp["status"], 201)
        product_id = product_resp["data"]["id"]

        market_resp = self._post(
            "/api/product-markets/",
            {
                "product_id": product_id,
                "market": Market.AMAZON,
                "market_product_id": "B00TEST",
            },
        )
        self.assertEqual(market_resp["status"], 201)
        self.assertEqual(market_resp["data"]["market"], Market.AMAZON)

    def test_video_product_crud_flow(self):
        video_id = self._post(
            "/api/videos/",
            {
                "user_id": self.user.id,
                "youtube_url": "https://youtu.be/api2",
                "slug": "api-video-2",
            },
        )["data"]["id"]
        product_id = self._post("/api/products/", {"name": "Lens"})["data"][
            "id"
        ]

        vp_resp = self._post(
            f"/api/videos/{video_id}/products",
            {
                "product_id": product_id,
                "name": "Prime lens",
                "timestamp": "00:10",
                "source": VideoProductSource.MANUAL,
                "is_found": True,
            },
        )
        self.assertEqual(vp_resp["status"], 201)
        vp_id = vp_resp["data"]["id"]

        patch_resp = self._patch(
            f"/api/videos/{video_id}/products/{vp_id}",
            {
                "is_reviewed": True,
                "sort_order": 3,
                "amazon_url": "https://amazon.com/dp/B001234567",
            },
        )
        self.assertTrue(patch_resp["data"]["is_reviewed"])
        self.assertEqual(patch_resp["data"]["sort_order"], 3)

        products_resp = self.client.get(
            f"/api/videos/{video_id}/products", **self.auth_headers
        )
        self.assertEqual(products_resp.status_code, 200)
        self.assertGreaterEqual(len(products_resp.json()), 1)

    def test_credit_required_for_submit(self):
        self.user.credits = 0
        self.user.save()
        resp = self._post(
            "/api/videos/",
            {
                "user_id": self.user.id,
                "youtube_url": "https://youtu.be/nope",
                "slug": "no-credit",
            },
        )
        self.assertEqual(resp["status"], 402)


class ApiDocsTests(TestCase):
    def test_api_docs_endpoint(self):
        response = self.client.get("/api/openapi.json")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("paths", payload)
        self.assertTrue(
            any(path.startswith("/api/users/") for path in payload["paths"])
        )
        self.assertTrue(
            any(path.startswith("/api/videos/") for path in payload["paths"])
        )
