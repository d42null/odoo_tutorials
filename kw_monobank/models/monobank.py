import datetime
import logging

import requests
from odoo import models

_logger = logging.getLogger(__name__)


class MonoBankApi:
    access_token = ''

    def __init__(self, access_token=''):
        self.access_token = access_token

    @staticmethod
    def get_url(ext=''):
        def urljoin(*args):
            return "/".join(map(lambda x: str(x).strip('/'), args))
        url = 'https://api.monobank.ua'
        return urljoin(url.strip('/'), ext.strip('/'))

    @staticmethod
    def headers():
        return {'Content-type': 'application/json',
                'Accept': 'text/plain',
                'Content-Encoding': 'utf-8'}

    def auth_headers(self):
        headers = self.headers()
        headers['X-Token'] = self.access_token
        return headers

    def request(self, method, url, data=None, params=None, headers=None,
                json_data=None, ):
        if not headers:
            headers = self.auth_headers()
        res = requests.request(
            method=method, url=self.get_url(url), data=data, params=params,
            headers=headers, json=json_data, timeout=10)
        if 200 > res.status_code or res.status_code > 300:
            # _logger.info(url)
            # _logger.info(params)
            # _logger.info(headers)
            # _logger.info(data)
            res = res.json()
            # _logger.info(res)
            return False
        # _logger.info(url)
        # _logger.info(params)
        # _logger.info(headers)
        # _logger.info(data)
        # _logger.info(res.text)
        res = res.json()
        # _logger.info(res)
        return res

    def get(self, url, params=None, headers=None):
        return self.request('get', url=url, params=params, headers=headers)

    def post(self, url, data=None, headers=None, json_data=None):
        return self.request('post', url=url, data=data, headers=headers,
                            json_data=json_data)

    def bank_currency(self):
        _logger.info('bank_currency')
        return self.get('/bank/currency')

    def personal_client_info(self):
        return self.get('/personal/client-info')

    def personal_webhook(self, webhook):
        data = {'webHookUrl': webhook}
        return self.post('/personal/webhook', data=data)

    def personal_statement(self, account, from_date, to_date):
        from_date = datetime.datetime(
            from_date.year, from_date.month, from_date.day, 0, 0, 0
        ).timestamp()
        to_date = datetime.datetime(
            to_date.year, to_date.month, to_date.day, 23, 59, 59
        ).timestamp()
        if not account:
            account = '0'
        return self.get(
            '/personal/statement/{account}/{from_date}/{to_date}'.format(
                account=account, from_date=str(int(from_date)),
                to_date=str(int(to_date))))


class MonoBank(models.AbstractModel):
    _name = 'kw.monobank.personal'
    _description = 'Mono Bank'

    @staticmethod
    def get_api(access_token=''):
        return MonoBankApi(access_token)
