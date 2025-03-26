# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from datetime import datetime

import phonenumbers
from werkzeug import urls

from odoo import _, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.payment import utils as payment_utils
from ..controllers.main import NovaPayController

_logger = logging.getLogger(__name__)

SUPERUSER_ID = 1

NOVAPAY__DONE_STATES = ['paid']
NOVAPAY__ERROR_STATES = ['expired', 'failed']


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    novapay_type = fields.Char('Transaction type')

    def _novapay_is_phone_number_valid_ua(self, phone):
        try:
            parsed_number = phonenumbers.parse(phone)
            if phonenumbers.is_valid_number_for_region(parsed_number, 'UA'):
                return True
        except phonenumbers.phonenumberutil.NumberParseException as ex_:
            _logger.info(f'Phone validation Error(NovaPay):  \n\n\n {ex_}')
        return False

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'novapay':
            return res

        amount = self.amount
        currency = self.env['res.currency'].sudo().browse(
            processing_values.get('currency_id'))
        if not currency.name == 'UAH':
            raise ValidationError(_(f'Wrong currency ("{currency.name}") for '
                                    'this transaction. For successful payment '
                                    'set currency to "UAH".'))
        if not self._novapay_is_phone_number_valid_ua(self.partner_phone):
            raise ValidationError(_(
                f'Wrong partner phone ("{self.partner_phone}") for this '
                'transaction. For successful payment set a valid "UA" '
                'phone number i.e. \n"+380 000000000"'
            ))
        (partner_first_name, partner_last_name) = \
            payment_utils.split_partner_name(self.partner_name)

        client_data = {
            "client_first_name": partner_first_name,
            "client_last_name": partner_last_name,
            "client_phone":
            self.partner_phone.replace(" ", "").replace("-", ""),
            "client_email": self.partner_email,
        }

        base_url = self.provider_id.get_base_url()
        callback_url = urls.url_join(base_url, NovaPayController._notify_url)
        success_url = urls.url_join(base_url, NovaPayController._return_url)
        external_id = processing_values['reference']

        api_url = self.provider_id._novapay_get_api_url(
            amount,
            currency,
            client_data,
            callback_url,
            success_url,
            external_id
        )
        parsed_url = urls.url_parse(api_url)
        url_params = urls.url_decode(parsed_url.query)

        return {
            'api_url': api_url.split("?")[0],
            'url_params': url_params
        }

    def _get_tx_from_notification_data(self, provider, data):
        tx = super()._get_tx_from_notification_data(provider, data)
        if provider != 'novapay':
            return tx

        reference = data.get('external_id')
        transaction_id = data.get('id')
        # response data must have them
        if not reference or not transaction_id:
            raise ValidationError(
                _('NovaPay: '
                  'received data with missing reference %(reference)s '
                  'or transaction_id %(transaction_id)s') % (reference,
                                                             transaction_id))

        # check if exist transaction
        txs = self.env['payment.transaction'].search(
            [('reference', '=', reference)]
        )
        if not txs or len(txs) > 1:

            error_msg = 'NovaPay: received data for id %s' % reference
            if not txs:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    # pylint: disable=R1710
    def _process_notification_data(self, data):
        super()._process_notification_data(data)
        if self.provider_code != 'novapay':
            return

        if self and self.state != 'done':
            status = data.get('status')
            res = {
                'provider_reference': data.get('id'),
                'novapay_type': 'novapay',
            }
            if status in NOVAPAY__DONE_STATES:
                try:
                    date = datetime.datetime.fromtimestamp(
                        data.get('created_at') / 1000.0)
                except Exception:
                    date = fields.Datetime.now()
                res.update(state='done', last_state_change=date)
                transaction = self.write(res)
                self._set_done()
                self.with_user(SUPERUSER_ID)._post_process()
                return transaction
            if status in NOVAPAY__ERROR_STATES:
                error = data.get('status', '')
                transaction = self.write(res)
                self._set_error(error)
                return transaction

            # if check pending
            res.update(state='pending',
                       state_message=data.get('status', ''))
            return self.write(res)
        return
