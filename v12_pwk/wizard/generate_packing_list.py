# coding: utf-8
from datetime import datetime
from openerp import models, api
import time
from dateutil.parser import parse
from odoo.exceptions import UserError
from odoo import models, fields, api, _


class PwkGeneratePackingListWizard(models.TransientModel):
    _name = 'pwk.generate.packing.list.wizard'

    line_ids = fields.One2many('pwk.generate.packing.list.wizard.line', 'reference', string='List')
    sale_line_ids = fields.Many2many('sale.order.line', 'packing_list_wizard_line_sale_line_default_rel',
        'packing_list_wizard_line_id', 'sale_line_id', string='Sales Order Lines')

    @api.multi
    def button_generate(self):    	
    	context = dict(self._context or {})
    	active_id = context.get('active_id', False)
    	packing_list_id = self.env['pwk.packing.list'].search([('id', '=', active_id)])

    	if self.sale_line_ids:
            for line in self.sale_line_ids:
                self.env['pwk.packing.list.line'].create({
                    'reference': packing_list_id.id,
                    'product_id': line.product_id.id,
                    'quantity': line.product_uom_qty
                })
