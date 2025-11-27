import json

from django.contrib.auth import get_user_model
from django.test import TestCase


class UserApiTests(TestCase):
    def test_user_crud_flow(self):
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

        delete_resp = self.client.delete(f"/api/users/{user_id}/")
        self.assertEqual(delete_resp.status_code, 204)
        self.assertFalse(get_user_model().objects.filter(pk=user_id).exists())
