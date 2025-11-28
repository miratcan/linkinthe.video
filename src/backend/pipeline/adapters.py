"""LLM provider interfaces and implementations."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class LLMProvider(ABC):
    """Interface for extracting product candidates from transcripts."""

    @abstractmethod
    def extract_products(self, transcript: str) -> List[Dict[str, Any]]:
        raise NotImplementedError


class MockProvider(LLMProvider):
    """Simple provider for tests and local runs."""

    def __init__(self, products: List[Dict[str, Any]] | None = None) -> None:
        self.products = products or [
            {"name": "Mock Tripod", "timestamp": "00:42", "sources": ["audio"], "asin": "B00MOCK123"}
        ]

    def extract_products(self, transcript: str) -> List[Dict[str, Any]]:
        return self.products


class OpenAIProvider(LLMProvider):
    """litellm-backed OpenAI provider (lazy import to avoid hard dependency in tests)."""

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.model = model

    def extract_products(self, transcript: str) -> List[Dict[str, Any]]:
        try:
            import litellm  # type: ignore
        except ImportError as exc:  # pragma: no cover - requires optional dep
            raise RuntimeError("litellm is required for OpenAIProvider") from exc

        prompt = (
            "Extract product mentions with optional timestamps from this transcript. "
            "Return JSON list objects with keys: name, timestamp (MM:SS), asin (if obvious). "
            f"Transcript:\n{transcript}"
        )
        response = litellm.completion(model=self.model, messages=[{"role": "user", "content": prompt}])
        content = response.choices[0].message["content"]  # type: ignore[index]
        try:
            parsed = json.loads(content)
            if isinstance(parsed, list):
                return parsed  # pragma: no cover - depends on model response
        except Exception:
            pass
        return []
