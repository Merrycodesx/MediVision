"""Desktop API client smoke tests.

Usage:
  cd medV_Desktop
  python test.py
"""

import unittest
from unittest.mock import Mock, patch

import requests

from components import api


class ApiClientTests(unittest.TestCase):
    def test_url_join(self):
        client = api.ApiClient("http://localhost:8000/api/")
        self.assertEqual(client._url("patients/"), "http://localhost:8000/api/patients/")
        self.assertEqual(client._url("/auth/login/"), "http://localhost:8000/api/auth/login/")

    def test_headers(self):
        client = api.ApiClient("http://localhost:8000/api")
        self.assertEqual(client._headers(), {})
        self.assertEqual(client._headers("abc"), {"Authorization": "Bearer abc"})

    @patch("components.api.requests.request")
    def test_request_success_payload(self, request_mock):
        response = Mock()
        response.status_code = 200
        response.text = '{"ok": true}'
        response.json.return_value = {"ok": True}
        response.raise_for_status.return_value = None
        request_mock.return_value = response

        client = api.ApiClient("http://localhost:8000/api")
        payload = client._request("GET", "test/")

        self.assertTrue(payload["success"])
        self.assertEqual(payload["status_code"], 200)
        self.assertTrue(payload["ok"])

    @patch("components.api.requests.request")
    def test_request_error_payload(self, request_mock):
        response = Mock()
        response.status_code = 401
        response.text = '{"detail": "Unauthorized"}'
        response.json.return_value = {"detail": "Unauthorized"}

        error = requests.HTTPError("401 Client Error")
        error.response = response

        request_mock.side_effect = error

        client = api.ApiClient("http://localhost:8000/api")
        payload = client._request("GET", "patients/")

        self.assertFalse(payload["success"])
        self.assertEqual(payload["status_code"], 401)
        self.assertIn("Unauthorized", payload["response"])
        self.assertEqual(payload["response_json"]["detail"], "Unauthorized")

    def test_login_helper_sets_token(self):
        with patch.object(api.client, "auth_login", return_value={"success": True, "access": "xyz"}):
            payload = api.login("x@y.com", "secret", "Doctor")

        self.assertTrue(payload["success"])
        self.assertEqual(payload["access"], "xyz")
        self.assertEqual(payload["token"], "xyz")


if __name__ == "__main__":
    unittest.main(verbosity=2)
