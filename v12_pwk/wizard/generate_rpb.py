# coding: utf-8
from datetime import datetime
from openerp import models, api
import time
from dateutil.parser import parse
from odoo.exceptions import UserError
from odoo import models, fields, api

class PwkGenerateRpbWizard(models.TransientModel):
    _name = 'pwk.generate.rpb.wizard'

    sale_line_ids = fields.Many2many('sale.order.line', 'rpb_sale_line_default_rel',
        'rpb_id', 'sale_line_id', string='Sales Orders')

    @api.multi
    def button_generate(self):    	
    	context = dict(self._context or {})
    	active_id = context.get('active_id', False)
    	rpb_id = self.env['pwk.rpb'].search([('id', '=', active_id)])

    	if self.sale_ids:
    		for line in self.sale_line_ids:
    			self.env['pwk.rpb.line'].create({
    				'reference': rpb_id.id,
    				'sale_id': line.order_id.id,
    				'sale_line_id': line.id
    				})

    	return True