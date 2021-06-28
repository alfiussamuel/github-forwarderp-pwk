# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_utils
from datetime import datetime


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    @api.model
    def _default_location_id(self):
        company_user = self.env.user.company_id
        warehouse = self.env['stock.warehouse'].search(
            [('company_id', '=', company_user.id)], limit=1)
        if warehouse:
            return warehouse.lot_stock_id.id
        else:
            raise UserError(
                _('You must define a warehouse for the company: %s.') % (company_user.name,))

    location_id = fields.Many2one(
        'stock.location', 'Inventoried Location',
        readonly=False, required=True,
        states={'draft': [('readonly', False)]},
        default=_default_location_id)
    date = fields.Datetime(
        'Inventory Date',
        readonly=False, required=True,
        default=fields.Datetime.now,
        help="The date that will be used for the stock level check of the products and the validation of the stock move related to this inventory.")
