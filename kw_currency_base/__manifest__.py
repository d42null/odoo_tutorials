{
    'name': 'Currency exchange rates import',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'category': 'Accounting',
    'license': 'OPL-1',
    'version': '18.0.1.0.5',

    'depends': ['account', ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/rate_update_service_view.xml',
    ],

    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
    ],

    'price': 0,
    'currency': 'EUR',

    'live_test_url': 'https://kw-currency-nbu.demo13.kitworks.systems',
}
