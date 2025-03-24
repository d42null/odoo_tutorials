import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class CurrencyRateUpdateService(models.Model):
    _name = "kw.currency.rate.update.service"
    _inherit = ["mail.thread"]
    _description = "Currency Rate Update"
    _sql_constraints = [
        (
            "curr_service_unique",
            "unique (rate_provider, company_id)",
            "You can use a service only one time per company !",
        )
    ]

    rate_provider = fields.Selection(
        selection=[],
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.user.company_id,
    )

    @api.model
    def _run_currency_update(self):
        _logger.info("Starting the currency rate update cron")
        self.search([]).refresh_currency()
        _logger.info("End of the currency rate update cron")

    def refresh_currency(self):
        for srv in self:
            provider_obj = self.env[srv.rate_provider]
            for cur in self.env["res.currency"].search(
                [
                    ("active", "=", True),
                ]
            ):
                if srv.company_id.currency_id.id == cur.id:
                    continue
                provider = provider_obj.create(
                    {
                        "date": fields.Date.today(),
                        "currency": cur.name,
                    }
                )
                rate = provider.get_currency_rate()
                if rate:
                    rates = self.env["res.currency.rate"].search(
                        [
                            ("currency_id", "=", cur.id),
                            ("company_id", "=", srv.company_id.id),
                            ("name", "=", fields.Date.today()),
                        ]
                    )
                    if not rates:
                        self.env["res.currency.rate"].create(
                            {
                                "currency_id": cur.id,
                                "rate": rate,
                                "name": fields.Date.today(),
                                "company_id": srv.company_id.id,
                            }
                        )
                    else:
                        rates.rate = rate
