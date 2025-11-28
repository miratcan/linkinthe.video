"""Pipeline tests."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase

from pipeline.adapters import (
    MockLLMProvider,
    MockProductSearchProvider,
    MockTranscriptionProvider,
    MockVisionProvider,
    ProviderRegistry,
)
from pipeline.client import trigger_analysis
from pipeline.steps import PipelineProviders, run_pipeline
from video.models import Video, VideoStatus


class AdapterTests(TestCase):
    """Test provider adapters."""

    def test_mock_transcription_provider(self):
        provider = MockTranscriptionProvider(text="Test transcript")
        result = provider.transcribe("/fake/path.wav")
        self.assertEqual(result.text, "Test transcript")
        self.assertEqual(result.language, "en")

    def test_mock_vision_provider(self):
        provider = MockVisionProvider()
        result = provider.analyze_image("/fake/image.jpg", "What products?")
        self.assertEqual(result.description, "Mock image analysis")
        self.assertGreaterEqual(len(result.products), 1)

    def test_mock_llm_provider(self):
        provider = MockLLMProvider()
        products = provider.extract_products("I love this tripod")
        self.assertGreaterEqual(len(products), 1)
        self.assertEqual(products[0]["name"], "Mock Tripod")

    def test_mock_product_search_provider(self):
        provider = MockProductSearchProvider()
        results = provider.search("camera")
        self.assertEqual(len(results), 1)
        self.assertIn("camera", results[0].name.lower())

        by_asin = provider.get_by_asin("B001234567")
        self.assertIsNotNone(by_asin)
        self.assertEqual(by_asin.asin, "B001234567")


class ProviderRegistryTests(TestCase):
    """Test provider factory."""

    def test_get_transcription_mock(self):
        provider = ProviderRegistry.get_transcription("mock")
        self.assertIsInstance(provider, MockTranscriptionProvider)

    def test_get_vision_mock(self):
        provider = ProviderRegistry.get_vision("mock")
        self.assertIsInstance(provider, MockVisionProvider)

    def test_get_llm_mock(self):
        provider = ProviderRegistry.get_llm("mock")
        self.assertIsInstance(provider, MockLLMProvider)

    def test_get_product_search_mock(self):
        provider = ProviderRegistry.get_product_search("mock")
        self.assertIsInstance(provider, MockProductSearchProvider)

    def test_unknown_provider_raises(self):
        with self.assertRaises(ValueError):
            ProviderRegistry.get_transcription("unknown")


class PipelineStepTests(TestCase):
    """Test pipeline execution."""

    def test_run_pipeline_with_mock_providers(self):
        providers = PipelineProviders(
            transcription=MockTranscriptionProvider(),
            vision=MockVisionProvider(),
            llm=MockLLMProvider(),
            product_search=MockProductSearchProvider(),
        )
        result = run_pipeline("https://youtu.be/mock", providers)
        self.assertGreaterEqual(len(result.found), 1)


class PipelineIntegrationTests(TestCase):
    """Test pipeline with database integration."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="creator", email="creator@example.com", password="pass"
        )
        self.video = Video.objects.create(
            user=self.user,
            youtube_url="https://youtu.be/mock",
            slug="mock-video",
        )

    def test_trigger_analysis_updates_status(self):
        self.user.credits = 5
        self.user.save()
        summary = trigger_analysis(self.video.id, use_mock=True)
        self.video.refresh_from_db()
        self.assertEqual(self.video.status, VideoStatus.COMPLETED)
        self.assertGreaterEqual(summary["found"], 1)

    def test_trigger_analysis_creates_video_products(self):
        self.user.credits = 5
        self.user.save()
        trigger_analysis(self.video.id, use_mock=True)
        self.video.refresh_from_db()
        products = self.video.video_products.all()
        self.assertGreaterEqual(products.count(), 1)
