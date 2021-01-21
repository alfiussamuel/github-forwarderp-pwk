# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################
import time
from datetime import datetime
from dateutil import relativedelta
import itertools
from operator import itemgetter
import operator

from datetime import datetime, timedelta
from odoo import api, models


class sale_status_report(models.AbstractModel):
    _name = 'report.dev_stock_ledger.stock_ledger_template'


    @api.multi
    def get_warehouse_id(self,data):
        return data
    @api.multi    
    def get_wizard_data(self,data):
        return data

    @api.multi
    def get_formate_date(self,date):
        if date:
            return date.strftime('%d-%m-%Y')
        return ''
    @api.multi
    def get_lines(self,data):
        product_ids = self.get_product_ids(data)
        in_lines = self.in_lines(product_ids,data)
        out_lines = self.out_lines(product_ids,data)
        lst = in_lines + out_lines
        new_lst = sorted(lst, key=itemgetter('date'))
        groups = itertools.groupby(new_lst, key=operator.itemgetter('date'))
        result = [{'date': k, 'values': [x for x in v]} for k, v in groups]
        return result
    
    
    @api.multi
    def get_product_ids(self,data):
        product_pool = self.env['product.product']
        if data.filter_by and data.filter_by == 'product':
            if data.product_ids:
                return data.product_ids.ids
            else:
                product_ids = product_pool.search([])
                return product_ids.ids
        else:
            if data.category_id:
                product_ids = product_pool.search([('type','!=','service'),('categ_id','child_of',data.category_id.id)])
                return product_ids.ids
            else:
                product_ids = product_pool.search([])
                return product_ids.ids
    
    @api.multi
    def in_lines(self,product_ids,data):
        for warehouse_id in data.warehouse_ids:
            state = ('draft', 'cancel', 'done')
            move_type = 'incoming'
            m_type = ''
            if data.location_id:
                m_type = 'and sm.location_dest_id = %s'
            query = """select DATE(sm.date) as in_date, sm.origin as in_origin,pt.name as in_product,\
                      sm.product_uom_qty as in_qty from stock_move as sm \
                      JOIN stock_picking_type as spt ON spt.id = sm.picking_type_id \
                      JOIN product_product as pp ON pp.id = sm.product_id \
                      JOIN product_template as pt ON pp.product_tmpl_id = pt.id \
                      where sm.date >= %s and sm.date <= %s and spt.warehouse_id = %s \
                      and spt.code = %s """ + m_type + """and sm.product_id in %s \
                      and sm.state not in %s
                      """
            if data.location_id:
                params = (data.start_date, data.end_date, warehouse_id.id, move_type, data.location_id.id, tuple(product_ids), state)
            else:
                params = (data.start_date, data.end_date, warehouse_id.id, move_type, tuple(product_ids), state)
            self.env.cr.execute(query, params)
            result = self.env.cr.dictfetchall()
            for res in result:
                res.update({
                    'out_date':'',
                    'out_origin':'',
                    'out_product':'',
                    'out_qty':0.0,
                    'date': res.get('in_date'),
                })
        return result

    @api.multi
    def out_lines(self,product_ids, data):
        for warehouse_id in data.warehouse_ids:
            state = ('draft', 'cancel', 'done')
            move_type = 'outgoing'
            m_type = ''
            
            if data.location_id:
                m_type = 'and sm.location_id = %s'

            query = """select DATE(sm.date) as out_date, sm.origin as out_origin,pt.name as out_product,\
                          sm.product_uom_qty as out_qty from stock_move as sm \
                          JOIN stock_picking_type as spt ON spt.id = sm.picking_type_id \
                          JOIN product_product as pp ON pp.id = sm.product_id \
                          JOIN product_template as pt ON pp.product_tmpl_id = pt.id \
                          where sm.date >= %s and sm.date <= %s and spt.warehouse_id = %s \
                          and spt.code = %s """ + m_type + """and sm.product_id in %s \
                          and sm.state not in %s
                          """

            if data.location_id:
                params = (
                data.start_date, data.end_date, warehouse_id.id, move_type, data.location_id.id, tuple(product_ids),
                state)
            else:
                params = (data.start_date, data.end_date, warehouse_id.id, move_type, tuple(product_ids), state)
            self.env.cr.execute(query, params)
            result = self.env.cr.dictfetchall()
            for res in result:
                res.update({
                    'in_date': '',
                    'in_origin': '',
                    'in_product': '',
                    'in_qty': '',
                    'date':res.get('out_date'),
                })
        return result
    
        

        
        
    @api.multi
    def _get_report_values(self, docids, data=None):
        docs = self.env['dev.stock.ledger'].browse(data['form'])
        
        return {
            'doc_ids': docs.ids,
            'doc_model': 'dev.stock.ledger',
            'docs': docs,
            'proforma': True,
            'get_warehouse_id':self.get_warehouse_id(docs.warehouse_ids),
            'get_lines':self.get_lines(docs),
            'get_wizard_data':self.get_wizard_data(docs),
            'get_formate_date':self.get_formate_date,
        }
        
        
        
        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
