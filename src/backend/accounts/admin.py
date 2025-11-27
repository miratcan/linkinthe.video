"""Admin registrations for account models."""

from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (("Credits", {"fields": ("credits",)}),)
    list_display = DjangoUserAdmin.list_display + ("credits",)
