from unittest.mock import patch
from odoo.tests.common import TransactionCase
from odoo import fields


class TestCurrencyRateUpdateService(TransactionCase):

    def setUp(self):
        super().setUp()

        # Create a currency rate update service
        self.currency_update_service = self.env[
            'kw.currency.rate.update.service'
        ].create({
            'rate_provider': 'kw.currency.rate.provider.monobank',
            'company_id': self.env.user.company_id.id,
        })

        # Create a test currency
        self.currency = self.env['res.currency'].create({
            'name': 'TES',
            'symbol': 'T',
            'kw_currency_code': '980',
            'active': True,
            'rounding': 0.01,
            'position': 'after',
        })

        # Create a currency rate provider
        self.currency_rate_provider = self.env[
            'kw.currency.rate.provider.monobank'
        ].create({
            'date': fields.Date.today(),
        })

    @patch(
        'odoo.addons.kw_monobank.models.exchange_provider.'
        'CurrencyRateProvider.get_currency_rate'
    )
    def test_refresh_currency(self, mock_get_currency_rate):
        """Test refreshing currency with valid API data."""

        # Mock API response
        mock_get_currency_rate.return_value = [
            {'currencyCodeA': 980, 'currencyCodeB': 840, 'rateCross': 27.5}
        ]

        # Refresh currency rates
        self.currency_update_service.refresh_currency()

        # Search for updated currency rates
        currency_rates = self.env['res.currency.rate'].search([
            ('currency_id', '=', self.currency.id),
            ('company_id', '=', self.env.user.company_id.id),
            ('name', '=', fields.Date.today())
        ])

        # Assertions
        self.assertTrue(currency_rates, "Currency rates should be updated.")
        self.assertEqual(
            len(currency_rates), 1,
            "There should be exactly one currency rate record."
        )
        for rate in currency_rates:
            self.assertGreater(
                rate.rate, 0, "Currency rate should be greater than 0."
            )
            self.assertEqual(
                rate.rate, 27.5, "Currency rate should be 27.5."
            )
            self.assertEqual(
                rate.currency_id.id, self.currency.id,
                "Currency ID should match the created currency."
            )
            self.assertEqual(
                rate.company_id.id, self.env.user.company_id.id,
                "Company ID should match the user's company."
            )

    @patch(
        'odoo.addons.kw_monobank.models.exchange_provider.'
        'CurrencyRateProvider.get_currency_rate'
    )
    def test_refresh_currency_with_no_data(self, mock_get_currency_rate):
        """Test refreshing currency when API returns no data."""

        # Mock API response with no data
        mock_get_currency_rate.return_value = []

        # Refresh currency rates
        self.currency_update_service.refresh_currency()

        # Search for updated currency rates
        currency_rates = self.env['res.currency.rate'].search([
            ('currency_id', '=', self.currency.id),
            ('company_id', '=', self.env.user.company_id.id),
            ('name', '=', fields.Date.today())
        ])

        # Assertions
        self.assertFalse(
            currency_rates, "Currency rates should not be updated "
            "when no data is returned."
        )
