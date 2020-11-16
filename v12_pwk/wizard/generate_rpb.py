# coding: utf-8
from datetime import datetime
from openerp import models, api
import time
from dateutil.parser import parse
from odoo.exceptions import UserError
from odoo import models, fields, api

class PwkGenerateRpbWizard(models.TransientModel):
    _name = 'pwk.generate.rpb.wizard'

    sale_ids = fields.Many2many('sale.order', 'rpb_sale_default_rel',
        'rpb_id', 'sale_id', string='Sales Orders')

    @api.multi
    def button_generate(self):    	
    	context = dict(self._context or {})
    	active_id = context.get('active_id', False)
    	rpb_id = self.env['pwk.rpb'].search([('id', '=', active_id)])

    	if self.sale_ids:
    		for sale in self.sale_ids:
    			for line in sale.order_line:
	    			self.env['pwk.rpb.line'].create({
	    				'reference': rpb_id.id,
	    				'sale_id': sale.id,
	    				'sale_line_id': line.id
	    				})

    	return True
        # context = dict(self._context or {})
        # active_id = context.get('active_id', False)
        # print ("active ID ", active_id)
        # context = dict(self._context or {})
        # print ("Context ", self.env.context)
        # self.model = self.env.context.get('res_model')

        # docs = self.env[self.model].browse(self.env.context.get('active_id'))
        # print ("Docs ", docs)
        # print ("Model ", self.model)