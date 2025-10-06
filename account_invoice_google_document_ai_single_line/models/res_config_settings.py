from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    google_ocr_invoice_mode = fields.Selection(
        related="company_id.google_ocr_invoice_mode",
        readonly=False,
        required=True,
    )
