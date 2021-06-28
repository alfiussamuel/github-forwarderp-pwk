# -*- coding: utf-8 -*-
{
    'name': 'BSC - forwardERP - COM',
    'version': '10',
    'category': 'Custom',
    'author': 'BSC',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'purchase', 'stock', 'v10_bsc_beacukai'],

    # always loaded
    'data': [
        'data/account.account.csv',
        'security/security.xml',
        'views/purchase_view.xml',
        'views/stock_picking_view.xml',
        'views/beacukai_config_views.xml',
        'views/excel_laporan_mutasi_view.xml',
        'report/layout_template.xml',
        'report/purchase_order_template.xml',
        'report/purchase_report.xml',
        'views/menu.xml',
    ],

}
