# coding: utf-8
from datetime import datetime
from openerp import models, api
import time
from dateutil.parser import parse
from odoo.exceptions import UserError
from odoo import models, fields, api, _

class PwkGenerateRpbWizardLine(models.TransientModel):
    _name = 'pwk.generate.rpb.wizard.line'

    reference = fields.Many2one('pwk.generate.rpb.wizard', 'Reference')
    no_container = fields.Char('No. Container')
    jumlah_container = fields.Integer('Jumlah Container')
    sale_line_ids = fields.Many2many('sale.order.line', 'rpb_wizard_line_sale_line_default_rel',
        'rpb_wizard_line_id', 'sale_line_id', string='Sales Order Lines')
    total_product = fields.Float(compute="_get_total", string='Total Product')

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
                existing_container = self.env['pwk.rpb.container'].search([
                    ('name', '=', container.no_container),
                    ('reference', '=', self.id)
                ])

                if existing_container:
                    raise UserError(_('Nomor Container sudah'))

                container_id = self.env['pwk.rpb.container'].create({
                    'reference': rpb_id.id,
                    'no_container': container.no_container,
                    'jumlah_container': container.jumlah_container,
                    'name': container.no_container,
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

                        rpb_line = self.env['pwk.rpb.line'].create({
                            'reference': rpb_id.id,
                            'container_id': container_id.id,
                            'jumlah_container': container_id.jumlah_container,
                            'sale_id': line.order_id.id,
                            'sale_line_id': line.id,
                            'total_qty': line.product_uom_qty,
                            'container_qty': line.product_uom_qty,
                            'outstanding_order_pcs': line.outstanding_order_pcs
                            })

                        rpb_line.button_reload_bom()