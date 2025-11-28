import json

from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserApiTests(TestCase):
    def setUp(self):
        # Create admin user for protected endpoints
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass",
        )
        self.client.login(username="admin", password="adminpass")

    def test_user_crud_requires_admin(self):
        # Admin can create users
        create_resp = self.client.post(
            "/api/users/",
            data=json.dumps(
                {
                    "username": "apiuser",
                    "email": "api@example.com",
                    "credits": 10,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(create_resp.status_code, 201)
        user_id = create_resp.json()["id"]

        # Admin can update credits
        patch_resp = self.client.patch(
            f"/api/users/{user_id}/",
            data=json.dumps({"credits": 25}),
            content_type="application/json",
        )
        self.assertEqual(patch_resp.status_code, 200)
        self.assertEqual(patch_resp.json()["credits"], 25)

        # Admin can delete users
        delete_resp = self.client.delete(f"/api/users/{user_id}/")
        self.assertEqual(delete_resp.status_code, 204)
        self.assertFalse(User.objects.filter(pk=user_id).exists())

    def test_non_admin_cannot_list_users(self):
        # Create regular user
        User.objects.create_user(
            username="regular",
            email="regular@example.com",
            password="regularpass",
        )
        self.client.logout()
        self.client.login(username="regular", password="regularpass")

        # Regular user cannot list users
        list_resp = self.client.get("/api/users/")
        self.assertEqual(list_resp.status_code, 403)

    def test_user_can_update_self_but_not_credits(self):
        regular = User.objects.create_user(
            username="regular",
            email="regular@example.com",
            password="regularpass",
        )
        self.client.logout()
        self.client.login(username="regular", password="regularpass")

        # Can update own username
        patch_resp = self.client.patch(
            f"/api/users/{regular.id}/",
            data=json.dumps({"username": "newname"}),
            content_type="application/json",
        )
        self.assertEqual(patch_resp.status_code, 200)

        # Cannot update own credits
        patch_resp = self.client.patch(
            f"/api/users/{regular.id}/",
            data=json.dumps({"credits": 9999}),
            content_type="application/json",
        )
        self.assertEqual(patch_resp.status_code, 403)

    def test_auth_register_and_login(self):
        self.client.logout()

        register_resp = self.client.post(
            "/api/auth/register",
            data=json.dumps(
                {"email": "new@example.com", "password": "pass1234"}
            ),
            content_type="application/json",
        )
        self.assertEqual(register_resp.status_code, 201)
        self.assertIn("sessionid", register_resp.cookies)
        self.assertIn("token", register_resp.json())

        me_resp = self.client.get("/api/auth/me")
        self.assertEqual(me_resp.status_code, 200)

        logout_resp = self.client.post("/api/auth/logout")
        self.assertEqual(logout_resp.status_code, 204)
