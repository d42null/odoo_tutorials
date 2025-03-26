import requests

from odoo import fields, models, _
from odoo.http import InternalServerError


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('novapay', "NovaPay")],
        ondelete={'novapay': 'set default'}
    )
    novapay_merchant_id = fields.Integer(string="Merchant ID")
    novapay_auth_token = fields.Char(string="Merchant PUBLIC KEY")

    def _create_session(self, client_data, callback_url,
                        success_url, external_id):
        url = 'https://api-qecom.novapay.ua/v1/session'
        payload = {
            "merchant_id": self.novapay_merchant_id,
            "client_first_name": client_data.get("client_first_name"),
            "client_last_name": client_data.get("client_last_name"),
            "client_patronymic": client_data.get("client_patronymic"),
            "client_phone": client_data.get("client_phone"),
            "client_email": client_data.get("client_email"),
            "callback_url": callback_url,
            "success_url": success_url,
            "external_id": external_id,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "x-sign": self.novapay_auth_token,
        }
        response = requests.post(url, json=payload,
                                 headers=headers, timeout=5)
        if response.status_code != 200:
            raise InternalServerError(_('An API error has occurred '
                                        f'\nresponse: {response}'))
        session_id = response.json().get("id")
        return session_id

    def _add_payment(self, session_id, amount, currency):
        url = 'https://api-qecom.novapay.ua/v1/payment'
        payload = {
            "merchant_id": self.novapay_merchant_id,
            "session_id": session_id,
            "amount": amount,
            "currency": currency.name,
            "use_hold": False,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "x-sign": self.novapay_auth_token,
        }
        response = requests.post(url, json=payload,
                                 headers=headers, timeout=5)
        if response.status_code != 200:
            raise InternalServerError(_('An API error has occurred '
                                        f'\nresponse: {response}'))
        payment_url = response.json().get("url")
        return payment_url

    def _novapay_get_api_url(self, amount, currency, client_data, callback_url,
                             success_url, external_id):
        session_id = self._create_session(
            client_data, callback_url,
            success_url, external_id
        )
        api_url = self._add_payment(session_id, amount, currency)
        # api_url = "https://odootestnotify.requestcatcher.com/odootest" # TEST

        return api_url
