# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

{
    'name': 'Stock Ledger Report (PDF/XLS)',
    'version': '1.0',
    'category': 'Generic Modules/Warehouse',
    'summary': 'odoo app Print Stock Ledger report with Product Incoming, Outgoing with PO, Sale Date & Reference',
    'description': """
          odoo app Print Stock Ledger report with Product Incoming, Outgoing with PO, Sale Date & Reference.
        
        Stock Ledger, Inventory Ledger, Incoming Qty Report, Outgoing Qty Report, Ledger, Sale Purchase Detailed Report, 
Stock Ledger Report (PDF/XLS)
Odoo Stock Ledger Report (PDF/XLS)
Stock Ledger report 
Odoo stock Ledger report 
Print stock Ledger report 
Odoo print stock Ledger report 
Stock Ledger report in PDF 
Odoo stock Ledger report in PDF 
Stock Ledger report in xls 
Odoo stock Ledger report in xls
Print stock Ledger report pdf 
Odoo print stock report pdf 
Print stock Ledger report xls 
Odoo print stock Ledger erport xls
Manage stock Ledger 
Odoo manage stock Ledger
Manage stock Ledger report ‘
Odoo manage stock Ledger report
        
        """,
    'author': 'DevIntelle Consulting Service Pvt.Ltd', 
    'website': 'http://www.devintellecs.com/',
    'depends': ['sale_stock','purchase'],
    'data': [
        'wizard/dev_stock_ledger_views.xml',
        'report/stock_ledger_template.xml',
        'report/dev_stock_ledger_menu.xml',
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price':39.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
