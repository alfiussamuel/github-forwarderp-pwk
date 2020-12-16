# coding: utf-8
from datetime import datetime
from openerp import models, api
import time
from dateutil.parser import parse
from odoo.exceptions import UserError
from odoo import models, fields, api

class PwkGenerateRpbWizardLine(models.TransientModel):
    _name = 'pwk.generate.rpb.wizard.line'

    reference = fields.Many2one('pwk.generate.rpb.wizard', 'Reference')
    container_no = fields.Char('Container No.')
    sale_line_ids = fields.Many2many('sale.order.line', 'rpb_wizard_line_sale_line_default_rel',
        'rpb_wizard_line_id', 'sale_line_id', string='Sales Order Lines')
    total_qty = fields.Float(compute="_get_total", string='Total Ordered Qty')

    @api.depends('sale_line_ids.product_id')
    def _get_total(self):
        for res in self:
            total_product = 0

            if res.sale_line_ids:
                for line in res.sale_line_ids:
                    total_product += 1

            res.total_product = total_product


class PwkGenerateRpbWizard(models.TransientModel):
    _name = 'pwk.generate.rpb.wizard'

    line_ids = fields.One2many('pwk.generate.rpb.wizard.line', 'reference', string='Container List')

    @api.multi
    def button_generate(self):    	
    	context = dict(self._context or {})
    	active_id = context.get('active_id', False)
    	rpb_id = self.env['pwk.rpb'].search([('id', '=', active_id)])

    	if self.line_ids:
            for container in self.line_ids:
                container_id = self.env['pwk.rpb.container'].create({
                    'reference': rpb_id.id,
                    'container_no': container.container_no,
                    })

                if container.sale_line_ids:    		
                    for line in container.sale_line_ids:
                        self.env['pwk.rpb.container.line'].create({
                            'reference': container_id.id,
                            'sale_id': line.order_id.id,
                            'sale_line_id': line.id,
                            'total_qty': line.product_uom_qty,
                            'container_qty': line.product_uom_qty                            
                            })                        

                        self.env['pwk.rpb.line'].create({
                            'reference': rpb_id.id,
                            'sale_id': line.order_id.id,
                            'sale_line_id': line.id,
                            'total_qty': line.product_uom_qty,
                            'container_qty': line.product_uom_qty                            
                            })