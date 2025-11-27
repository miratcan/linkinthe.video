"""Pipeline steps and orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from pipeline.adapters import LLMProvider


@dataclass
class PipelineResult:
    found: List[Dict[str, Any]]
    lost: List[Dict[str, Any]]


def download_video(youtube_url: str) -> str:
    """Stub for yt-dlp download; returns a fake path for now."""
    return f"/tmp/downloads/{youtube_url.rsplit('/', 1)[-1]}.mp4"


def extract_audio(video_path: str) -> str:
    """Stub for ffmpeg audio extraction; returns a fake path for now."""
    return video_path.replace(".mp4", ".wav")


def transcribe_audio(audio_path: str) -> str:
    """Stubbed transcription."""
    return f"Transcript for {audio_path}"


def detect_products(transcript: str, llm: LLMProvider) -> List[Dict[str, Any]]:
    return llm.extract_products(transcript)


def fuzzy_match(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return products


def search_amazon(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return products


def run_analysis(youtube_url: str, llm: LLMProvider) -> PipelineResult:
    video_path = download_video(youtube_url)
    audio_path = extract_audio(video_path)
    transcript = transcribe_audio(audio_path)
    candidates = detect_products(transcript, llm)
    enriched = search_amazon(fuzzy_match(candidates))

    found = [
        {
            "name": item.get("name", "Unknown"),
            "timestamp": item.get("timestamp", ""),
            "asin": item.get("asin"),
            "sources": item.get("sources", []),
        }
        for item in enriched
    ]
    return PipelineResult(found=found, lost=[])
