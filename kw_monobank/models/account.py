import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo import models, fields, _

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _name = 'account.journal'
    _inherit = ['account.journal', 'kw.finance.statement.import.mixin', ]

    kw_monobank_downloading_date = fields.Date(
        readonly=False, string='Monobank progress date',
        default=fields.Date.context_today)
    kw_monobank_token = fields.Char(
        string='Monobank token', )
    monobank_personal_account_id = fields.Many2one(
        comodel_name='kw.monobank.personal.account',
        domain="[('monobank_token', '=', kw_monobank_token)]")

    def __get_bank_statements_available_sources(self):
        res = super().__get_bank_statements_available_sources()
        res.append(('monobank', _('Monobank')))
        return res

    def kw_monobank_get_monobank(self):
        self.ensure_one()
        return self.env['kw.monobank.personal'].get_api(self.kw_monobank_token)

    def kw_monobank_init_sync(self):
        self.ensure_one()
        if self.kw_bank_import_initial_date:
            self.kw_monobank_downloading_date = \
                self.kw_bank_import_initial_date

    def get_monobank_account_info(self):
        self.ensure_one()
        if self.kw_monobank_token:
            account_info = self.env['kw.monobank.personal.account']
            account_info.api_personal_info_create(
                self.kw_monobank_token)

    def kw_monobank_self_sync(self):
        self.ensure_one()
        obj = self
        downloading_date = obj.kw_monobank_downloading_date
        last_statement = self.env['account.bank.statement'].search(
            [('journal_id', '=', obj.id), ('date', '<=', downloading_date)],
            order='date desc', limit=1)

        if last_statement:
            balance_end_real = last_statement.balance_end_real
        else:
            balance_end_real = 0
        bank_statement = self.env['account.bank.statement'].search(
            [('journal_id', '=', obj.id), ('date', '=', downloading_date)])
        if bank_statement:
            balance_end_real = bank_statement.balance_start
        if self.kw_monobank_token:
            _logger.info(downloading_date)
            monobank = obj.kw_monobank_get_monobank()
            data = obj.monobank_sync_statements(
                monobank.personal_statement(
                    obj.monobank_personal_account_id.accountId,
                    downloading_date,
                    downloading_date),
                balance_end_real)
            _logger.info(data)

    def _kw_monobank_cron_sync(self):
        for obj in self.env['account.journal'].search(
                [('bank_statements_source', '=', 'monobank')]):
            last_statement = self.env['account.bank.statement'].search(
                [('journal_id', '=', obj.id)], order='date desc', limit=1)
            downloading_date = obj.kw_monobank_downloading_date
            if last_statement:
                balance_end_real = last_statement.balance_end_real
            else:
                balance_end_real = 0
            bank_statement = self.env['account.bank.statement'].search(
                [('journal_id', '=', obj.id), ('date', '=', downloading_date)])
            if bank_statement:
                balance_end_real = bank_statement.balance_start
            if obj.kw_monobank_token:
                _logger.info(downloading_date)
                monobank = obj.kw_monobank_get_monobank()
                data = obj.monobank_sync_statements(
                    monobank.personal_statement(
                        obj.monobank_personal_account_id.accountId,
                        downloading_date,
                        downloading_date),
                    balance_end_real)
                _logger.info(data)
                if downloading_date < datetime.now().date() \
                        and datetime.now().time().hour > 3:
                    downloading_date = downloading_date + relativedelta(
                        days=1)
                    obj.kw_monobank_downloading_date = downloading_date

    def kw_monobank_today_sync(self):
        self.ensure_one()
        monobank = self.kw_monobank_get_monobank()
        self.monobank_sync_statements(monobank.get_statement_today())

    # pylint: disable=R1710
    def monobank_sync_statements(self, statement_records, balance_start):
        self.ensure_one()
        _logger.info(statement_records)
        acc_number = self.bank_account_id.acc_number.replace(' ', '')
        statements = {}
        if statement_records:
            for record in statement_records:
                if record.get('time'):
                    statement_date = datetime.fromtimestamp(
                        record.get('time')).date()
                    statement_date = datetime.strftime(
                        statement_date, '%d.%m.%Y')
                currency_id = self.env['res.currency'].search(
                    [('kw_currency_code', '=', record.get('currencyCode'))])
                if currency_id:
                    rate = currency_id.rate
                else:
                    rate = 1
                direction = (record.get('operationAmount', 0)/100)*(1/rate)
                if not statements.get(statement_date):
                    statements[statement_date] = {
                        'name': '{} {}'.format(acc_number, statement_date),
                        'date': datetime.fromtimestamp(
                            record.get('time')).strftime('%d.%m.%Y'),
                        'balance_start': balance_start,
                        'balance_end_real': balance_start + direction,
                        'transactions': [],
                    }
                else:
                    ber = statements[statement_date]['balance_end_real']
                    statements[statement_date]['balance_end_real'] =\
                        ber + direction
                partner_id = False
                counterIban = record.get('counterIban')
                if counterIban:
                    partner = self.get_partner(
                        enterprise_code=record.get('counterEdrpou'),
                        acc_number=record.get('counterIban'),
                        bank_name=record.get('counterEdrpou'),
                        create=self.kw_bank_import_partner_auto_create,
                        use_name_search=True, )
                    if partner:
                        partner_id = partner.id
                statements[statement_date]['transactions'].append({
                    'name': '%s-%s' % (acc_number, record.get('id')),
                    'date': datetime.fromtimestamp(record.get('time')),
                    'amount': direction,
                    'unique_import_id': '%s-%s' % (acc_number,
                                                   record.get('id')),
                    'partner_id': partner_id,
                    'note': record.get('comment'),
                    'ref': record.get('id'),
                    'payment_ref': record.get('description'),
                    'kw_bank_import_raw_acc': record.get('counterIban'),
                    'kw_bank_import_raw_enterprise_code':
                        record.get('counterEdrpou'),
                    'kw_bank_import_raw_description':
                        record.get('description'),
                    'journal_id': self.id,
                })
            self.kw_bank_import_commit_statement(statements)
            return statements

    def monobank_get_statement(self, account, from_date, to_date):
        monobank = self.kw_monobank_get_monobank()
        result = monobank.personal_statement(account, from_date, to_date)
        _logger.info(result)
