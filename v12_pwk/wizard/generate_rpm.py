# coding: utf-8
from datetime import datetime
from openerp import models, api
import time
from dateutil.parser import parse
from odoo.exceptions import UserError
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class PwkGenerateRpmWizard(models.TransientModel):
    _name = 'pwk.generate.rpm.wizard'

    date_start = fields.Date('Periode')
    date_end = fields.Date('Periode')
    rpb_id = fields.Many2one('pwk.rpb', 'RPB')
    rpb_line_ids = fields.Many2many('pwk.rpb.line', 'rpm_wizard_line_rpb_line_default_rel',
        'rpm_wizard_line_id', 'rpb_line_id', string='RPB Lines')

    @api.multi
    def button_generate(self):    	
    	context = dict(self._context or {})
    	active_id = context.get('active_id', False)
    	rpm_id = self.env['pwk.rpm'].search([('id', '=', active_id)])
        
    	if self.rpb_line_ids:
            rpm_id.write({'rpb_id': self.rpb_id.id})
            for line in self.rpb_line_ids:
                self.env['pwk.rpm.line'].create({
                    'reference': rpm_id.id,
                    'rpb_line_id': line.id,
                    'sale_line_id': line.sale_line_id.id,
                    'sale_id': line.sale_line_id.order_id.id,
                    'total_qty': line.subtotal_qty
                })
