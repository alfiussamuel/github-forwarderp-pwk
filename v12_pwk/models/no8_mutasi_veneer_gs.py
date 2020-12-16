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

class PwkMutasiVeneerGsLine(models.Model):
    _name = "pwk.mutasi.veneer.gs.line"

    reference = fields.Many2one('pwk.mutasi.veneer.gs', 'Reference')
    product_id = fields.Many2one('product.product', 'Product')
    tebal = fields.Float(compute="_get_product_attribute", string='Tebal')
    lebar = fields.Float(compute="_get_product_attribute", string='Lebar')
    panjang = fields.Float(compute="_get_product_attribute", string='Panjang')
    grade = fields.Many2one(compute="_get_product_attribute", comodel_name='pwk.grade', string='Grade')
    stock_awal_pcs = fields.Float(compute="_get_stock_awal", string='Stok Awal')
    stock_awal_vol = fields.Float(compute="_get_volume", string='Stok Awal', digits=dp.get_precision('FourDecimal'))
    
    stock_masuk_repair_pcs = fields.Float(string='Stok Masuk Repair (Pcs)')
    stock_masuk_repair_vol = fields.Float(compute="_get_volume", string='Stok Masuk Repair (M3)', digits=dp.get_precision('FourDecimal'))
    acc_stock_masuk_repair_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Repair')
    acc_stock_masuk_repair_vol = fields.Float(compute="_get_volume", string='Stok Masuk Repair', digits=dp.get_precision('FourDecimal'))

    stock_masuk_supplier_pcs = fields.Float(string='Stok Masuk Supplier (Pcs)')
    stock_masuk_supplier_vol = fields.Float(compute="_get_volume", string='Stok Masuk Supplier (M3)', digits=dp.get_precision('FourDecimal'))
    acc_stock_masuk_supplier_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Supplier')
    acc_stock_masuk_supplier_vol = fields.Float(compute="_get_volume", string='Stok Masuk Supplier', digits=dp.get_precision('FourDecimal'))
    
    stock_keluar_gs_pcs = fields.Float('Stok Keluar GS (Pcs)')
    stock_keluar_gs_vol = fields.Float(compute="_get_volume", string='Stok Keluar GS (M3)', digits=dp.get_precision('FourDecimal'))
    acc_stock_keluar_gs_pcs = fields.Float(compute="_get_acc", string='Stok Keluar GS')
    acc_stock_keluar_gs_vol = fields.Float(compute="_get_volume", string='Stok Keluar GS', digits=dp.get_precision('FourDecimal'))

    stock_keluar_hpr_pcs = fields.Float('Stok Keluar H/PR (Pcs)')
    stock_keluar_hpr_vol = fields.Float(compute="_get_volume", string='Stok Keluar H/PR (M3)', digits=dp.get_precision('FourDecimal'))
    acc_stock_keluar_hpr_pcs = fields.Float(compute="_get_acc", string='Stok Keluar H/PR')
    acc_stock_keluar_hpr_vol = fields.Float(compute="_get_volume", string='Stok Keluar H/PR', digits=dp.get_precision('FourDecimal'))

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

    @api.depends('stock_awal_pcs','stock_masuk_repair_pcs','stock_masuk_supplier_pcs','stock_keluar_gs_pcs','stock_keluar_hpr_pcs')
    def _get_volume(self):
        for res in self:
            res.stock_awal_vol = res.stock_awal_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.stock_masuk_repair_vol = res.stock_masuk_repair_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.stock_masuk_supplier_vol = res.stock_masuk_supplier_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.stock_keluar_gs_vol = res.stock_keluar_gs_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.stock_keluar_hpr_vol = res.stock_keluar_hpr_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.acc_stock_masuk_repair_vol = res.acc_stock_masuk_repair_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.acc_stock_masuk_supplier_vol = res.acc_stock_masuk_supplier_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.acc_stock_keluar_gs_vol = res.acc_stock_keluar_gs_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.acc_stock_keluar_hpr_vol = res.acc_stock_keluar_hpr_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.stock_akhir_vol = res.stock_akhir_pcs * res.tebal * res.lebar * res.panjang / 1000000000

    @api.depends('stock_awal_pcs','stock_masuk_repair_pcs','stock_keluar_gs_pcs','stock_masuk_supplier_pcs','stock_keluar_hpr_pcs')
    def _get_acc(self):
        for res in self:
            acc_stock_masuk_repair_pcs = 0
            acc_stock_masuk_supplier_pcs = 0
            acc_stock_keluar_gs_pcs = 0
            acc_stock_keluar_hpr_pcs = 0

            source_ids = self.env['pwk.mutasi.veneer.gs.line'].search([
                ('reference.date','=',res.reference.date - timedelta(1)),
                ('product_id','=',res.product_id.id)
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.veneer.gs.line'].search([
                    ('reference.date','<',res.reference.date),
                    ('product_id','=',res.product_id.id)
                    ])

            if source_ids:
                acc_stock_masuk_repair_pcs = source_ids[0].acc_stock_masuk_repair_pcs
                acc_stock_masuk_supplier_pcs = source_ids[0].acc_stock_masuk_supplier_pcs
                acc_stock_keluar_gs_pcs = source_ids[0].acc_stock_keluar_gs_pcs
                acc_stock_keluar_hpr_pcs = source_ids[0].acc_stock_keluar_hpr_pcs

            res.acc_stock_masuk_repair_pcs = acc_stock_masuk_repair_pcs + res.stock_masuk_repair_pcs
            res.acc_stock_masuk_supplier_pcs = acc_stock_masuk_supplier_pcs + res.stock_masuk_supplier_pcs
            res.acc_stock_keluar_gs_pcs = acc_stock_keluar_gs_pcs + res.stock_keluar_gs_pcs
            res.acc_stock_keluar_hpr_pcs = acc_stock_keluar_hpr_pcs + res.stock_keluar_hpr_pcs

    @api.depends('product_id')
    def _get_stock_awal(self):
        for res in self:
            stock_awal_pcs = 0
            source_ids = self.env['pwk.mutasi.veneer.gs.line'].search([
                ('reference.date','=',res.reference.date - timedelta(1)),
                ('product_id','=',res.product_id.id)
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.veneer.gs.line'].search([
                    ('reference.date','<',res.reference.date),
                    ('product_id','=',res.product_id.id)
                    ])
                        
            if source_ids:
                stock_awal_pcs = source_ids[0].stock_akhir_pcs

            res.stock_awal_pcs = stock_awal_pcs

    @api.depends('stock_awal_pcs','stock_masuk_repair_pcs','stock_keluar_gs_pcs','stock_masuk_supplier_pcs','stock_keluar_hpr_pcs')
    def _get_stock_akhir(self):
        for res in self:
            res.stock_akhir_pcs = res.stock_awal_pcs + res.stock_masuk_repair_pcs + res.stock_masuk_supplier_pcs - res.stock_keluar_gs_pcs - res.stock_keluar_hpr_pcs

class PwkMutasiVeneerGs(models.Model):    
    _name = "pwk.mutasi.veneer.gs"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char('No. Dokumen', track_visibility="always")
    date = fields.Date('Tanggal', default=fields.Date.today(), track_visibility="always")
    user_id = fields.Many2one('res.users', string="Dibuat Oleh", default=lambda self: self.env.user, track_visibility="always")
    state = fields.Selection([('Draft','Draft'),('Approved','Approved')], string="Status", default="Draft", track_visibility="always")
    line_ids = fields.One2many('pwk.mutasi.veneer.gs.line', 'reference', string="RolerDryer", track_visibility="always")

    def get_sequence(self, name=False, obj=False, context=None):
        sequence_id = self.env['ir.sequence'].search([
            ('name', '=', name),
            ('code', '=', obj),
            ('suffix', '=', '.MVGS.%(month)s.%(year)s')
        ])
        if not sequence_id :
            sequence_id = self.env['ir.sequence'].sudo().create({
                'name': name,
                'code': obj,
                'implementation': 'no_gap',
                'suffix': '.MVGS.%(month)s.%(year)s',
                'padding': 3
            })
        return sequence_id.next_by_id()

    @api.model
    def create(self, vals):
        vals['name'] = self.get_sequence('Mutasi Veneer Glue Spreader', 'pwk.mutasi.veneer.gs')
        return super(PwkMutasiVeneerGs, self).create(vals)

    @api.multi
    def button_approve(self):
        for res in self:
            res.state = "Approved"

    @api.multi
    def button_reload(self):
        for res in self:
            existing_ids = self.env['pwk.mutasi.veneer.gs.line'].search([
                ('reference', '=', self.id)
            ])
            
            if existing_ids:
                for existing in existing_ids:
                    existing.unlink()

            source_ids = self.env['pwk.mutasi.veneer.ok.repair.line'].search([
                ('reference.date','=',res.date),
                ])

            print (source_ids)

            if not source_ids:
                source_ids = self.env['pwk.mutasi.veneer.ok.repair.line'].search([
                    ('reference.date','=',res.date - timedelta(1)),
                    ])

            print (source_ids)
            
            if source_ids:
                for source in source_ids:
                    self.env['pwk.mutasi.veneer.gs.line'].create({
                        'reference': res.id,
                        'product_id': source.product_id.id,
                        })
