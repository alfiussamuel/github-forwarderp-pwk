# coding: utf-8
from datetime import datetime, timedelta
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
                    'container_no': line.container_id.name,
                    'rpb_line_id': line.id,
                    'rpb_id': line.reference.id,
                    'sale_line_id': line.sale_line_id.id,
                    'sale_id': line.sale_line_id.order_id.id,
                    'total_qty': line.subtotal_qty
                })

                if rpm_line_id:
                    # Create Detail Date for P1 and P2
                    date_start = rpm_id.date_start

                    while date_start <= rpm_id.date_end:
                        self.env['pwk.rpm.line.date'].create({
                            'reference': rpm_line_id.id,
                            'date': date_start
                        })

                        date_start = date_start + timedelta(days = 1)

                    # Check existing RPM Container and Fill Container
                    rpm_container_id = self.env['pwk.rpm.container'].search([
                        ('name', '=', line.container_id.name),
                        ('reference', '=', rpm_id.id)
                    ])

                    if not rpm_container_id:
                        rpm_container_id = self.env['pwk.rpm.container'].create({
                            'reference': rpm_id.id,
                            'name': line.container_id.name,
                            })

                    self.env['pwk.rpm.container.line'].create({
                        'reference': rpm_container_id.id,
                        'sale_id': line.sale_id.id,
                        'sale_line_id': line.sale_line_id.id,
                        'container_qty': line.total_qty,
                        'rpm_line_id': rpm_line_id.id
                        })


                    # Fill Bill of Material from RPB
                    if line.is_detail1 and line.is_selected_detail1:
                        for bom in line.detail_ids_1:
                            self.env['pwk.rpm.line.detail1'].create({
                                'reference': rpm_line_id.id,
                                'product_id': bom.product_id.id,
                                'thick': bom.thick,
                                'width': bom.width,
                                'length': bom.length,
                                'ply': bom.ply,
                                'quantity': bom.quantity,
                            })

                            rpm_line_id.write({
                                'is_detail1': True,
                                'is_selected_detail1': True,
                            })

                    elif line.is_detail2 and line.is_selected_detail2:
                        for bom in line.detail_ids_2:
                            self.env['pwk.rpm.line.detail2'].create({
                                'reference': rpm_line_id.id,
                                'product_id': bom.product_id.id,
                                'thick': bom.thick,
                                'width': bom.width,
                                'length': bom.length,
                                'ply': bom.ply,
                                'quantity': bom.quantity,
                            })

                            rpm_line_id.write({
                                'is_detail2': True,
                                'is_selected_detail2': True,
                            })

                    elif line.is_detail3 and line.is_selected_detail3:
                        for bom in line.detail_ids_3:
                            self.env['pwk.rpm.line.detail3'].create({
                                'reference': rpm_line_id.id,
                                'product_id': bom.product_id.id,
                                'thick': bom.thick,
                                'width': bom.width,
                                'length': bom.length,
                                'ply': bom.ply,
                                'quantity': bom.quantity,
                            })

                            rpm_line_id.write({
                                'is_detail3': True,
                                'is_selected_detail3': True,
                            })

                    elif line.is_detail4 and line.is_selected_detail4:
                        for bom in line.detail_ids_4:
                            self.env['pwk.rpm.line.detail4'].create({
                                'reference': rpm_line_id.id,
                                'product_id': bom.product_id.id,
                                'thick': bom.thick,
                                'width': bom.width,
                                'length': bom.length,
                                'ply': bom.ply,
                                'quantity': bom.quantity,
                            })

                            rpm_line_id.write({
                                'is_detail4': True,
                                'is_selected_detail4': True,
                            })

                    elif line.is_detail5 and line.is_selected_detail5:
                        for bom in line.detail_ids_5:
                            self.env['pwk.rpm.line.detail5'].create({
                                'reference': rpm_line_id.id,
                                'product_id': bom.product_id.id,
                                'thick': bom.thick,
                                'width': bom.width,
                                'length': bom.length,
                                'ply': bom.ply,
                                'quantity': bom.quantity,
                            })

                            rpm_line_id.write({
                                'is_detail5': True,
                                'is_selected_detail5': True,
                            })