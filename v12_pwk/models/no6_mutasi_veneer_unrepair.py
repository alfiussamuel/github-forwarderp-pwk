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

class PwkMutasiVeneerUnrepairLine(models.Model):
    _name = "pwk.mutasi.veneer.unrepair.line"

    reference = fields.Many2one('pwk.mutasi.veneer.unrepair', 'Reference')
    product_id = fields.Many2one('product.product', 'Product')
    tebal = fields.Float(compute="_get_product_attribute", string='Tebal')
    lebar = fields.Float(compute="_get_product_attribute", string='Lebar')
    panjang = fields.Float(compute="_get_product_attribute", string='Panjang')
    grade = fields.Many2one(compute="_get_product_attribute", comodel_name='pwk.grade', string='Grade')
    stock_awal_pcs = fields.Float(compute="_get_stock_awal", string='Stok Awal')
    stock_awal_vol = fields.Float(compute="_get_volume", string='Stok Awal', digits=dp.get_precision('FourDecimal'))
    stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Kering')
    stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Kering', digits=dp.get_precision('FourDecimal'))
    acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Kering')
    acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Kering', digits=dp.get_precision('FourDecimal'))
    stock_keluar_pcs = fields.Float('Stok Keluar Kering')
    stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar OK Repair', digits=dp.get_precision('FourDecimal'))
    acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar OK Repair')
    acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar OK Repair', digits=dp.get_precision('FourDecimal'))
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

    @api.depends('stock_awal_pcs','stock_masuk_pcs','stock_keluar_pcs')
    def _get_volume(self):
        for res in self:
            res.stock_awal_vol = res.stock_awal_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.stock_masuk_vol = res.stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.stock_keluar_vol = res.stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.acc_stock_masuk_vol = res.acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.acc_stock_keluar_vol = res.acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.stock_akhir_vol = res.stock_akhir_pcs * res.tebal * res.lebar * res.panjang / 1000000000

    @api.depends('stock_awal_pcs','stock_masuk_pcs','stock_keluar_pcs')
    def _get_acc(self):
        for res in self:
            acc_stock_masuk_pcs = 0
            acc_stock_keluar_pcs = 0

            source_ids = self.env['pwk.mutasi.veneer.unrepair.line'].search([
                ('reference.date','=',res.reference.date - timedelta(1)),
                ('product_id','=',res.product_id.id)
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.veneer.unrepair.line'].search([
                    ('reference.date','<',res.reference.date),
                    ('product_id','=',res.product_id.id)
                    ])

            if source_ids:
                acc_stock_masuk_pcs = source_ids[0].acc_stock_masuk_pcs
                acc_stock_keluar_pcs = source_ids[0].acc_stock_keluar_pcs

            res.acc_stock_masuk_pcs = acc_stock_masuk_pcs + res.stock_masuk_pcs
            res.acc_stock_keluar_pcs = acc_stock_keluar_pcs + res.stock_keluar_pcs

    @api.depends('product_id')
    def _get_stock_awal(self):
        for res in self:
            stock_awal_pcs = 0
            source_ids = self.env['pwk.mutasi.veneer.unrepair.line'].search([
                ('reference.date','=',res.reference.date - timedelta(1)),
                ('product_id','=',res.product_id.id)
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.veneer.unrepair.line'].search([
                    ('reference.date','<',res.reference.date),
                    ('product_id','=',res.product_id.id)
                    ])
                        
            if source_ids:
                stock_awal_pcs = source_ids[0].stock_akhir_pcs

            res.stock_awal_pcs = stock_awal_pcs

    @api.depends('product_id')
    def _get_stock_masuk(self):
        for res in self:
            stock_masuk_pcs = 0
            source_ids = self.env['pwk.mutasi.veneer.kering.line'].search([
                ('reference.date','=',res.reference.date),
                ('product_id','=',res.product_id.id)
                ])
                        
            if source_ids:
                stock_masuk_pcs = source_ids[0].repair_stock_keluar_pcs

            res.stock_masuk_pcs = stock_masuk_pcs

    @api.depends('stock_awal_pcs','stock_masuk_pcs','stock_keluar_pcs')
    def _get_stock_akhir(self):
        for res in self:
            res.stock_akhir_pcs = res.stock_awal_pcs + res.stock_masuk_pcs - res.stock_keluar_pcs

class PwkMutasiVeneerUnrepair(models.Model):    
    _name = "pwk.mutasi.veneer.unrepair"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char('No. Dokumen', track_visibility="always")
    date = fields.Date('Tanggal', default=fields.Date.today(), track_visibility="always")
    user_id = fields.Many2one('res.users', string="Dibuat Oleh", default=lambda self: self.env.user, track_visibility="always")
    state = fields.Selection([('Draft','Draft'),('Approved','Approved')], string="Status", default="Draft", track_visibility="always")
    line_ids = fields.One2many('pwk.mutasi.veneer.unrepair.line', 'reference', string="RolerDryer", track_visibility="always")

    def get_sequence(self, name=False, obj=False, context=None):
        sequence_id = self.env['ir.sequence'].search([
            ('name', '=', name),
            ('code', '=', obj),
            ('suffix', '=', '.MVUR.%(month)s.%(year)s')
        ])
        if not sequence_id :
            sequence_id = self.env['ir.sequence'].sudo().create({
                'name': name,
                'code': obj,
                'implementation': 'no_gap',
                'suffix': '.MVUR.%(month)s.%(year)s',
                'padding': 3
            })
        return sequence_id.next_by_id()

    @api.multi
    def button_reload(self):
        for res in self:
            existing_ids = self.env['pwk.mutasi.veneer.unrepair.line'].search([
                ('reference', '=', self.id)
            ])
            
            if existing_ids:
                for existing in existing_ids:
                    existing.unlink()
                    
            source_ids = self.env['pwk.mutasi.veneer.kering.line'].search([
                ('reference.date','=',res.date),
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.veneer.kering.line'].search([
                    ('reference.date','<',res.date),
                    ])

            if source_ids:
                for source in source_ids:
                    self.env['pwk.mutasi.veneer.unrepair.line'].create({
                        'reference': res.id,
                        'product_id': source.product_id.id,
                        })

    @api.model
    def create(self, vals):
        vals['name'] = self.get_sequence('Mutasi Veneer Unrepair', 'pwk.mutasi.veneer.unrepair')
        return super(PwkMutasiVeneerUnrepair, self).create(vals)

    @api.multi
    def button_approve(self):
        for res in self:
            res.state = "Approved"

    @api.multi
    def button_print(self):
        return self.env.ref('v12_pwk.report_mutasi_veneer_unrepair').report_action(self)
