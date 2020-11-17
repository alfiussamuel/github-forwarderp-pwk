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

class PwkMutasiAssemblingFinishingGs1(models.Model):
    _name = "pwk.mutasi.assembling.finishing.gs1"

    reference = fields.Many2one('pwk.mutasi.assembling.finishing', 'Reference')
    product_id = fields.Many2one('product.product', 'Product')
    tebal = fields.Float(compute="_get_product_attribute", string='Tebal')
    lebar = fields.Float(compute="_get_product_attribute", string='Lebar')
    panjang = fields.Float(compute="_get_product_attribute", string='Panjang')
    grade = fields.Many2one(compute="_get_product_attribute", comodel_name='pwk.grade', string='Grade')
    stock_awal_pcs = fields.Float(compute="_get_stock_awal", string='Stok Awal')
    stock_awal_vol = fields.Float(compute="_get_volume", string='Stok Awal', digits=dp.get_precision('FourDecimal'))
    
    gs_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk GS (Pcs)')
    gs_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk GS (M3)', digits=dp.get_precision('FourDecimal'))
    gs_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk GS')
    gs_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk GS', digits=dp.get_precision('FourDecimal'))

    re_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Re-GS (Pcs)')
    re_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Re-GS (M3)', digits=dp.get_precision('FourDecimal'))
    re_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Re-GS')
    re_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Re-GS', digits=dp.get_precision('FourDecimal'))
    
    hot_stock_keluar_pcs = fields.Float('Stok Keluar Hot (Pcs)')
    hot_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Hot (M3)', digits=dp.get_precision('FourDecimal'))
    hot_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Hot')
    hot_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Hot', digits=dp.get_precision('FourDecimal'))

    gs_stock_keluar_pcs = fields.Float('Stok Keluar GS (Pcs)')
    gs_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar GS (M3)', digits=dp.get_precision('FourDecimal'))
    gs_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar GS')
    gs_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar GS', digits=dp.get_precision('FourDecimal'))

    stock_akhir_pcs = fields.Float(compute="_get_stock_akhir", string='Stok Akhir')
    stock_akhir_vol = fields.Float(compute="_get_volume", string='Stok Akhir', digits=dp.get_precision('FourDecimal'))

    @api.depends('product_id')
    def _get_product_attribute(self):
        for res in self:
            if res.product_id:
                res.tebal = res.product_id.tebal
                res.lebar = res.product_id.lebar
                res.panjang = res.product_id.panjang
                res.grade = res.product_id.grade.id

    @api.depends('stock_awal_pcs','gs_stock_masuk_pcs','re_stock_masuk_pcs','hot_stock_keluar_pcs','gs_stock_keluar_pcs')
    def _get_volume(self):
        for res in self:
            res.stock_awal_vol = res.stock_awal_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.gs_stock_masuk_vol = res.gs_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_stock_masuk_vol = res.re_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.hot_stock_keluar_vol = res.hot_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.gs_stock_keluar_vol = res.gs_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.gs_acc_stock_masuk_vol = res.gs_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_acc_stock_masuk_vol = res.re_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.hot_acc_stock_keluar_vol = res.hot_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.gs_acc_stock_keluar_vol = res.gs_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.stock_akhir_vol = res.stock_akhir_pcs * res.tebal * res.lebar * res.panjang / 1000000000

    @api.depends('stock_awal_pcs','gs_stock_masuk_pcs','re_stock_masuk_pcs','gs_stock_keluar_pcs','hot_stock_keluar_pcs')
    def _get_acc(self):
        for res in self:
            gs_acc_stock_masuk_pcs = 0
            re_acc_stock_masuk_pcs = 0
            hot_acc_stock_keluar_pcs = 0
            gs_acc_stock_keluar_pcs = 0

            if res.product_id:
                source_ids = self.env['pwk.mutasi.assembling.finishing.gs1'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.assembling.finishing.gs1'].search([
                        ('reference.date','<',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])

                if source_ids:
                    gs_acc_stock_masuk_pcs = source_ids[0].gs_acc_stock_masuk_pcs
                    re_acc_stock_masuk_pcs = source_ids[0].re_acc_stock_masuk_pcs
                    hot_acc_stock_keluar_pcs = source_ids[0].hot_acc_stock_keluar_pcs
                    gs_acc_stock_keluar_pcs = source_ids[0].gs_acc_stock_keluar_pcs

            res.gs_acc_stock_masuk_pcs = gs_acc_stock_masuk_pcs + res.gs_stock_masuk_pcs
            res.re_acc_stock_masuk_pcs = re_acc_stock_masuk_pcs + res.re_stock_masuk_pcs
            res.hot_acc_stock_keluar_pcs = hot_acc_stock_keluar_pcs + res.hot_stock_keluar_pcs
            res.gs_acc_stock_keluar_pcs = gs_acc_stock_keluar_pcs + res.gs_stock_keluar_pcs

    @api.depends('product_id','gs_stock_keluar_pcs')
    def _get_stock_masuk(self):
        for res in self:
            gs_stock_masuk_pcs = 0
            re_stock_masuk_pcs = 0

            if res.product_id:
                if res.reference.gs1_selection == "Veneer GS":
                    source_ids = self.env['pwk.mutasi.veneer.gs.line'].search([
                        ('reference.date','=',res.reference.date - timedelta(1)),
                        ('product_id','=',res.product_id.id)
                        ])

                    if source_ids:
                        gs_stock_masuk_pcs = source_ids[0].stock_keluar_gs_pcs
                
                re_stock_masuk_pcs = res.gs_stock_keluar_pcs

            res.gs_stock_masuk_pcs = gs_stock_masuk_pcs
            res.re_stock_masuk_pcs = re_stock_masuk_pcs

    @api.depends('product_id')
    def _get_stock_awal(self):
        for res in self:
            stock_awal_pcs = 0

            if res.product_id:
                source_ids = self.env['pwk.mutasi.assembling.finishing.gs1'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.assembling.finishing.gs1'].search([
                        ('reference.date','<',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])
                            
                if source_ids:
                    stock_awal_pcs = source_ids[0].stock_akhir_pcs

            res.stock_awal_pcs = stock_awal_pcs

    @api.depends('stock_awal_pcs','gs_stock_masuk_pcs','re_stock_masuk_pcs','hot_stock_keluar_pcs','gs_stock_keluar_pcs')
    def _get_stock_akhir(self):
        for res in self:
            res.stock_akhir_pcs = res.stock_awal_pcs + res.gs_stock_masuk_pcs + res.re_stock_masuk_pcs - res.hot_stock_keluar_pcs - res.gs_stock_keluar_pcs

class PwkMutasiAssemblingFinishing(models.Model):    
    _name = "pwk.mutasi.assembling.finishing"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char('No. Dokumen', track_visibility="always")
    date = fields.Date('Tanggal', default=fields.Date.today(), track_visibility="always")
    user_id = fields.Many2one('res.users', string="Dibuat Oleh", default=lambda self: self.env.user, track_visibility="always")
    state = fields.Selection([('Draft','Draft'),('Approved','Approved')], string="Status", default="Draft", track_visibility="always")
    gs1_ids = fields.One2many('pwk.mutasi.assembling.finishing.gs1', 'reference', string="GS 1", track_visibility="always")
    gs1_selection = fields.Selection([('Veneer GS','Veneer GS'),('Proses Ulang 2','Proses Ulang 2'),('Semua Proses','Semua Proses')], string="Proses Asal", default="Veneer GS", track_visibility="always")

    def get_sequence(self, name=False, obj=False, context=None):
        sequence_id = self.env['ir.sequence'].search([
            ('name', '=', name),
            ('code', '=', obj),
            ('suffix', '=', '.MASF.%(month)s.%(year)s')
        ])
        if not sequence_id :
            sequence_id = self.env['ir.sequence'].sudo().create({
                'name': name,
                'code': obj,
                'implementation': 'no_gap',
                'suffix': '.MASF.%(month)s.%(year)s',
                'padding': 3
            })
        return sequence_id.next_by_id()

    @api.multi
    def button_reload_gs1(self):
        for res in self:
            source_ids = self.env['pwk.mutasi.veneer.gs.line'].search([
                ('reference.date','=',res.date - timedelta(1)),
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.veneer.gs.line'].search([
                    ('reference.date','<',res.date),
                    ])

            if source_ids:
                for source in source_ids:
                    self.env['pwk.mutasi.assembling.finishing.gs1'].create({
                        'reference': res.id,
                        'product_id': source.product_id.id,
                        })

    @api.model
    def create(self, vals):
        vals['name'] = self.get_sequence('Mutasi Assembling Finishing', 'pwk.mutasi.assembling.finishing')
        return super(PwkMutasiAssemblingFinishing, self).create(vals)

    @api.multi
    def button_approve(self):
        for res in self:
            res.state = "Approved"
