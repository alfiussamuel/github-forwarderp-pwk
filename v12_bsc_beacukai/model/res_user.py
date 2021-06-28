from odoo import api, models, fields


class Users(models.Model):
    _inherit = "res.users"

    default_picking_type = fields.Many2one('stock.picking.type',
                                           string='Default Picking Type',
                                           groups='stock.group_stock_manager')
