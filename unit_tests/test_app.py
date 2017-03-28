from gatekeeper.main import app
from gatekeeper.views.deed_gatekeeper import build_response
import unittest
from unit_tests.schema_tests import run_schema_checks
from unittest.mock import Mock


class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_schema_checks(self):
        self.assertTrue(run_schema_checks())

    def test_build_response(self):
        mock_payload = Mock()
        mock_payload.json.return_value = {"deed": "/AAAAA"}
        mock_payload.status_code = 201
        mock_payload.headers = {"Content-Type": "application/json"}
        resp = build_response(mock_payload)

        self.assertTrue(resp.status_code)
        self.assertIn('{"deed": "/AAAAA"}', str(resp.data))
