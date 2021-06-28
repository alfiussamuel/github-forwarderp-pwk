# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api


class DecimalPrecision(models.Model):
    _inherit = 'decimal.precision'

    @api.model
    def update_dp(self):
        rec = self.search([('name', '=', 'Product Unit of Measure')], limit=1)
        if rec:
            rec.digits = 5


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    @api.model
    def update_procurement_rule(self):
        rec = self.search([('name', '=', 'WH: Stock -> Customers')], limit=1)
        barang_jadi_location = self.env['stock.location'].search([('name', '=', 'Barang Jadi')], limit=1)

        if rec and barang_jadi_location:
            rec.location_src_id = barang_jadi_location.id

