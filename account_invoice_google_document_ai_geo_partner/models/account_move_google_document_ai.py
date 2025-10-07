import logging

import requests

from odoo import api, models

_logger = logging.getLogger(__name__)


class AccountMoveGoogleDocumentAi(models.AbstractModel):
    _inherit = "account.move.google.document.ai"

    @api.model
    def _get_geocode_autocomplete_url(self):
        """Return the OpenStreetMap Nominatim URL from config."""
        return (
            self.env["ir.config_parameter"].sudo().get_param("geocode.autocomplete_url")
        )

    def _get_ocr_partner(self, partner_data):
        """Inherit method to search or create partner with geocode information."""
        partner = super()._get_ocr_partner(partner_data)
        if partner:
            return partner
        if partner_data.get("address"):
            address = partner_data["address"]
            geocode = self._get_geocode_from_address(address)
            if geocode:
                partner = self.env["res.partner"].search(
                    [
                        ("partner_latitude", "=", geocode["latitude"]),
                        ("partner_longitude", "=", geocode["longitude"]),
                    ],
                    limit=1,
                )
                if partner:
                    return partner
        partner_values = self._prepare_partner_data(partner_data, geocode)
        partner = self.env["res.partner"].create(partner_values)
        return partner

    def _prepare_partner_data(self, partner_data, geocode):
        """New method to prepare partner data with geocode information."""
        partner_values = {
            "name": partner_data.get("name", "Unknown"),
            "vat": partner_data.get("vat", False),
            "email": partner_data.get("email", False),
            "phone": partner_data.get("phone", False),
            "supplier_rank": 1,
        }
        if not geocode:
            return partner_values
        partner_values.update(
            {
                "partner_latitude": geocode.get("latitude", False),
                "partner_longitude": geocode.get("longitude", False),
            }
        )
        return partner_values

    def _get_geocode_from_address(self, address):
        """New method to get geocode information from address using OpenStreetMap
        Nominatim API."""
        try:
            url = self._get_geocode_autocomplete_url()
            response = requests.get(
                url,
                params={"q": address, "format": "json", "limit": 1},
                headers={"User-Agent": "Odoo Geocoder Bot"},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            if not data:
                return {}
            return {
                "latitude": data[0].get("lat"),
                "longitude": data[0].get("lon"),
                "display_name": data[0].get("display_name"),
            }
        except Exception as e:
            _logger.warning(f"Geocoding failed for address '{address}': {e}")
