import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class MonobankPersonalAccounts(models.Model):
    _name = 'kw.monobank.personal.account'
    _description = 'kw.monobank.personal.account'

    name = fields.Char(readonly=1)
    monobank_token = fields.Char(readonly=1)
    client_name = fields.Char(readonly=1)
    clientId = fields.Char(readonly=1, required=True,)
    accountId = fields.Char(readonly=1)
    sendId = fields.Char(readonly=1)
    balance = fields.Float(readonly=1)
    credit_limit = fields.Float(readonly=1)
    currency_code = fields.Integer(readonly=1)
    cashback_type = fields.Char(readonly=1)
    type = fields.Char(readonly=1)
    iban = fields.Char(readonly=1)
    maskedPan = fields.Char(readonly=1, required=True,)

    def kw_monobank_get_monobank(self, token):
        return self.env['kw.monobank.personal'].get_api(token)

    def api_personal_info_create(self, token):
        monobank = self.kw_monobank_get_monobank(token)
        data = monobank.personal_client_info()
        if data:
            for account in data.get('accounts'):
                name = '{} - {} ({})'.format(
                    data.get('name'), account.get('maskedPan')[0]
                    if account.get('maskedPan') else 'No card number',
                    account.get('type'))
                account_id = self.env['kw.monobank.personal.account'].search(
                    [("name", "=", name), ("monobank_token", "=", token)])
                if not account_id:
                    personal_info = {
                        'name': name,
                        'monobank_token': token,
                        'client_name': data.get('name'),
                        'clientId': data.get('clientId'),
                        'accountId': account.get('id'),
                        'sendId': account.get('sendId'),
                        'balance': account.get('balance')/100,
                        'currency_code': account.get('currencyCode'),
                        'credit_limit': account.get('creditLimit'),
                        'cashback_type': account.get('cashbackType'),
                        'type': account.get('type'),
                        'iban': account.get('iban'),
                        'maskedPan': account.get(
                            'maskedPan')[0] if account.get(
                                'maskedPan') else 'No card number'
                    }
                    self.create(personal_info)
