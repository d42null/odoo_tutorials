import logging

_logger = logging.getLogger(__name__)


def migrate(cr, installed_version):

    cr.execute("""
            DELETE FROM ir_ui_view WHERE id IN (
                SELECT res_id
                FROM ir_model_data
                WHERE model = 'ir.ui.view'
                  AND ( module LIKE '%monobank%'
                  OR module LIKE '%mono_bank%' )
            );""")

    cr.execute("""
            DELETE FROM ir_ui_menu WHERE id IN (
                SELECT res_id
                FROM ir_model_data
                WHERE model = 'ir.ui.menu'
                    AND ( module LIKE '%monobank%'
                    OR module LIKE '%mono_bank%' )
            );""")

    cr.execute("""
            DELETE FROM ir_act_window WHERE id IN (
                SELECT res_id
                FROM ir_model_data
                WHERE model = 'ir.actions.act_window'
                    AND ( module LIKE '%monobank%'
                    OR module LIKE '%mono_bank%' )
            );""")

    cr.execute("""
            DELETE FROM ir_model_access
            WHERE name = 'access_kw_monobank_personal_account';
            DELETE FROM ir_model_access
            WHERE name = 'access_kw_currency_rate_provider_monobank';
        """)

    cr.execute("""
            DELETE FROM ir_module_module
            WHERE name = 'kw_bank_import_monobank';
            DELETE FROM ir_module_module
            WHERE name = 'kw_currency_monobank';
            DELETE FROM ir_module_module
            WHERE name = 'kw_mono_bank_personal';
        """)

    cr.execute("""
            DELETE FROM ir_model_data WHERE module LIKE '%monobank%'
            OR module LIKE '%mono_bank%';
        """)

    cr.commit()
