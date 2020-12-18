# coding: utf-8
from datetime import datetime
from openerp import models, api
import time
from dateutil.parser import parse
from odoo.exceptions import UserError
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class PwkGenerateRpmWizardLine(models.TransientModel):
    _name = 'pwk.generate.rpm.wizard.line'

    reference = fields.Many2one('pwk.generate.rpm.wizard', 'Reference')
    sale_line_id = fields.Many2one('sale.order.line', 'No. Order Line')
    product_id = fields.Many2one('product.product', string='Product')
    thick = fields.Float(string='Thick')
    width = fields.Float(string='Width')
    length = fields.Float(string='Length')
    glue_id = fields.Many2one('pwk.glue', string='Glue')
    grade_id = fields.Many2one('pwk.grade', string='Grade')                
    remaining_qty = fields.Float(string='Qty Remaining')
    remaining_volume = fields.Float(string='Vol Remaining')
    total_qty = fields.Float(string='Qty RPM')
    total_volume = fields.Float(compute="_get_vol", string='Vol RPM', digits=dp.get_precision('FourDecimal'))

    @api.depends('total_qty')
    def _get_volume(self):
        for res in self:
            res.total_volume = res.total_qty * res.thick * res.width * res.length / 1000000000

class PwkGenerateRpmWizard(models.TransientModel):
    _name = 'pwk.generate.rpm.wizard'

    line_ids = fields.One2many('pwk.generate.rpm.wizard.line', 'reference', string='List')
    date_start = fields.Date('Periode')
    date_end = fields.Date('Periode')

    @api.multi
    def button_reload(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        rpb_id = self.env['pwk.rpb'].search([('id', '=', active_id)])
        
        if self.line_ids:
            for current_line in self.line_ids:
                current_line.unlink()

        if rpb_id.line_ids:
            for line in rpb_id.line_ids:
                self.env['pwk.generate.rpm.wizard.line'].create({
                    'sale_line_id': line.sale_line_id.id,
                    'product_id': line.product_id.id,
                    'thick': line.thick,
                    'width': line.width,
                    'length': line.length,
                    'glue_id': line.glue_id.id,
                    'grade_id': line.grade_id.id,
                    'remaining_qty': line.remaining_qty,
                    'remaining_volume': line.remaining_volume,
                })


    @api.multi
    def button_generate(self):    	
    	context = dict(self._context or {})
    	active_id = context.get('active_id', False)
    	rpb_id = self.env['pwk.rpb'].search([('id', '=', active_id)])

    	if self.line_ids:
            rpm_id = self.env['pwk.rpm'].create({
                'rpb_id': rpb_id.id,
                'date_start': self.date_start,
                'date_end': self.date_end,                    
            })

            for line in self.line_ids:
                self.env['pwk.rpm.line'].create({
                    'reference': rpm_id.id,
                    'sale_line_id': line.sale_line_id.id,
                    'sale_id': line.sale_line_id.order_id.id,
                    'total_qty': line.total_qty
                })
