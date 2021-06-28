# -*- coding: utf-8 -*-
{
    'name': "BSC - forwardERP - Beacukai Mixin",
    'description': """
        This is work around to fix error inheriting when abstract model
    """,
    'author': "BSC",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'product', 'v10_bsc_beacukai'],
    'data': [
        'views/product_views.xml'
    ],
}
