# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Product Cost Price History',
    'version': '12.0',
    'category': 'Purchases',
    'author': 'Business Solution Consulting',
    'description': """
      Add a products cost price history list and graph view
    """,
    'website': 'http://auriumtechnologies.com',
    'depends': ['purchase','abs_hide_sale_cost_price'],
    'data': [
        'views/product_price_history_view.xml', 
    ],
    'images':['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
