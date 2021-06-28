# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_type = fields.Char('Type')
    product_size = fields.Char('Size')
    product_brand = fields.Char('Brand')
    product_spec = fields.Char('Other Specification')
