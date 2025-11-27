from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase

from pipeline.adapters import MockProvider
from pipeline.client import trigger_analysis
from pipeline.steps import run_analysis
from video.models import Video, VideoStatus


class PipelineStepTests(TestCase):
    def test_run_analysis_with_mock_provider(self):
        result = run_analysis("https://youtu.be/mock", MockProvider())
        self.assertGreaterEqual(len(result.found), 1)
        self.assertEqual(result.lost, [])


class PipelineIntegrationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="creator", email="creator@example.com", password="pass"
        )
        self.video = Video.objects.create(
            user=self.user, youtube_url="https://youtu.be/mock", slug="mock-video"
        )

    def test_trigger_analysis_updates_status(self):
        self.user.credits = 5
        self.user.save()
        summary = trigger_analysis(self.video.id, use_mock=True)
        self.video.refresh_from_db()
        self.assertEqual(self.video.status, VideoStatus.COMPLETED)
        self.assertGreaterEqual(summary["found"], 1)
