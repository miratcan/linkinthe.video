"""Provider interfaces and implementations for pipeline services.

All external API calls go through adapters for easy swapping and testing.
Each provider has: ABC interface, Mock, and real implementations.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class TranscriptionResult:
    """Result from transcription service."""

    text: str
    language: str = "en"
    segments: list[dict[str, Any]] | None = None  # Optional timestamps


@dataclass
class VisionResult:
    """Result from vision analysis."""

    description: str
    products: list[dict[str, Any]]  # Detected products with confidence


@dataclass
class ProductSearchResult:
    """Result from product search."""

    asin: str
    name: str
    image_url: str | None = None
    price: str | None = None
    url: str | None = None


# =============================================================================
# Transcription Provider
# =============================================================================


class TranscriptionProvider(ABC):
    """Interface for audio-to-text transcription services."""

    @abstractmethod
    def transcribe(self, audio_path: str) -> TranscriptionResult:
        """Transcribe audio file to text."""
        raise NotImplementedError


class MockTranscriptionProvider(TranscriptionProvider):
    """Mock provider for tests."""

    def __init__(self, text: str = "This is a mock transcript.") -> None:
        self._text = text

    def transcribe(self, audio_path: str) -> TranscriptionResult:
        return TranscriptionResult(text=self._text, language="en")


class WhisperProvider(TranscriptionProvider):
    """OpenAI Whisper API provider via litellm."""

    def __init__(self, model: str = "whisper-1") -> None:
        self.model = model

    def transcribe(self, audio_path: str) -> TranscriptionResult:
        try:
            import litellm  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "litellm is required for WhisperProvider"
            ) from exc

        with open(audio_path, "rb") as audio_file:
            response = litellm.transcription(
                model=self.model,
                file=audio_file,
            )

        return TranscriptionResult(
            text=response.text,
            language=getattr(response, "language", "en"),
        )


class GeminiTranscriptionProvider(TranscriptionProvider):
    """Google Gemini transcription via litellm."""

    def __init__(self, model: str = "gemini/gemini-1.5-flash") -> None:
        self.model = model

    def transcribe(self, audio_path: str) -> TranscriptionResult:
        try:
            import base64

            import litellm  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "litellm is required for GeminiTranscriptionProvider"
            ) from exc

        with open(audio_path, "rb") as f:
            audio_data = base64.b64encode(f.read()).decode("utf-8")

        response = litellm.completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Transcribe this audio. Return only the "
                                "transcription text, nothing else."
                            ),
                        },
                        {
                            "type": "audio_url",
                            "audio_url": {
                                "url": f"data:audio/wav;base64,{audio_data}"
                            },
                        },
                    ],
                }
            ],
        )

        text = response.choices[0].message.content or ""
        return TranscriptionResult(text=text, language="en")


# =============================================================================
# Vision Provider
# =============================================================================


class VisionProvider(ABC):
    """Interface for image analysis services."""

    @abstractmethod
    def analyze_image(
        self, image_path: str, prompt: str
    ) -> VisionResult:
        """Analyze image and extract information based on prompt."""
        raise NotImplementedError


class MockVisionProvider(VisionProvider):
    """Mock provider for tests."""

    def __init__(
        self, products: list[dict[str, Any]] | None = None
    ) -> None:
        self._products = products or [
            {"name": "Mock Product", "confidence": 0.95}
        ]

    def analyze_image(
        self, image_path: str, prompt: str
    ) -> VisionResult:
        return VisionResult(
            description="Mock image analysis",
            products=self._products,
        )


class OpenAIVisionProvider(VisionProvider):
    """OpenAI GPT-4 Vision provider via litellm."""

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.model = model

    def analyze_image(
        self, image_path: str, prompt: str
    ) -> VisionResult:
        try:
            import base64

            import litellm  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "litellm is required for OpenAIVisionProvider"
            ) from exc

        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        ext = image_path.rsplit(".", 1)[-1].lower()
        mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png"}.get(ext, "jpeg")

        system_prompt = (
            "You are a product identification assistant. "
            "Analyze images and identify products. "
            "Return JSON with 'description' and 'products' array. "
            "Each product has 'name' and 'confidence' (0-1)."
        )

        response = litellm.completion(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{mime};base64,{image_data}"
                            },
                        },
                    ],
                },
            ],
        )

        content = response.choices[0].message.content or "{}"
        try:
            data = json.loads(content)
            return VisionResult(
                description=data.get("description", ""),
                products=data.get("products", []),
            )
        except json.JSONDecodeError:
            return VisionResult(description=content, products=[])


class GeminiVisionProvider(VisionProvider):
    """Google Gemini Vision provider via litellm."""

    def __init__(self, model: str = "gemini/gemini-1.5-flash") -> None:
        self.model = model

    def analyze_image(
        self, image_path: str, prompt: str
    ) -> VisionResult:
        try:
            import base64

            import litellm  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "litellm is required for GeminiVisionProvider"
            ) from exc

        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        ext = image_path.rsplit(".", 1)[-1].lower()
        mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png"}.get(ext, "jpeg")

        full_prompt = (
            f"{prompt}\n\n"
            "Return JSON with 'description' and 'products' array. "
            "Each product has 'name' and 'confidence' (0-1)."
        )

        response = litellm.completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": full_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{mime};base64,{image_data}"
                            },
                        },
                    ],
                }
            ],
        )

        content = response.choices[0].message.content or "{}"
        try:
            data = json.loads(content)
            return VisionResult(
                description=data.get("description", ""),
                products=data.get("products", []),
            )
        except json.JSONDecodeError:
            return VisionResult(description=content, products=[])


# =============================================================================
# LLM Provider (Product Extraction)
# =============================================================================


class LLMProvider(ABC):
    """Interface for LLM-based text analysis."""

    @abstractmethod
    def extract_products(
        self, transcript: str
    ) -> list[dict[str, Any]]:
        """Extract product mentions from transcript text."""
        raise NotImplementedError


class MockLLMProvider(LLMProvider):
    """Mock provider for tests."""

    def __init__(
        self, products: list[dict[str, Any]] | None = None
    ) -> None:
        self.products = products or [
            {
                "name": "Mock Tripod",
                "timestamp": "00:42",
                "sources": ["audio"],
                "asin": "B00MOCK123",
            }
        ]

    def extract_products(
        self, transcript: str
    ) -> list[dict[str, Any]]:
        return self.products


class OpenAILLMProvider(LLMProvider):
    """OpenAI GPT provider via litellm."""

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.model = model

    def extract_products(
        self, transcript: str
    ) -> list[dict[str, Any]]:
        try:
            import litellm  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "litellm is required for OpenAILLMProvider"
            ) from exc

        prompt = (
            "Extract product mentions from this transcript. "
            "Return a JSON array of objects with keys: "
            "name, timestamp (MM:SS if mentioned), asin (if obvious), "
            "sources (array: 'audio').\n\n"
            f"Transcript:\n{transcript}"
        )

        response = litellm.completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or "[]"
        try:
            data = json.loads(content)
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "products" in data:
                return data["products"]
        except json.JSONDecodeError:
            pass
        return []


class GeminiLLMProvider(LLMProvider):
    """Google Gemini provider via litellm."""

    def __init__(self, model: str = "gemini/gemini-1.5-flash") -> None:
        self.model = model

    def extract_products(
        self, transcript: str
    ) -> list[dict[str, Any]]:
        try:
            import litellm  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "litellm is required for GeminiLLMProvider"
            ) from exc

        prompt = (
            "Extract product mentions from this transcript. "
            "Return ONLY a JSON array of objects with keys: "
            "name, timestamp (MM:SS if mentioned), asin (if obvious), "
            "sources (array: 'audio'). No other text.\n\n"
            f"Transcript:\n{transcript}"
        )

        response = litellm.completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )

        content = response.choices[0].message.content or "[]"
        # Clean markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]

        try:
            data = json.loads(content.strip())
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "products" in data:
                return data["products"]
        except json.JSONDecodeError:
            pass
        return []


# =============================================================================
# Product Search Provider
# =============================================================================


class ProductSearchProvider(ABC):
    """Interface for product search services."""

    @abstractmethod
    def search(self, query: str) -> list[ProductSearchResult]:
        """Search for products by name/query."""
        raise NotImplementedError

    @abstractmethod
    def get_by_asin(self, asin: str) -> ProductSearchResult | None:
        """Get product details by ASIN."""
        raise NotImplementedError


class MockProductSearchProvider(ProductSearchProvider):
    """Mock provider for tests."""

    def search(self, query: str) -> list[ProductSearchResult]:
        return [
            ProductSearchResult(
                asin="B00MOCK123",
                name=f"Mock Product: {query}",
                image_url="https://example.com/mock.jpg",
            )
        ]

    def get_by_asin(self, asin: str) -> ProductSearchResult | None:
        return ProductSearchResult(
            asin=asin,
            name=f"Mock Product {asin}",
            image_url="https://example.com/mock.jpg",
        )


class AmazonProductSearchProvider(ProductSearchProvider):
    """Amazon Product Advertising API provider."""

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        partner_tag: str,
        region: str = "us-east-1",
    ) -> None:
        self.access_key = access_key
        self.secret_key = secret_key
        self.partner_tag = partner_tag
        self.region = region

    def search(self, query: str) -> list[ProductSearchResult]:
        # TODO: Implement Amazon PA-API search
        # This requires paapi5-python-sdk or manual signing
        raise NotImplementedError(
            "Amazon Product Search not yet implemented"
        )

    def get_by_asin(self, asin: str) -> ProductSearchResult | None:
        # TODO: Implement Amazon PA-API GetItems
        raise NotImplementedError(
            "Amazon Product Search not yet implemented"
        )


# =============================================================================
# Provider Registry (Factory)
# =============================================================================


class ProviderRegistry:
    """Factory for creating provider instances from config."""

    TRANSCRIPTION_PROVIDERS: dict[str, type[TranscriptionProvider]] = {
        "mock": MockTranscriptionProvider,
        "whisper": WhisperProvider,
        "gemini": GeminiTranscriptionProvider,
    }

    VISION_PROVIDERS: dict[str, type[VisionProvider]] = {
        "mock": MockVisionProvider,
        "openai": OpenAIVisionProvider,
        "gemini": GeminiVisionProvider,
    }

    LLM_PROVIDERS: dict[str, type[LLMProvider]] = {
        "mock": MockLLMProvider,
        "openai": OpenAILLMProvider,
        "gemini": GeminiLLMProvider,
    }

    PRODUCT_SEARCH_PROVIDERS: dict[str, type[ProductSearchProvider]] = {
        "mock": MockProductSearchProvider,
        "amazon": AmazonProductSearchProvider,
    }

    @classmethod
    def get_transcription(
        cls, name: str, **kwargs: Any
    ) -> TranscriptionProvider:
        """Get transcription provider by name."""
        provider_class = cls.TRANSCRIPTION_PROVIDERS.get(name)
        if not provider_class:
            raise ValueError(f"Unknown transcription provider: {name}")
        return provider_class(**kwargs)

    @classmethod
    def get_vision(cls, name: str, **kwargs: Any) -> VisionProvider:
        """Get vision provider by name."""
        provider_class = cls.VISION_PROVIDERS.get(name)
        if not provider_class:
            raise ValueError(f"Unknown vision provider: {name}")
        return provider_class(**kwargs)

    @classmethod
    def get_llm(cls, name: str, **kwargs: Any) -> LLMProvider:
        """Get LLM provider by name."""
        provider_class = cls.LLM_PROVIDERS.get(name)
        if not provider_class:
            raise ValueError(f"Unknown LLM provider: {name}")
        return provider_class(**kwargs)

    @classmethod
    def get_product_search(
        cls, name: str, **kwargs: Any
    ) -> ProductSearchProvider:
        """Get product search provider by name."""
        provider_class = cls.PRODUCT_SEARCH_PROVIDERS.get(name)
        if not provider_class:
            raise ValueError(f"Unknown product search provider: {name}")
        return provider_class(**kwargs)
