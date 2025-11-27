"""Lightweight JSON API endpoints for user operations."""

from __future__ import annotations

import json
from typing import Any

from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


User = get_user_model()


def _parse_json(request: HttpRequest) -> dict[str, Any]:
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode())
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON body")


def _json_error(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"error": message}, status=status)


def _serialize_user(user: User) -> dict[str, Any]:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "credits": user.credits,
    }


@csrf_exempt
@require_http_methods(["GET", "POST"])
def users(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        data = [_serialize_user(u) for u in User.objects.all().order_by("id")]
        return JsonResponse({"results": data})

    try:
        body = _parse_json(request)
    except ValueError as exc:
        return _json_error(str(exc))

    username = body.get("username")
    email = body.get("email")
    password = body.get("password") or get_random_string(12)
    if not all([username, email]):
        return _json_error("username and email are required")

    user = User.objects.create_user(username=username, email=email, password=password)
    if "credits" in body:
        user.credits = body["credits"]
        user.save()
    return JsonResponse(_serialize_user(user), status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def user_detail(request: HttpRequest, user_id: int) -> HttpResponse:
    user = get_object_or_404(User, pk=user_id)
    if request.method == "GET":
        return JsonResponse(_serialize_user(user))
    if request.method == "DELETE":
        user.delete()
        return HttpResponse(status=204)

    try:
        body = _parse_json(request)
    except ValueError as exc:
        return _json_error(str(exc))

    if "username" in body:
        user.username = body["username"]
    if "email" in body:
        user.email = body["email"]
    if "credits" in body:
        user.credits = body["credits"]
    if "password" in body and body["password"]:
        user.set_password(body["password"])
    user.save()
    return JsonResponse(_serialize_user(user))
