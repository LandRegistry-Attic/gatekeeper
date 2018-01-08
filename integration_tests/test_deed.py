import json
import unittest
import PyPDF2
import io
import os
import time

import requests
from integration_tests.deed_data import valid_deed
from gatekeeper.main import app


class TestDeedRoutes(unittest.TestCase):
    webseal_headers = {
        "Content-Type": "application/json",
        os.getenv("WEBSEAL_HEADER_KEY"): os.getenv('WEBSEAL_HEADER_VALUE')
    }

    webseal_headers_for_pdf = {
        "Content-Type": "application/json",
        "Accept": "application/pdf",
        os.getenv("WEBSEAL_HEADER_KEY"): os.getenv('WEBSEAL_HEADER_VALUE')
    }

    def setUp(self):
        self.app = app

    def test_deed_create_and_get(self):
        create_deed = requests.post(app.config["DEED_API_URL"] + '/deed/', data=json.dumps(valid_deed), headers=self.webseal_headers)
        self.assertEqual(create_deed.status_code, 201)
        self.assertIn("/deed/", str(create_deed.json()))
        created_deed = requests.get(app.config["DEED_API_URL"] + create_deed.json()["path"], headers=self.webseal_headers)
        self.assertEqual(created_deed.status_code, 200)

        created_deed = created_deed.json()

        self.assertIn("title_number", str(created_deed['deed']))
        self.assertIn("borrowers", str(created_deed['deed']))
        self.assertIn("forename", str(created_deed['deed']))
        self.assertIn("surname", str(created_deed['deed']))
        self.assertIn("charge_clause", str(created_deed['deed']))
        self.assertIn("additional_provisions", str(created_deed['deed']))
        self.assertIn("lender", str(created_deed['deed']))
        self.assertIn("property_address", str(created_deed['deed']))

    def test_bad_get(self):
        fake_token_deed = requests.get(app.config["DEED_API_URL"] + "/deed/fake", headers=self.webseal_headers)
        self.assertEqual(fake_token_deed.status_code, 404)

    def test_save_make_effective(self):
        create_deed = requests.post(app.config["DEED_API_URL"] + '/deed/',
                                    data=json.dumps(valid_deed),
                                    headers=self.webseal_headers)

        self.assertEqual(create_deed.status_code, 201)

        response_json = create_deed.json()

        get_created_deed = requests.get(app.config["DEED_API_URL"] + response_json["path"],
                                        headers=self.webseal_headers)

        self.assertEqual(get_created_deed.status_code, 200)

        created_deed = get_created_deed.json()

        code_payload = {
            "borrower_token": created_deed["deed"]["borrowers"][0]["token"]
        }

        request_code = requests.post(app.config["DEED_API_URL"] + response_json["path"] + '/request-auth-code',
                                     data=json.dumps(code_payload),
                                     headers=self.webseal_headers)

        self.assertEqual(request_code.status_code, 200)

        sign_payload = {
            "borrower_token": created_deed["deed"]["borrowers"][0]["token"],
            "authentication_code": "aaaa"
        }

        sign_deed = requests.post(app.config["DEED_API_URL"] + response_json["path"] + '/verify-auth-code',
                                  data=json.dumps(sign_payload),
                                  headers=self.webseal_headers)

        self.assertEqual(sign_deed.status_code, 200)

        timer = time.time() + 60
        while time.time() < timer and sign_deed.status_code != 200:
            make_effective = requests.post(app.config["DEED_API_URL"] + response_json["path"] + '/make-effective', headers=self.webseal_headers)

            self.assertEqual(make_effective.status_code, 200)

    def test_get_signed_deeds(self):
        create_deed = requests.post(app.config["DEED_API_URL"] + '/deed/',
                                    data=json.dumps(valid_deed),
                                    headers=self.webseal_headers)

        self.assertEqual(create_deed.status_code, 201)

        response_json = create_deed.json()

        get_created_deed = requests.get(app.config["DEED_API_URL"] + response_json["path"],
                                        headers=self.webseal_headers)

        self.assertEqual(get_created_deed.status_code, 200)

        created_deed = get_created_deed.json()

        code_payload = {
            "borrower_token": created_deed["deed"]["borrowers"][0]["token"]
        }

        request_code = requests.post(app.config["DEED_API_URL"] + response_json["path"] + '/request-auth-code',
                                     data=json.dumps(code_payload),
                                     headers=self.webseal_headers)

        self.assertEqual(request_code.status_code, 200)

        sign_payload = {
            "borrower_token": created_deed["deed"]["borrowers"][0]["token"],
            "authentication_code": "aaaa"
        }

        sign_deed = requests.post(app.config["DEED_API_URL"] + response_json["path"] + '/verify-auth-code',
                                  data=json.dumps(sign_payload),
                                  headers=self.webseal_headers)
        self.assertEqual(sign_deed.status_code, 200)

        test_result = requests.get(app.config["DEED_API_URL"] + '/deed/retrieve-signed',
                                   headers=self.webseal_headers)

        signed_deeds = test_result.json()
        self.assertIn("deeds", str(signed_deeds))

    def test_deed_pdf(self):
        create_deed = requests.post(app.config["DEED_API_URL"] + '/deed/',
                                    data=json.dumps(valid_deed),
                                    headers=self.webseal_headers)
        response_json = create_deed.json()
        get_created_deed = requests.get(app.config["DEED_API_URL"] + response_json["path"],
                                        headers=self.webseal_headers_for_pdf)
        obj = PyPDF2.PdfFileReader(io.BytesIO(get_created_deed.content))
        txt = obj.getPage(0).extractText()
        self.assertTrue('Digital Mortgage Deed' in txt)
        txt = obj.getPage(1).extractText()
        self.assertTrue('e-MD12344' in txt)
        # Can look at this file if you want.
        f = open('integration_test_deed.pdf', 'wb')
        f.write(get_created_deed.content)
        f.close()
