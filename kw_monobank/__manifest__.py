{
    'name': "MonoBank",

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'category': 'Accounting',
    'license': 'OPL-1',
    'version': '18.0.1.0.17',

    'depends': ['kw_bank_import_base', 'kw_currency_base', 'kw_currency_code'],

    'installable': True,

    'data': [
        'data/ir_cron.xml',
        'views/mono_personal_info.xml',
        'views/account_view.xml',
        'security/ir.model.access.csv',
    ],

    'demo': [
        'demo/test_data.xml',
    ],

    'images': [
        'static/description/icon.png',
        'static/description/cover.png',
    ],

    'price': 140,
    'currency': 'EUR',
}
