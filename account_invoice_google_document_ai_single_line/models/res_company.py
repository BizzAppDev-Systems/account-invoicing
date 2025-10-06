from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    google_ocr_invoice_mode = fields.Selection(
        [("default", "Default Mode"), ("single_line_total", "Single Line Total Mode")],
        default="default",
        help="Select the mode for Google Document AI Invoice OCR processing.",
    )
