"""Account-related models."""

from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user with credit balance."""

    credits = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return self.email or self.username
