"""Ninja (Shinobi) API setup with autodocs."""

from __future__ import annotations

from ninja import NinjaAPI

from user.api import router as user_router
from video.api import router as video_router

api = NinjaAPI(title="linkinthe.video API", version="0.1.0")

# Routers register their own subpaths (e.g., users/, videos/, products/...)
api.add_router("/", user_router)
api.add_router("/", video_router)
