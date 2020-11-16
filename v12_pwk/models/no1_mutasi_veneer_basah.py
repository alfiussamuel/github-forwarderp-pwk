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

class PwkMutasiVeneerBasahStacking(models.Model):    
    _name = "pwk.mutasi.veneer.basah.stacking"

    reference = fields.Many2one('pwk.mutasi.veneer.basah', 'Reference')
    product_id = fields.Many2one('product.product', 'Product')
    tebal = fields.Float(compute="_get_product_attribute", string='Tebal')
    lebar = fields.Float(compute="_get_product_attribute", string='Lebar')
    panjang = fields.Float(compute="_get_product_attribute", string='Panjang')
    grade = fields.Many2one(compute="_get_product_attribute", comodel_name='pwk.grade', string='Grade')
    stock_awal_pcs = fields.Float(compute="_get_stock_awal", string='Stok Awal')
    stock_awal_vol = fields.Float(compute="_get_volume", string='Stok Awal')
    stock_masuk_supplier_pcs = fields.Float('Stok Masuk Supplier')    
    stock_masuk_supplier_vol = fields.Float(compute="_get_volume", string='Stok Masuk Supplier')
    acc_stock_masuk_supplier_pcs = fields.Float(compute="_get_acc", string='Akumulasi')
    acc_stock_masuk_supplier_vol = fields.Float(compute="_get_volume", string='Acc Stok Masuk Supplier')
    stock_masuk_rotary_pcs = fields.Float('Stok Masuk Rotary')    
    stock_masuk_rotary_vol = fields.Float(compute="_get_volume", string='Stok Masuk Rotary')
    acc_stock_masuk_rotary_pcs = fields.Float(compute="_get_acc", string='Akumulasi')
    acc_stock_masuk_rotary_vol = fields.Float(compute="_get_volume", string='Akumulasi')
    stock_keluar_stacking_pcs = fields.Float('Stok Keluar Stacking')    
    stock_keluar_stacking_vol = fields.Float(compute="_get_volume", string='Stok Keluar Stacking')
    acc_stock_keluar_stacking_pcs = fields.Float(compute="_get_acc", string='Akumulasi')
    acc_stock_keluar_stacking_vol = fields.Float(compute="_get_volume", string='Akumulasi')
    stock_keluar_roler_pcs = fields.Float('Stok Keluar Roler')    
    stock_keluar_roler_vol = fields.Float(compute="_get_volume", string='Stok Keluar Roler')
    acc_stock_keluar_roler_pcs = fields.Float(compute="_get_acc", string='Akumulasi')
    acc_stock_keluar_roler_vol = fields.Float(compute="_get_volume", string='Akumulasi')
    stock_akhir_pcs = fields.Float(compute="_get_stock_akhir", string='Stok Akhir')
    stock_akhir_vol = fields.Float(compute="_get_volume", string='Stok Akhir')

    @api.depends('product_id')
    def _get_product_attribute(self):
        for res in self:
            if res.product_id:
                res.tebal = res.product_id.tebal
                res.lebar = res.product_id.lebar
                res.panjang = res.product_id.panjang
                res.grade = res.product_id.grade.id

    @api.depends('stock_awal_pcs','stock_masuk_rotary_pcs','stock_masuk_supplier_pcs','stock_keluar_roler_pcs','stock_keluar_stacking_pcs')
    def _get_volume(self):
        for res in self:            
            res.stock_awal_vol = res.stock_awal_pcs
            res.stock_masuk_rotary_vol = res.stock_masuk_rotary_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.stock_masuk_supplier_vol = res.stock_masuk_supplier_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.stock_keluar_roler_vol = res.stock_keluar_roler_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.stock_keluar_stacking_vol = res.stock_keluar_stacking_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.acc_stock_masuk_rotary_vol = res.acc_stock_masuk_rotary_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.acc_stock_masuk_supplier_vol = res.acc_stock_masuk_supplier_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.acc_stock_keluar_roler_vol = res.acc_stock_keluar_roler_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.acc_stock_keluar_stacking_vol = res.acc_stock_keluar_stacking_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.stock_akhir_vol = res.stock_akhir_pcs

    @api.depends('product_id')
    def _get_stock_awal(self):
        for res in self:
            for res in self:
                stock_awal_pcs = 0
                source_ids = self.env['pwk.mutasi.veneer.basah.stacking'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.veneer.basah.stacking'].search([
                        ('reference.date','<',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])
                
                if source_ids:
                    stock_awal_pcs = source_ids[0].stock_akhir_pcs

                res.stock_awal_pcs = stock_awal_pcs

    @api.depends('stock_awal_pcs','stock_masuk_rotary_pcs','stock_masuk_supplier_pcs','stock_keluar_roler_pcs','stock_keluar_stacking_pcs')
    def _get_acc(self):
        for res in self:
            acc_stock_masuk_supplier_pcs = 0
            acc_stock_masuk_rotary_pcs = 0
            acc_stock_keluar_roler_pcs = 0
            acc_stock_keluar_stacking_pcs = 0

            source_ids = self.env['pwk.mutasi.veneer.basah.stacking'].search([
                ('reference.date','=',res.reference.date - timedelta(1)),
                ('product_id','=',res.product_id.id)
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.veneer.basah.stacking'].search([
                    ('reference.date','<',res.reference.date),
                    ('product_id','=',res.product_id.id)
                    ])

            if source_ids:
                acc_stock_masuk_supplier_pcs = source_ids[0].acc_stock_masuk_supplier_pcs
                acc_stock_masuk_rotary_pcs = source_ids[0].acc_stock_masuk_rotary_pcs
                acc_stock_keluar_roler_pcs = source_ids[0].acc_stock_keluar_roler_pcs
                acc_stock_keluar_stacking_pcs = source_ids[0].acc_stock_keluar_stacking_pcs

            res.acc_stock_masuk_supplier_pcs = acc_stock_masuk_supplier_pcs + res.stock_masuk_supplier_pcs
            res.acc_stock_masuk_rotary_pcs = acc_stock_masuk_rotary_pcs + res.stock_masuk_rotary_pcs
            res.stock_keluar_roler_pcs = stock_keluar_roler_pcs + res.stock_keluar_roler_pcs
            res.stock_keluar_stacking_pcs = stock_keluar_stacking_pcs + res.stock_keluar_stacking_pcs

    @api.depends('stock_awal_pcs','stock_masuk_rotary_pcs','stock_masuk_supplier_pcs','stock_keluar_roler_pcs','stock_keluar_stacking_pcs')
    def _get_stock_akhir(self):
        for res in self:
            res.stock_akhir_pcs = res.stock_awal_pcs + res.stock_masuk_rotary_pcs + res.stock_masuk_supplier_pcs - res.stock_keluar_roler_pcs - res.stock_keluar_stacking_pcs

class PwkMutasiVeneerBasah(models.Model):    
    _name = "pwk.mutasi.veneer.basah"

    name = fields.Char('No. Dokumen')
    date = fields.Date('Tanggal', default=fields.Date.today())
    user_id = fields.Many2one('res.users', string="Dibuat Oleh", default=lambda self: self.env.user)
    state = fields.Selection([('Draft','Draft'),('Approved','Approved')], string="Status")
    stacking_ids = fields.One2many('pwk.mutasi.veneer.basah.stacking', 'reference', string="Stacking")
    # kd_ids = fields.One2many('pwk.mutasi.veneer.basah.kd', 'reference', string="KD")

    def get_sequence(self, name=False, obj=False, context=None):
        sequence_id = self.env['ir.sequence'].search([
            ('name', '=', name),
            ('code', '=', obj),
            ('prefix', '=', 'PWKWI.'),
            ('suffix', '=', '.MVB.%(month)s.%(year)s')
        ])
        if not sequence_id :
            sequence_id = self.env['ir.sequence'].sudo().create({
                'name': name,
                'code': obj,
                'implementation': 'no_gap',
                'prefix': 'PWKWI.',
                'suffix': '.MVB.%(month)s.%(year)s',
                'padding': 3
            })
        return sequence_id.next_by_id()

    @api.model
    def create(self, vals):
        vals['name'] = self.get_sequence('Mutasi Veneer Basah', 'pwk.mutasi.veneer.basah')
        return super(PwkMutasiVeneerBasah, self).create(vals)

    @api.multi
    def button_approve(self):
        for res in self:
            res.state = "Approved"