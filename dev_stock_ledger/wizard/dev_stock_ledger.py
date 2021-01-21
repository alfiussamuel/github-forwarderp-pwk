# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from io import BytesIO
from datetime import datetime
from openerp import models, fields, api, _
import xlwt
from xlwt import easyxf
import base64
import itertools
from operator import itemgetter
import operator




class dev_stock_ledger(models.TransientModel):
    _name = "dev.stock.ledger"

    warehouse_ids = fields.Many2many('stock.warehouse',string='Warehouse',required="1")
    location_id = fields.Many2one('stock.location',string='Location', domain="[('usage','!=','view')]")
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    
    filter_by = fields.Selection([('product','Product'),('category','Product Category')],string='Filter By', default='product')
    
    category_id = fields.Many2one('product.category',string='Category')
    product_ids = fields.Many2many('product.product',string='Products')


#    @api.multi
#    def print_pdf(self):
#        return self.env['report'].get_action(self, 'dev_stock_ledger.stock_ledger_template')
        
    @api.multi
    def print_pdf(self):
        data = self.read()
        datas = {
            'form': self.id
        }
        return self.env.ref('dev_stock_ledger.print_dev_stock_ledger').report_action(self, data=datas)


    @api.multi
    def get_product_ids(self):
        product_pool = self.env['product.product']
        if self.filter_by and self.filter_by == 'product':
            if self.product_ids:
                return self.product_ids.ids
            else:
                product_ids = product_pool.search([])
                return product_ids.ids
        else:
            if self.category_id:
                product_ids = product_pool.search([('type','!=','service'),('categ_id','child_of',self.category_id.id)])
                return product_ids.ids
            else:
                product_ids = product_pool.search([])
                return product_ids.ids

    @api.multi
    def in_lines(self,product_ids,warehouse_id):
        state = ('draft', 'cancel', 'done')
        move_type = 'incoming'
        m_type = ''
        if self.location_id:
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

        if self.location_id:
            params = (self.start_date, self.end_date, warehouse_id.id, move_type, self.location_id.id, tuple(product_ids), state)
        else:
            params = (self.start_date, self.end_date, warehouse_id.id, move_type, tuple(product_ids), state)

        print ("=======",params)
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
    def out_lines(self, product_ids,warehouse_id):
        state = ('draft', 'cancel', 'done')
        move_type = 'outgoing'
        m_type = ''
        if self.location_id:
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

        if self.location_id:
            params = (
            self.start_date, self.end_date, warehouse_id.id, move_type, self.location_id.id, tuple(product_ids),
            state)
        else:
            params = (self.start_date, self.end_date, warehouse_id.id, move_type, tuple(product_ids), state)

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
    def get_lines(self,warehouse_id):
        product_ids = self.get_product_ids()
        in_lines = self.in_lines(product_ids,warehouse_id)
        out_lines = self.out_lines(product_ids,warehouse_id)
        lst = in_lines + out_lines
        new_lst = sorted(lst, key=itemgetter('date'))
        groups = itertools.groupby(new_lst, key=operator.itemgetter('date'))
        result = [{'date': k, 'values': [x for x in v]} for k, v in groups]
        return result


    @api.multi
    def export_stock_ledger(self):
        workbook = xlwt.Workbook()
        filename = 'Stock Ledger.xls'
        # Style
        main_header_style = easyxf('font:height 400;pattern: pattern solid, fore_color gray25;'
                                   'align: horiz center;font: color black; font:bold True;'
                                   "borders: top thin,left thin,right thin,bottom thin")

        header_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                              'align: horiz center;font: color black; font:bold True;'
                              "borders: top thin,left thin,right thin,bottom thin")

        in_header_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                                 'align: horiz center;font: color black; font:bold True;'
                                 "borders: top thin,left thin,right thin,bottom thin")

        out_header_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray40;'
                                  'align: horiz center;font: color black; font:bold True;'
                                  "borders: top thin,left thin,right thin,bottom thin")

        text_left = easyxf('font:height 150; align: horiz left;' "borders: top thin,bottom thin")
        text_left_bold = easyxf('font:height 200; align: horiz left;font:bold True;' "borders: top thin,bottom thin")
        text_center = easyxf('font:height 150; align: horiz center;' "borders: top thin,bottom thin")
        text_right = easyxf('font:height 150; align: horiz right;' "borders: top thin,bottom thin",
                            num_format_str='0.00')

        worksheet = []
        for l in range(0, len(self.warehouse_ids)):
            worksheet.append(l)
        work=0
        for warehouse_id in self.warehouse_ids:
            worksheet[work] = workbook.add_sheet(warehouse_id.name)
            for i in range(0, 9):
                if i in [2,6]:
                    worksheet[work].col(i).width = 320 * 30
                else:
                    worksheet[work].col(i).width = 130 * 30

            worksheet[work].write_merge(0, 1, 0, 7, 'STOCK LEDGER', main_header_style)

            tags = ['Date', 'Origin', 'Product', 'Qty', 'Date','Origin', 'Product', 'Qty']

            worksheet[work].write_merge(7, 7, 0, 3, 'INCOMMING', in_header_style)
            worksheet[work].write_merge(7, 7, 4, 7, 'OUTGOING', out_header_style)

            c=0
            r = 8
            for tag in tags:
                if c <= 3:
                    worksheet[work].write(r, c, tag, in_header_style)
                else:
                    worksheet[work].write(r, c, tag, out_header_style)
                c+=1

            in_qty = 0
            out_qty = 0

            lines = self.get_lines(warehouse_id)
            r+=1
            for line in lines:
                for val in line.get('values'):
                    if val.get('in_date'):
                        date = val.get('in_date').strftime("%d-%m-%Y")
                        worksheet[work].write(r, 0, date, text_center)
                    else:
                        worksheet[work].write(r, 0, '', text_center)

                    worksheet[work].write(r, 1, val.get('in_origin'), text_center)
                    worksheet[work].write(r, 2, val.get('in_product'), text_left)

                    if val.get('in_qty'):
                        in_qty += val.get('in_qty')
                        worksheet[work].write(r, 3, val.get('in_qty'), text_right)
                    else:
                        worksheet[work].write(r, 3, '', text_center)

                    if val.get('out_date'):
                        date = val.get('out_date').strftime("%d-%m-%Y")
                        worksheet[work].write(r, 4, date, text_center)
                    else:
                        worksheet[work].write(r, 4, '', text_center)

                    worksheet[work].write(r, 5, val.get('out_origin'), text_center)
                    worksheet[work].write(r, 6, val.get('out_product'), text_left)

                    if val.get('out_qty'):
                        out_qty += val.get('out_qty')
                        worksheet[work].write(r, 7, val.get('out_qty'), text_right)
                    else:
                        worksheet[work].write(r, 7, '', text_left)
                    r+=1

            worksheet[work].write(4, 0, 'Warehouse', header_style)
            worksheet[work].write(4, 1, 'Location', header_style)
            worksheet[work].write(4, 2, 'Date', header_style)
            worksheet[work].write(4, 3, 'In Qty', header_style)
            worksheet[work].write(4, 4, 'Out Qty', header_style)

            worksheet[work].write(5, 0, warehouse_id.name, text_center)
            worksheet[work].write(5, 1, self.location_id.name or '', text_center)
            s_date =''
            if self.start_date:
                s_date = self.start_date.strftime("%d-%m-%Y")
            e_date = ''
            if self.end_date:
                e_date = self.end_date.strftime("%d-%m-%Y")
            date = s_date + ' TO '+ e_date
            worksheet[work].write(5, 2, date, text_center)
            worksheet[work].write(5, 3, in_qty, text_right)
            worksheet[work].write(5, 4, out_qty, text_right)
            work+=1





        fp = BytesIO()
        workbook.save(fp)
        export_id = self.env['dev.stock.ledger.excel'].create(
            {'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        fp.close()

        return {
            'view_mode': 'form',
            'res_id': export_id.id,
            'res_model': 'dev.stock.ledger.excel',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }



class dev_stock_ledger_excel(models.TransientModel):
    _name = "dev.stock.ledger.excel"

    excel_file = fields.Binary('Excel Report')
    file_name = fields.Char('Excel File')

