from unittest.mock import patch
from datetime import datetime
from odoo.tests.common import TransactionCase
from odoo import fields
from dateutil.relativedelta import relativedelta


class TestAccountJournal(TransactionCase):

    def setUp(self):
        super(TestAccountJournal, self).setUp()
        self.partner = self.env.ref('kw_monobank.demo_monobank_partner')
        self.company = self.env.ref('kw_monobank.demo_monobank_company')
        self.journal = self.env.ref(
            'kw_monobank.demo_monobank_journal'
        )
        # Link the partner to the company
        self.partner.write({"company_id": self.company.id})

    def test_get_bank_statements_available_sources(self):
        """Test getting available bank statement sources."""
        sources = self.journal._get_bank_statements_available_sources()
        self.assertIn(('monobank', 'Monobank'), sources)

    def test_kw_monobank_get_monobank(self):
        """Test getting Monobank API instance."""
        monobank_api = self.journal.kw_monobank_get_monobank()
        self.assertIsNotNone(monobank_api)

    def test_kw_monobank_init_sync(self):
        """Test initializing Monobank sync."""
        self.journal.kw_bank_import_initial_date = fields.Date.today()
        self.journal.kw_monobank_init_sync()
        self.assertEqual(
            self.journal.kw_monobank_downloading_date,
            self.journal.kw_bank_import_initial_date
        )

    @patch(
        'odoo.addons.kw_monobank.models.monobank.'
        'MonoBankApi.personal_client_info'
    )
    def test_get_monobank_account_info(self, mock_personal_client_info):
        """Test getting Monobank account info."""
        mock_personal_client_info.return_value = {
            'name': 'Test Client Mono',
            'clientId': 'test_mono_client_id',
            'accounts': [{
                'id': 'test_account_id',
                'maskedPan': ['1234'],
                'type': 'card',
                'balance': 10000,
                'currencyCode': 980,
                'creditLimit': 5000,
                'cashbackType': 'UAH',
                'iban': 'UA1234567890'
            }]
        }
        self.journal.get_monobank_account_info()
        mock_personal_client_info.assert_called_once()

        # Fetch the account and perform checks
        accounts = self.env['kw.monobank.personal.account'].search(
            [('clientId', '=', 'test_mono_client_id')]
        )

        # Basic check for number of accounts
        self.assertEqual(len(accounts), 1)

        # Detailed checks for each field
        account = accounts[0]
        self.assertEqual(account.client_name, 'Test Client Mono')
        self.assertEqual(account.clientId, 'test_mono_client_id')
        self.assertEqual(account.accountId, 'test_account_id')
        self.assertEqual(account.maskedPan, '1234')
        self.assertEqual(account.type, 'card')
        self.assertEqual(account.balance, 100)
        self.assertEqual(account.iban, 'UA1234567890')

    @patch(
        'odoo.addons.kw_monobank.models.monobank.'
        'MonoBankApi.personal_statement'
    )
    def test_kw_monobank_self_sync(self, mock_personal_statement):
        """Test self synchronization with Monobank with data."""
        mock_personal_statement.return_value = [{
            'time': 1622505600,
            'currencyCode': 980,
            'operationAmount': 10000,
            'counterIban': 'UA1234567890',
            'counterEdrpou': '12345678',
            'comment': 'Test transaction',
            'description': 'Test description',
            'id': 'test_id'
        }]
        self.journal.kw_monobank_self_sync()
        mock_personal_statement.assert_called_once()
        bank_statement = self.env['account.bank.statement'].search([
            ('journal_id', '=', self.journal.id),
        ])
        self.assertTrue(bank_statement)

        # Basic checks for bank statement
        self.assertEqual(bank_statement.balance_start, 0)

        # Check the balance end real
        expected_balance_end = 100
        self.assertEqual(bank_statement.balance_end_real,
                         expected_balance_end)

        # Check the transactions list
        self.assertEqual(len(bank_statement.line_ids), 1)

        # Check the transaction details
        transaction = bank_statement.line_ids[0]
        self.assertEqual(transaction.amount, 100)
        self.assertEqual(transaction.name,
                         'MONO_/2021/00001')
        self.assertEqual(transaction.note, 'Test transaction')
        self.assertEqual(transaction.payment_ref, 'Test description')
        self.assertEqual(transaction.kw_bank_import_raw_acc, 'UA1234567890')
        self.assertEqual(transaction.kw_bank_import_raw_enterprise_code,
                         '12345678')
        self.assertEqual(transaction.kw_bank_import_raw_description,
                         'Test description')

    @patch(
        'odoo.addons.kw_monobank.models.monobank.'
        'MonoBankApi.personal_statement'
    )
    def test_kw_monobank_cron_sync_with_data(self, mock_personal_statement):
        """Test cron synchronization with Monobank with data."""
        mock_personal_statement.return_value = [{
            'time': 1622505600,
            'currencyCode': 980,
            'operationAmount': 10000,
            'counterIban': 'UA1234567890',
            'counterEdrpou': '12345678',
            'comment': 'Test transaction',
            'description': 'Test description',
            'id': 'test_id'
        }]

        # Set downloading date to a past date to test updating
        past_date = datetime(2022, 1, 1).date()
        self.journal.kw_monobank_downloading_date = past_date

        self.journal._kw_monobank_cron_sync()

        # Ensure the personal_statement method was called
        mock_personal_statement.assert_called()

        # Ensure that there are journals to sync
        journals = self.env['account.journal'].search(
            [('bank_statements_source', '=', 'monobank')]
        )
        self.assertGreater(len(journals), 0, "No journals found for Monobank")

        # Check if the personal_statement method was called
        mock_personal_statement.assert_called()

        # Check if downloading date was updated if it was in the past
        if past_date < datetime.now().date():
            self.assertGreaterEqual(self.journal.kw_monobank_downloading_date,
                                    past_date + relativedelta(days=1))

        bank_statement = self.env['account.bank.statement'].search([
            ('journal_id', '=', self.journal.id),
        ])

        self.assertTrue(bank_statement)

        # Basic checks for bank statement
        self.assertEqual(bank_statement.balance_start, 0)

        # Check the balance end real
        expected_balance_end = 100
        self.assertEqual(bank_statement.balance_end_real,
                         expected_balance_end)

        # Check the transactions list
        self.assertEqual(len(bank_statement.line_ids), 1)

        # Check the transaction details
        transaction = bank_statement.line_ids[0]
        self.assertEqual(transaction.amount, 100)
        self.assertEqual(transaction.name,
                         'MONO_/2021/00001')
        self.assertEqual(transaction.note, 'Test transaction')
        self.assertEqual(transaction.payment_ref, 'Test description')
        self.assertEqual(transaction.kw_bank_import_raw_acc, 'UA1234567890')
        self.assertEqual(transaction.kw_bank_import_raw_enterprise_code,
                         '12345678')
        self.assertEqual(transaction.kw_bank_import_raw_description,
                         'Test description')

    def test_monobank_sync_statements(self):
        """Test synchronizing Monobank statements."""
        statements = [{
            'time': 1622505600,
            'currencyCode': 980,
            'operationAmount': 10000,
            'counterIban': 'UA1234567890',
            'counterEdrpou': '12345678',
            'comment': 'Test transaction',
            'description': 'Test description',
            'id': 'test_id'
        }]
        balance_start = 0
        result = self.journal.monobank_sync_statements(statements,
                                                       balance_start)

        # Basic checks
        self.assertIsNotNone(result)
        self.assertIn('01.06.2021', result)

        # Check the balance start
        self.assertEqual(result['01.06.2021']['balance_start'],
                         balance_start)

        # Check the balance end real
        expected_balance_end = balance_start + 100
        self.assertEqual(result['01.06.2021']['balance_end_real'],
                         expected_balance_end)

        # Check the transactions list
        self.assertEqual(len(result['01.06.2021']['transactions']), 1)

        # Check the transaction details
        transaction = result['01.06.2021']['transactions'][0]
        self.assertEqual(transaction['amount'], 100)
        self.assertEqual(transaction['name'],
                         'UA573052990000026002005022255-test_id')
        self.assertEqual(transaction['note'], 'Test transaction')
        self.assertEqual(transaction['payment_ref'], 'Test description')
        self.assertEqual(transaction['kw_bank_import_raw_acc'],
                         'UA1234567890')
        self.assertEqual(transaction['kw_bank_import_raw_enterprise_code'],
                         '12345678')
        self.assertEqual(transaction['kw_bank_import_raw_description'],
                         'Test description')

    def test_monobank_sync_statements_with_invalid_data(self):
        """Test synchronizing Monobank statements with invalid data."""
        statements = [{
            'time': 'invalid_time',
            'currencyCode': 980,
            'operationAmount': 10000,
            'counterIban': 'UA1234567890',
            'counterEdrpou': '12345678',
            'comment': 'Test transaction',
            'description': 'Test description',
            'id': 'test_id'
        }]
        balance_start = 0
        with self.assertRaises(TypeError):
            self.journal.monobank_sync_statements(statements, balance_start)
