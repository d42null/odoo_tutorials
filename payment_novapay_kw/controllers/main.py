# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import threading

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.tools import synchronized


_logger = logging.getLogger(__name__)


class NovaPayController(http.Controller):
    _notify_url = 'payment/novapay/notify'
    _return_url = 'payment/novapay/return'

    _payment_url = 'payment/status'

    _lock = threading.RLock()

    @synchronized()
    def novapay_validate_data(self, **post):  # pylint: disable=R0911
        model_data = request.env['ir.model.data'].sudo().search(
            [('name', '=', 'payment_provider_novapay'),
             ('module', '=', 'payment_novapay_kw')])
        if not model_data:
            return False
        provider = request.env['payment.provider'].sudo().search(
            [('id', '=', model_data.res_id)])
        if not provider:
            return False

        reference = post['external_id']
        if not reference:
            return False
        tx_model = request.env['payment.transaction'].sudo()
        tx = tx_model.search([('reference', '=', reference)])
        # transactions that done - need ignore
        if tx:
            if tx.state != 'done':
                try:
                    result = tx_model._handle_notification_data('novapay',
                                                                post)
                except Exception as e:
                    _logger.info('++++++++++++++++++++++++++++++++')
                    _logger.info(e)
                    result = True
                # need commit changes inside synchronized
                # block for avoid multi feedback's
                try:
                    request._cr.commit()
                except Exception as e:
                    _logger.info('++++++++++++++++++++++++++++++++')
                    _logger.info(e)
                return result
            # we shell return True in this case for
            # redirecting to validation url
            return True
        return False

    @http.route('/payment/novapay/notify', type='http', auth='none',
                methods=['POST'], csrf=False)
    def novapay_notify(self, **post):
        # try to validate notify response
        try:
            self.novapay_validate_data(**post)
        except ValidationError as ex:
            _logger.exception(str(ex))
        return ''

    @http.route('/payment/novapay/return', type='http', auth="public",
                methods=['POST', 'GET'], csrf=False, save_session=False)
    def novapay_return(self, **post):
        # try to validate return response
        if post:
            self.novapay_validate_data(**post)
        return request.redirect(self._payment_url)
