"""URL configuration for linkinthe.video."""

from __future__ import annotations

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("control-panel/", admin.site.urls),
]
