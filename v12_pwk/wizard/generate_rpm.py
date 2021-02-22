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
                rpm_line_id = self.env['pwk.rpm.line'].create({
                    'reference': rpm_id.id,
                    'rpb_line_id': line.id,
                    'rpb_id': line.reference.id,
                    'sale_line_id': line.sale_line_id.id,
                    'sale_id': line.sale_line_id.order_id.id,
                    'total_qty': line.subtotal_qty
                })

                if rpm_line_id:
                    model_detail = ''
                    list_detail = ''

                    if line.is_detail1:
                        model_detail = self.env['pwk.rpm.line.detail1']
                        list_detail = line.detail_ids_1
                    elif line.is_detail2:
                        model_detail = self.env['pwk.rpm.line.detail2']
                        list_detail = line.detail_ids_2
                    elif line.is_detail3:
                        model_detail = self.env['pwk.rpm.line.detail3']
                        list_detail = line.detail_ids_3
                    elif line.is_detail4:
                        model_detail = self.env['pwk.rpm.line.detail4']
                        list_detail = line.detail_ids_4
                    elif line.is_detail5:
                        model_detail = self.env['pwk.rpm.line.detail5']
                        list_detail = line.detail_ids_5

                    if model_detail and list_detail:
                        for bom in list_detail:
                            model_detail.create({
                                'reference': rpm_line_id.id,
                                'product_id': bom.product_id.id,
                                'thick': bom.thick,
                                'width': bom.width,
                                'length': bom.length,
                                'ply': bom.ply,
                                'quantity': bom.quantity,
                            })


