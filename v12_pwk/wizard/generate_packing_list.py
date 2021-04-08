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
            container_no = 1

            for line in self.sale_line_ids:
                container_start = container_no
                container_end = container_no - 1
                container_start_end = ''
                crate_qty_each = 1

                if line.crate_qty_each > 0:
                    crate_qty_each = line.crate_qty_each

                packing_list_line_id = self.env['pwk.packing.list.line'].create({
                    'reference': packing_list_id.id,
                    'product_id': line.product_id.id,
                    'sale_line_id': line.id,
                    'sale_id': line.order_id.id,
                    'crate_number': (line.qty_packing_list / crate_qty_each),
                    'crate_qty_each': crate_qty_each
                })

                # Create Container Detail for each Packing List Line
                for container in line.container_ids:
                    self.env['pwk.packing.list.line.container'].create({
                        'reference': packing_list_line_id.id,
                        'position_id': container.position_id.id,
                        'pallet_id': container.pallet_id.id,
                        'strapping_id': container.strapping_id.id,    
                        'qty': container.qty,
                        'number': container.number,
                    })

                    container_end += 1
                    container_no += 1

                if container_start < 10 and container_end < 10:
                    container_start_end = '0' + str(container_start) + ' - ' + '0' + str(container_end)
                elif container_start > 10 and container_end < 10:
                    container_start_end = str(container_start) + ' - ' + '0' + str(container_end)
                elif container_start < 10 and container_end > 10:
                    container_start_end = '0' + str(container_start) + ' - ' + str(container_end)
                elif container_start > 10 and container_end > 10:
                    container_start_end = str(container_start) + ' - ' + str(container_end)

                packing_list_line_id.write({'container_start_end': container_start_end})

                # Create Groups for Printing
                existing_group_id = self.env['pwk.packing.list.group'].search([
                    ('reference', '=', packing_list_id.id),
                    # ('product_id', '=', line.product_id.id),
                    ('jenis_kayu_id', '=', line.product_id.jenis_kayu.id)
                ])

                if not existing_group_id:
                    self.env['pwk.packing.list.group'].create({
                        'reference': packing_list_id.id,
                        'product_id': line.product_id.id,
                        'jenis_kayu_id': line.product_id.jenis_kayu.id
                    })

                rpb_line_ids = self.env['pwk.rpb.line'].search([('sale_line_id', '=', line.id)])

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
                        self.env['pwk.packing.list.line.detail'].create({
                            'reference': packing_list_line_id.id,
                            'product_id': bom_line.product_id.id,
                            'thick': bom_line.product_id.tebal,
                            'width': bom_line.product_id.lebar,
                            'length': bom_line.product_id.panjang,
                            'quantity': bom_line.quantity * line.qty_packing_list,
                            'ply': bom_line.ply,
                        })

                else:
                    bom_list = self.env['mrp.bom'].search([
                        ('product_tmpl_id.name', '=', line.product_id.name)
                    ])

                    for bom_line in bom_list.bom_line_ids:                        
                        self.env['pwk.packing.list.line.detail'].create({
                            'reference': packing_list_line_id.id,
                            'product_id': bom_line.product_id.id,
                            'thick': bom_line.product_id.tebal,
                            'width': bom_line.product_id.lebar,
                            'length': bom_line.product_id.panjang,
                            'quantity': bom_line.product_qty * line.qty_packing_list,
                            'ply': bom_line.product_qty
                        })
