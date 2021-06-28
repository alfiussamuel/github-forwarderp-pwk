# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    bc_ref_type = fields.Selection([
        ('beacukai.incoming', 'BC IN'),
        ('beacukai.incoming.23', 'BC IN 23'),
        ('beacukai.incoming.27', 'BC IN 27'),
        ('beacukai.incoming.40', 'BC IN 40'),
        ('beacukai.incoming.262', 'BC IN 262'),
        ('beacukai.outgoing', 'BC OUT'),
        ('beacukai.outgoing.25', 'BC OUT 25'),
        ('beacukai.outgoing.27', 'BC OUT 27'),
        ('beacukai.outgoing.30', 'BC OUT 30'),
        ('beacukai.outgoing.41', 'BC OUT 41'),
        ('beacukai.outgoing.261', 'BC OUT 261'),
    ], string='Beacukai Ref Type')
    bc_ref_id = fields.Integer('Referenced Dokumen ID')
