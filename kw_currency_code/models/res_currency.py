import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ResCurrency(models.Model):
    _name = 'res.currency'
    _inherit = 'res.currency'

    kw_currency_code = fields.Char(
        string='Currency code', size=3, readonly=True)
