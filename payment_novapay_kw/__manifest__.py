{
    'name': 'Payment NovaPay',
    'version': '18.0.1.2.1',
    'category': 'Customizations',
    'sequence': -100,
    'summary': 'Payment NovaPay System',
    'author': "Tymur",

    'depends': [
        'payment',
        'kw_payment_base'
    ],

    'external_dependencies': {
        'python': ['phonenumbers']
    },

    'data': [
        'views/payment_novapay_templates.xml',
        'views/payment_provider_views.xml',
        'views/payment_transaction_views.xml',

        'data/payment_provider_data.xml',
    ],

    # 'post_init_hook': 'post_init_hook',
    # 'uninstall_hook': 'uninstall_hook',

    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
