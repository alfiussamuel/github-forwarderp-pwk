from odoo import api,fields,models,_
import time
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning
from datetime import datetime, timedelta
from dateutil.relativedelta import *
from odoo.tools.safe_eval import safe_eval
import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_compare, float_round
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils
import math
import re    
from num2words import num2words

class PwkPemakaianVeneerLine(models.Model):
    _name = "pwk.pemakaian.veneer.line"

    reference = fields.Many2one('pwk.mutasi.harian.pmg', 'Reference')
    product_id = fields.Many2one('product.product', 'Product')
    tebal = fields.Float(compute="_get_product_attribute", string='Tebal')
    lebar = fields.Float(compute="_get_product_attribute", string='Lebar')
    panjang = fields.Float(compute="_get_product_attribute", string='Panjang')
    grade = fields.Many2one(compute="_get_product_attribute", comodel_name='pwk.grade', string='Grade')
    quantity = fields.Float(string='Quantity', digits=dp.get_precision('ZeroDecimal'))
    volume = fields.Float(compute="_get_volume", string='Volume', digits=dp.get_precision('FourDecimal'))
    keterangan = fields.Selection([('P1','P1'),('P2','P2')], string="Keterangan")

    @api.depends('product_id')
    def _get_product_attribute(self):
        for res in self:
            if res.product_id:
                res.tebal = res.product_id.tebal
                res.lebar = res.product_id.lebar
                res.panjang = res.product_id.panjang
                res.grade = res.product_id.grade.id

    @api.depends('quantity')
    def _get_volume(self):
        for res in self:
            res.volume = res.quantity * res.tebal * res.lebar * res.panjang / 1000000000
            

class PwkPemakaianVeneer(models.Model):    
    _name = "pwk.pemakaian.veneer"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char('No. Dokumen', track_visibility="always")
    date = fields.Date('Tanggal', default=fields.Date.today(), track_visibility="always")
    user_id = fields.Many2one('res.users', string="Dibuat Oleh", default=lambda self: self.env.user, track_visibility="always")
    state = fields.Selection([('Draft','Draft'),('Approved','Approved')], string="Status", default="Draft", track_visibility="always")
    line_ids = fields.One2many('pwk.pemakaian.veneer.line', 'reference', string="Detail", track_visibility="always")

    def get_sequence(self, name=False, obj=False, context=None):
        sequence_id = self.env['ir.sequence'].search([
            ('name', '=', name),
            ('code', '=', obj),
            ('suffix', '=', '.MHPM.%(month)s.%(year)s')
        ])
        if not sequence_id :
            sequence_id = self.env['ir.sequence'].sudo().create({
                'name': name,
                'code': obj,
                'implementation': 'no_gap',
                'suffix': '.MHPM.%(month)s.%(year)s',
                'padding': 3
            })
        return sequence_id.next_by_id()

    @api.model
    def create(self, vals):
        vals['name'] = self.get_sequence('Pemakaian Veneer', 'pwk.pemakaian.veneer')
        return super(PwkPemakaianVeneer, self).create(vals)

    @api.multi
    def button_approve(self):
        for res in self:
            res.state = "Approved"            

    @api.multi
    def button_draft(self):
        for res in self:
            res.state = 'Draft'
