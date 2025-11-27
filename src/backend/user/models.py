"""Account-related models."""

from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string


class User(AbstractUser):
    """Custom user with credit balance."""

    credits = models.PositiveIntegerField(default=0)
    api_token = models.CharField(max_length=64, unique=True, default="", blank=True)

    def save(self, *args, **kwargs):  # type: ignore[override]
        if not self.api_token:
            self.api_token = get_random_string(48)
        super().save(*args, **kwargs)

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return self.email or self.username
