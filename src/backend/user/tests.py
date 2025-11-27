import json

from django.contrib.auth import get_user_model
from django.test import TestCase


class UserApiTests(TestCase):
    def test_user_crud_flow_and_auth(self):
        create_resp = self.client.post(
            "/api/users/",
            data=json.dumps({"username": "apiuser", "email": "api@example.com", "credits": 10}),
            content_type="application/json",
        )
        self.assertEqual(create_resp.status_code, 201)
        user_id = create_resp.json()["id"]

        patch_resp = self.client.patch(
            f"/api/users/{user_id}/",
            data=json.dumps({"credits": 25}),
            content_type="application/json",
        )
        self.assertEqual(patch_resp.status_code, 200)
        self.assertEqual(patch_resp.json()["credits"], 25)

        register_resp = self.client.post(
            "/api/auth/register",
            data=json.dumps({"email": "new@example.com", "password": "pass1234"}),
            content_type="application/json",
        )
        self.assertEqual(register_resp.status_code, 201)
        self.assertIn("sessionid", register_resp.cookies)

        me_resp = self.client.get("/api/auth/me")
        self.assertEqual(me_resp.status_code, 200)

        logout_resp = self.client.post("/api/auth/logout")
        self.assertEqual(logout_resp.status_code, 204)

        delete_resp = self.client.delete(f"/api/users/{user_id}/")
        self.assertEqual(delete_resp.status_code, 204)
        self.assertFalse(get_user_model().objects.filter(pk=user_id).exists())
