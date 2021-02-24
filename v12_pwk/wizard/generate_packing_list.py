# coding: utf-8
from datetime import datetime
from openerp import models, api
import time
from dateutil.parser import parse
from odoo.exceptions import UserError
from odoo import models, fields, api, _


class PwkGeneratePackingListWizard(models.TransientModel):
    _name = 'pwk.generate.packing.list.wizard'

    sale_line_ids = fields.Many2many('sale.order.line', 'packing_list_wizard_line_sale_line_default_rel',
        'packing_list_wizard_line_id', 'sale_line_id', string='Sales Order Lines')

    @api.multi
    def button_generate(self):    	
    	context = dict(self._context or {})
    	active_id = context.get('active_id', False)
    	packing_list_id = self.env['pwk.packing.list'].search([('id', '=', active_id)])

    	if self.sale_line_ids:
            bom_list = ''

            for line in self.sale_line_ids:
                packing_list_line_id = self.env['pwk.packing.list.line'].create({
                    'reference': packing_list_id.id,
                    'product_id': line.product_id.id,
                    'quantity': line.product_uom_qty,
                    'sale_line_id': line.id,
                    'sale_id': line.order_id.id,
                    'crate_number': line.crate_number,
                    'crate_qty_each': line.crate_qty_each
                })

                rpb_line_ids = self.env['pwk.rpb.line'].search([
                    ('sale_line_id', '=', line.id),
                ])

                if rpb_line_ids:
                    if rpb_line_ids[0].is_selected_detail1 and rpb_line_ids[0].detail_ids_1:
                        bom_list = rpb_line_ids[0].detail_ids_1
                    elif rpb_line_ids[0].is_selected_detail2 and rpb_line_ids[0].detail_ids_2:
                        bom_list = rpb_line_ids[0].detail_ids_2
                    elif rpb_line_ids[0].is_selected_detail3 and rpb_line_ids[0].detail_ids_3:
                        bom_list = rpb_line_ids[0].detail_ids_3
                    elif rpb_line_ids[0].is_selected_detail4 and rpb_line_ids[0].detail_ids_4:
                        bom_list = rpb_line_ids[0].detail_ids_4
                    elif rpb_line_ids[0].is_selected_detail5 and rpb_line_ids[0].detail_ids_5:
                        bom_list = rpb_line_ids[0].detail_ids_5

                    for bom_line in bom_list:                        
                        self.env['pwk.packing.list.line.bom'].create({
                            'reference': line.id,
                            'product_id': bom_line.product_id.id,
                            'thick': bom_line.product_id.tebal,
                            'width': bom_line.product_id.lebar,
                            'length': bom_line.product_id.panjang,
                            'quantity': bom_line.product_qty * line.product_uom_qty,
                            'ply': bom_line.ply,
                            'notes': bom_line.notes
                        })

                else:
                    bom_list = self.env['mrp.bom'].search([
                        ('product_tmpl_id.name', '=', line.product_id.name)
                    ])

                    for bom_line in bom_list:                        
                        self.env['pwk.packing.list.line.bom'].create({
                            'reference': line.id,
                            'product_id': bom_line.product_id.id,
                            'thick': bom_line.product_id.tebal,
                            'width': bom_line.product_id.lebar,
                            'length': bom_line.product_id.panjang,
                            'quantity': bom_line.product_qty * line.product_uom_qty,
                        }