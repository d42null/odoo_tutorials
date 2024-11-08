# -*- coding: utf-8 -*-
{
    'name': "RealEstate",

    'summary': """
        RealEstate
    """,

    'description': """
        RealEstate
    """,

    'author': "Odoo",
    'website': "https://www.odoo.com/",
    'category': 'Tutorials/RealEstate',
    'version': '0.1',
    'application': True,
    'installable': True,
    'depends': ['base'],

    'data': [
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
        'security/ir.model.access.csv',],
    # 'assets': {
    #     'web.assets_backend': [
    #         'awesome_clicker/static/src/**/*',
    #     ],

    # },
    'license': 'AGPL-3'
}
