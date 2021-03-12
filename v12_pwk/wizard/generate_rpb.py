# coding: utf-8
from datetime import datetime
from openerp import models, api
import time
from dateutil.parser import parse
from odoo.exceptions import UserError
from odoo import models, fields, api, _

class PwkGenerateRpbWizardLine(models.TransientModel):
    _name = 'pwk.generate.rpb.wizard.line'

    @api.model
    def _default_nomor_container(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        rpb_id = self.env['pwk.rpb'].search([('id', '=', active_id)])

        print("RPB ", rpb_id.name)
        return int(self.reference.nomor_container) + 1
        
    reference = fields.Many2one('pwk.generate.rpb.wizard', 'Reference')
    no_container = fields.Char('No. Container', default=_default_nomor_container)
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

    @api.model
    def _default_nomor_container(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        rpb_id = self.env['pwk.rpb'].search([('id', '=', active_id)])

        previous_ids = self.env['pwk.rpb.line'].search([
            ('reference', '=', rpb_id.id),
        ], order='id desc')

        if previous_ids:
            return previous_ids[0].container_id.name
        else:
            return 0

    line_ids = fields.One2many('pwk.generate.rpb.wizard.line', 'reference', string='Container List')
    nomor_container = fields.Integer('Nomor Container', default=_default_nomor_container)

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

                if container.sale_line_ids:
                    for line in container.sale_line_ids:
                        jumlah_container = line.container
                        if container == 0:
                            container = 1

                        container_no = int(container.no_container)
                        while jumlah_container > 0:
                            container_id = self.env['pwk.rpb.container'].create({
                                'reference': rpb_id.id,
                                'no_container': container_no,
                                'jumlah_container': container.jumlah_container,
                                'name': container_no,
                            })

                            self.env['pwk.rpb.container.line'].create({
                                'reference': container_id.id,
                                'sale_id': line.order_id.id,
                                'sale_line_id': line.id,
                                'total_qty': line.product_uom_qty / (line.container or 1),
                                'container_qty': line.product_uom_qty / (line.container or 1)
                            })

                            rpb_line = self.env['pwk.rpb.line'].create({
                                'reference': rpb_id.id,
                                'container_id': container_id.id,
                                'jumlah_container': 1,
                                'sale_id': line.order_id.id,
                                'sale_line_id': line.id,
                                'total_qty': line.qty_rpb / (line.container or 1),
                                'container_qty': line.qty_rpb / (line.container or 1),
                                'outstanding_order_pcs': line.outstanding_order_pcs
                            })

                            rpb_line.button_reload_bom()
                            jumlah_container -= 1
                            container_no += 1