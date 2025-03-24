import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class CurrencyRateProvider(models.TransientModel):
    _name = 'kw.currency.rate.provider'
    _description = 'Currency rate provider'

    date = fields.Date()
    currency = fields.Char()

    def get_currency_rate(self):
        _logger.debug(self)
        return 1
