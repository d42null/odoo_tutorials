import logging

from odoo import models

_logger = logging.getLogger(__name__)


class CurrencyRateProvider(models.TransientModel):
    _name = 'kw.currency.rate.provider.monobank'
    _inherit = ['kw.monobank.personal', 'kw.currency.rate.provider', ]
    _description = 'Currency rate provider MonoBank'

    # pylint: disable=R1710
    def get_currency_rate(self):
        self.ensure_one()
        try:
            connector = self.get_api()
            res = connector.bank_currency()
        except Exception as e:
            _logger.debug('currency %s, date %, error',
                          self.currency, self.date, e)
            return None
        if res:
            return res
