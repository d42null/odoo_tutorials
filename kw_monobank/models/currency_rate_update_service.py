import logging

from odoo import models, fields, _

_logger = logging.getLogger(__name__)


class CurrencyRateUpdateService(models.Model):
    _name = 'kw.currency.rate.update.service'
    _inherit = 'kw.currency.rate.update.service'

    rate_provider = fields.Selection(
        selection_add=[
            ('kw.currency.rate.provider.monobank', _('MonoBank')),
        ], )

    # pylint: disable=R1702,W8110
    def refresh_currency(self):
        for srv in self:
            if srv.rate_provider != 'kw.currency.rate.provider.monobank':
                super(CurrencyRateUpdateService, srv).refresh_currency()
                continue

            provider_obj = self.env[srv.rate_provider]
            provider = provider_obj.create({
                'date': fields.Date.today(),
            })
            main_cur = self.company_id.currency_id.kw_currency_code
            data = provider.get_currency_rate()
            if not data:
                continue

            for cur in self.env['res.currency'].search(
                    [('active', '=', True), ]):
                if srv.company_id.currency_id.id == cur.id:
                    continue

                monobank_cur = [obj for obj in data if
                                obj['currencyCodeA'] == int(
                                    cur.kw_currency_code) and
                                obj['currencyCodeB'] == int(main_cur)]
                if not monobank_cur:
                    continue

                for mono_cur in monobank_cur:
                    rate = mono_cur.get('rateCross') or \
                        1 / ((mono_cur.get('rateBuy')
                             + mono_cur.get('rateSell')) / 2)
                    rate = float('{:.5f}'.format(rate))
                    rates = self.env['res.currency.rate'].search([
                        ('currency_id', '=', cur.id),
                        ('company_id', '=', srv.company_id.id),
                        ('name', '=', fields.Date.today())])
                    if not rates:
                        self.env['res.currency.rate'].create({
                            'currency_id': cur.id,
                            'rate': rate,
                            'name': fields.Date.today(),
                            'company_id': srv.company_id.id,
                        })
                    else:
                        rates.rate = rate
