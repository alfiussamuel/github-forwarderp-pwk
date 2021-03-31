from odoo import api,fields,models,_
import time
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning
from datetime import datetime, date
from datetime import datetime, timedelta
from dateutil.relativedelta import *
from odoo.tools.safe_eval import safe_eval
import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_compare, float_round
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils
import math
import re

class StockMove(models.Model):    
    _inherit = "stock.move"

    thick = fields.Float(compute="_get_sale_fields", string='Thick')
    width = fields.Float(compute="_get_sale_fields", string='Width')
    length = fields.Float(compute="_get_sale_fields", string='Length')
    grade_id = fields.Many2one(compute="_get_sale_fields", comodel_name='pwk.grade', string='Grade')        

    @api.depends('product_id')
    def _get_sale_fields(self):
        for res in self:
            if res.product_id:
                res.thick = res.product_id.tebal
                res.width = res.product_id.lebar
                res.length = res.product_id.panjang
                res.grade_id = res.product_id.grade.id


class StockPickingGroup(models.Model):    
    _name = "stock.picking.group"

    reference = fields.Many2one('stock.picking', 'Delivery Order')
    jenis_kayu_id = fields.Many2one('pwk.jenis.kayu', 'Jenis Kayu')
    goods_type = fields.Selection([
        ('Plywood','Plywood'),
        ('Blockboard','Blockboard'),
        ('Barecore','Barecore'),
        ('Faceback','Faceback'),
        ('MDF','MDF'),
        ('Veneer','Veneer')]
        , string="Goods Type")


class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    certificate_id = fields.Many2one('pwk.certificate', 'Certificate')
    is_logo = fields.Boolean('Show Legal Logo', default=True)
    no_kendaraan = fields.Char('No. Kendaraan')
    group_ids = fields.One2many('stock.picking.group', 'reference', 'Groups')

    @api.multi
    def print_delivery_order(self):
        # Create Groups for Printing
        for res in self:
            if res.move_ids_without_package:
                for line in res.move_ids_without_package:
                    existing_group_id = self.env['stock.picking.group'].search([
                        ('reference', '=', res.id),
                        ('goods_type', '=', line.product_id.goods_type),
                        ('jenis_kayu_id', '=', line.product_id.jenis_kayu.id)
                    ])

                    if not existing_group_id:
                        self.env['stock.picking.group'].create({
                            'reference': res.id,
                            'goods_type': line.product_id.goods_type,
                            'jenis_kayu_id': line.product_id.jenis_kayu.id
                        })

            return self.env.ref('v12_pwk.delivery_order').report_action(self)