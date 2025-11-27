"""User API router using Django Ninja (Shinobi)."""

from __future__ import annotations

from typing import Optional

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.urls import reverse
from ninja import Router, Schema

User = get_user_model()
router = Router(tags=["users"])


class UserSchema(Schema):
    id: int
    username: str
    email: Optional[str] = None
    credits: int


class UserCreateSchema(Schema):
    username: str
    email: str
    password: Optional[str] = None
    credits: Optional[int] = 0


class UserUpdateSchema(Schema):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    credits: Optional[int] = None


class AuthRegisterSchema(Schema):
    email: str
    password: str
    username: Optional[str] = None


class AuthLoginSchema(Schema):
    email: str
    password: str


class AuthResponseSchema(Schema):
    user: UserSchema
    session: Optional[str] = None


@router.get("users/", response=list[UserSchema])
def list_users(request):
    return User.objects.all().order_by("id")


@router.post("users/", response={201: UserSchema})
def create_user(request, payload: UserCreateSchema):
    password = payload.password or get_random_string(12)
    user = User.objects.create_user(
        username=payload.username,
        email=payload.email,
        password=password,
    )
    if payload.credits is not None:
        user.credits = payload.credits
        user.save()
    return 201, user


@router.get("users/{user_id}/", response=UserSchema)
def get_user(request, user_id: int):
    return get_object_or_404(User, pk=user_id)


@router.patch("users/{user_id}/", response=UserSchema)
def update_user(request, user_id: int, payload: UserUpdateSchema):
    user = get_object_or_404(User, pk=user_id)
    if payload.username is not None:
        user.username = payload.username
    if payload.email is not None:
        user.email = payload.email
    if payload.credits is not None:
        user.credits = payload.credits
    if payload.password:
        user.set_password(payload.password)
    user.save()
    return user


@router.delete("users/{user_id}/", response={204: None})
def delete_user(request, user_id: int):
    user = get_object_or_404(User, pk=user_id)
    user.delete()
    return 204, None


@router.post("auth/register", response={201: AuthResponseSchema})
def register(request, payload: AuthRegisterSchema):
    username = payload.username or payload.email.split("@")[0]
    user = User.objects.create_user(username=username, email=payload.email, password=payload.password)
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return 201, {"user": user, "session": request.session.session_key}


@router.post("auth/login", response=AuthResponseSchema)
def auth_login(request, payload: AuthLoginSchema):
    user = User.objects.filter(email__iexact=payload.email).first()
    username = user.username if user else payload.email
    user = authenticate(request, username=username, password=payload.password)
    if not user:
        return 401, {"detail": "Invalid credentials"}
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return {"user": user, "session": request.session.session_key}


@router.post("auth/logout", response={204: None})
def auth_logout(request):
    logout(request)
    return 204, None


@router.get("auth/me", response={200: AuthResponseSchema, 401: dict})
def auth_me(request):
    if not request.user.is_authenticated:
        return 401, {"detail": "Not authenticated"}
    return {"user": request.user, "session": request.session.session_key}


@router.post("auth/google", response=dict)
def auth_google(request):
    """Return Google OAuth start URL (callback handled by allauth at /accounts/google/login/)."""
    auth_url = request.build_absolute_uri(reverse("socialaccount_login", args=["google"]))
    return {"authorization_url": auth_url}
