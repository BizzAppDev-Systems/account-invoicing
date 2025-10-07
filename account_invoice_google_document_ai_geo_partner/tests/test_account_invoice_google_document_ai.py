from unittest.mock import patch

from odoo.addons.account_invoice_google_document_ai.tests.test_google_document_ai import (
    TestGoogleDocumentAi,
)


class TestAccountMoveGoogleDocumentAi(TestGoogleDocumentAi):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_data = {
            "name": "Test Partner",
            "address": "Test Address",
        }
        cls.geocode_data = {
            "latitude": "12.34",
            "longitude": "56.779999999999994",
            "display_name": "Test Address",
        }
        cls.ocr_model = cls.env["account.move.google.document.ai"]

    def _create_existing_partner(self):
        """Helper method to create an existing partner with geocode."""
        return self.env["res.partner"].create(
            {
                "name": "Existing Partner",
                "partner_latitude": self.geocode_data["latitude"],
                "partner_longitude": self.geocode_data["longitude"],
            }
        )

    def test_get_geocode_autocomplete_url(self):
        """New method to check geocode autocomplete URL retrieval."""
        self.env["ir.config_parameter"].sudo().set_param(
            "geocode.autocomplete_url", "https://fake.url/nominatim"
        )
        url = self.ocr_model._get_geocode_autocomplete_url()
        # Asserts the URL is correctly fetched from config.
        self.assertEqual(
            url,
            "https://fake.url/nominatim",
            "Geocode autocomplete URL is not correctly fetched from config.",
        )

    @patch("requests.get")
    def test_get_geocode_from_address_success(self, mock_get):
        """New method to check successful geocode retrieval from address."""
        mock_get.return_value.json.return_value = [
            {"lat": "12.34", "lon": "56.78", "display_name": "Test Address"}
        ]
        result = self.ocr_model._get_geocode_from_address("Test Address")
        # Asserts the geocode data is correctly returned.
        self.assertEqual(
            result["latitude"], "12.34", "Latitude is not correctly returned."
        )
        self.assertEqual(
            result["longitude"], "56.78", "Longitude is not correctly returned."
        )
        self.assertEqual(
            result["display_name"],
            "Test Address",
            "Display name is not correctly returned.",
        )

    @patch(
        "odoo.addons.account_invoice_google_document_ai_geo_partner.models."
        "account_move_google_document_ai.AccountMoveGoogleDocumentAi."
        "_get_geocode_from_address"
    )
    def test_get_ocr_partner_with_existing_geocode(self, mock_get_geocode):
        """New method to check _get_ocr_partner when partner with geocode exists."""
        mock_get_geocode.return_value = self.geocode_data
        existing_partner = self._create_existing_partner()
        partner = self.ocr_model._get_ocr_partner(self.partner_data)
        # Assert that the existing partner is returned
        self.assertEqual(
            partner.id, existing_partner.id, "Existing partner is not returned."
        )

    @patch(
        "odoo.addons.account_invoice_google_document_ai_geo_partner.models."
        "account_move_google_document_ai.AccountMoveGoogleDocumentAi."
        "_get_geocode_from_address"
    )
    def test_get_ocr_partner_with_new_geocode(self, mock_get_geocode):
        """New method to check _get_ocr_partner when no partner with geocode exists."""
        mock_get_geocode.return_value = self.geocode_data
        partner = self.ocr_model._get_ocr_partner(self.partner_data)
        # Assert that a new partner is created
        self.assertEqual(
            partner.name,
            self.partner_data["name"],
            "Partner name is not correctly set.",
        )
        self.assertEqual(
            partner.partner_latitude,
            float(self.geocode_data["latitude"]),
            "Latitude is not correctly set.",
        )
        self.assertEqual(
            partner.partner_longitude,
            float(self.geocode_data["longitude"]),
            "Longitude is not correctly set.",
        )
