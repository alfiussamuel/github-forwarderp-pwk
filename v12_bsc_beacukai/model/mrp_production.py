# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _


class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'

    name = fields.Char(
        'Reference', copy=False, readonly=True, default=lambda x: _('New'),  states={'confirmed': [('readonly', False)]})

