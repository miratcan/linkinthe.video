"""URL configuration for linkinthe.video."""

from __future__ import annotations

from django.contrib import admin
from django.urls import include, path

from config.api import api

urlpatterns = [
    path("control-panel/", admin.site.urls),
    path("api/", api.urls),
    path("accounts/", include("allauth.urls")),
]
