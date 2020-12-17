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

class PwkPemakaianVeneerGsLine(models.Model):
    _name = "pwk.pemakaian.veneer.gs.line"

    reference = fields.Many2one('pwk.pemakaian.veneer.gs', 'Reference')
    
    bj_product_id = fields.Many2one('product.product', 'Ply/BB')
    bj_tebal = fields.Float(compute="_get_product_attribute", string='Tebal')
    bj_lebar = fields.Float(compute="_get_product_attribute", string='Lebar')
    bj_panjang = fields.Float(compute="_get_product_attribute", string='Panjang')
    bj_jenis_kayu = fields.Float(compute="_get_product_attribute", comodel_name="pwk.jenis.kayu",  string='Jenis Kayu')
    bj_grade = fields.Many2one(compute="_get_product_attribute", comodel_name='pwk.grade', string='Grade')
    bj_pcs = fields.Float('PCS')
    bj_vol = fields.Float(compute="_get_volume", string='M3', digits=dp.get_precision('FourDecimal'))
    
    bb_product_id = fields.Many2one('product.product', 'Veneer/Core')
    bb_tebal = fields.Float(compute="_get_product_attribute", string='Tebal')
    bb_lebar = fields.Float(compute="_get_product_attribute", string='Lebar')
    bb_panjang = fields.Float(compute="_get_product_attribute", string='Panjang')
    bb_jenis_kayu = fields.Float(compute="_get_product_attribute", comodel_name="pwk.jenis.kayu", string='Jenis Kayu')
    bb_grade = fields.Many2one(compute="_get_product_attribute", comodel_name='pwk.grade', string='Grade')
    bb_pcs = fields.Float('PCS')
    bb_vol = fields.Float(compute="_get_volume", string='M3', digits=dp.get_precision('FourDecimal')
    
    @api.depends('bj_product_id', 'bb_product_id')
    def _get_product_attribute(self):
        for res in self:
#             if res.bj_product_id:                         
            res.bj_tebal = 0
            res.bj_lebar = 0
            res.bj_panjang = 0
            res.bj_grade = 0
            res.bj_jenis_kayu = 0
                          #             if res.bb_product_id:    
#                 res.bb_tebal = res.bb_product_id.tebal
#                 res.bb_lebar = res.bb_product_id.lebar
#                 res.bb_panjang = res.bb_product_id.panjang
#                 res.bb_grade = res.bb_product_id.grade.id
#                 res.bb_jenis_kayu = res.bb_product_id.jenis_kayu.id
                         
#     @api.depends('bj_product_id', 'bb_product_id')
#     def _get_product_attribute(self):
#         for res in self:
#             if res.bj_product_id:                         
#                 res.bj_tebal = res.bj_product_id.tebal
#                 res.bj_lebar = res.bj_product_id.lebar
#                 res.bj_panjang = res.bj_product_id.panjang
#                 res.bj_grade = res.bj_product_id.grade.id
#                 res.bj_jenis_kayu = res.bj_product_id.jenis_kayu.id
#             if res.bb_product_id:    
#                 res.bb_tebal = res.bb_product_id.tebal
#                 res.bb_lebar = res.bb_product_id.lebar
#                 res.bb_panjang = res.bb_product_id.panjang
#                 res.bb_grade = res.bb_product_id.grade.id
#                 res.bb_jenis_kayu = res.bb_product_id.jenis_kayu.id

    @api.depends('bj_pcs','bb_pcs')
    def _get_volume(self):
        for res in self:
            res.bj_vol = res.bj_pcs * res.bj_tebal * res.bj_lebar * res.bj_panjang / 1000000000
            res.bb_vol = res.bb_pcs * res.bb_tebal * res.bb_lebar * res.bb_panjang / 1000000000
                  
                          
class PwkPemakaianVeneerGs(models.Model):    
    _name = "pwk.pemakaian.veneer.gs"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char('No. Dokumen', track_visibility="always")
    date = fields.Date('Tanggal', default=fields.Date.today(), track_visibility="always")
    user_id = fields.Many2one('res.users', string="Dibuat Oleh", default=lambda self: self.env.user, track_visibility="always")
    state = fields.Selection([('Draft','Draft'),('Approved','Approved')], string="Status", default="Draft", track_visibility="always")
    line_ids = fields.One2many('pwk.pemakaian.veneer.gs.line', 'reference', string="Pemakaian Veneer GS", track_visibility="always")

    def get_sequence(self, name=False, obj=False, context=None):
        sequence_id = self.env['ir.sequence'].search([
            ('name', '=', name),
            ('code', '=', obj),
            ('suffix', '=', '.PVGS.%(month)s.%(year)s')
        ])
        if not sequence_id :
            sequence_id = self.env['ir.sequence'].sudo().create({
                'name': name,
                'code': obj,
                'implementation': 'no_gap',
                'suffix': '.PVGS.%(month)s.%(year)s',
                'padding': 3
            })
        return sequence_id.next_by_id()

    @api.model
    def create(self, vals):
        vals['name'] = self.get_sequence('Pemakaian Veneer GS', 'pwk.pemakaian.veneer.gs')
        return super(PwkPemakaianVeneerGs, self).create(vals)

    @api.multi
    def button_approve(self):
        for res in self:
            res.state = "Approved"            

    @api.multi
    def button_draft(self):
        for res in self:
            res.state = 'Draft'
