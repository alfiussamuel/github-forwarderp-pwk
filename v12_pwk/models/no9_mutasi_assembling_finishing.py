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
                    source_ids = self.env['pwk.pemakaian.veneer.gs.line'].search([
                        ('reference.date','=',res.reference.date),
                        ('bj_product_id','=',res.product_id.id)
                        ])

                    if source_ids:
                        gs_stock_masuk_pcs = source_ids[0].bj_pcs
                
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

class PwkMutasiAssemblingFinishingGs2(models.Model):
    _name = "pwk.mutasi.assembling.finishing.gs2"

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

    sk_stock_keluar_pcs = fields.Float('Stok Keluar SK (Pcs)')
    sk_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar SK (M3)', digits=dp.get_precision('FourDecimal'))
    sk_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar SK')
    sk_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar SK', digits=dp.get_precision('FourDecimal'))

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

    @api.depends('stock_awal_pcs','gs_stock_masuk_pcs','re_stock_masuk_pcs','hot_stock_keluar_pcs','gs_stock_keluar_pcs','sk_stock_keluar_pcs')
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
            res.sk_acc_stock_keluar_vol = res.sk_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.stock_akhir_vol = res.stock_akhir_pcs * res.tebal * res.lebar * res.panjang / 1000000000

    @api.depends('stock_awal_pcs','gs_stock_masuk_pcs','re_stock_masuk_pcs','gs_stock_keluar_pcs','hot_stock_keluar_pcs')
    def _get_acc(self):
        for res in self:
            gs_acc_stock_masuk_pcs = 0
            re_acc_stock_masuk_pcs = 0
            hot_acc_stock_keluar_pcs = 0
            gs_acc_stock_keluar_pcs = 0
            sk_acc_stock_keluar_pcs = 0

            if res.product_id:
                source_ids = self.env['pwk.mutasi.assembling.finishing.gs2'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.assembling.finishing.gs2'].search([
                        ('reference.date','<',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])

                if source_ids:
                    gs_acc_stock_masuk_pcs = source_ids[0].gs_acc_stock_masuk_pcs
                    re_acc_stock_masuk_pcs = source_ids[0].re_acc_stock_masuk_pcs
                    hot_acc_stock_keluar_pcs = source_ids[0].hot_acc_stock_keluar_pcs
                    gs_acc_stock_keluar_pcs = source_ids[0].gs_acc_stock_keluar_pcs
                    sk_acc_stock_keluar_pcs = source_ids[0].sk_acc_stock_keluar_pcs

            res.gs_acc_stock_masuk_pcs = gs_acc_stock_masuk_pcs + res.gs_stock_masuk_pcs
            res.re_acc_stock_masuk_pcs = re_acc_stock_masuk_pcs + res.re_stock_masuk_pcs
            res.hot_acc_stock_keluar_pcs = hot_acc_stock_keluar_pcs + res.hot_stock_keluar_pcs
            res.gs_acc_stock_keluar_pcs = gs_acc_stock_keluar_pcs + res.gs_stock_keluar_pcs
            res.sk_acc_stock_keluar_pcs = sk_acc_stock_keluar_pcs + res.sk_stock_keluar_pcs

    @api.depends('product_id')
    def _get_stock_masuk(self):
        for res in self:
            gs_stock_masuk_pcs = 0
            re_stock_masuk_pcs = 0

            if res.product_id:
                if res.reference.gs1_selection == "Veneer GS":
                    source_ids = self.env['pwk.pemakaian.veneer.gs.line'].search([
                        ('reference.date','=',res.reference.date),
                        ('bj_product_id','=',res.product_id.id)
                        ])

                    if source_ids:
                        gs_stock_masuk_pcs = source_ids[0].bj_pcs
                
            res.gs_stock_masuk_pcs = gs_stock_masuk_pcs

    @api.depends('product_id')
    def _get_stock_awal(self):
        for res in self:
            stock_awal_pcs = 0

            if res.product_id:
                source_ids = self.env['pwk.mutasi.assembling.finishing.gs2'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.assembling.finishing.gs2'].search([
                        ('reference.date','<',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])
                            
                if source_ids:
                    stock_awal_pcs = source_ids[0].stock_akhir_pcs

            res.stock_awal_pcs = stock_awal_pcs

    @api.depends('stock_awal_pcs','gs_stock_masuk_pcs','re_stock_masuk_pcs','hot_stock_keluar_pcs','gs_stock_keluar_pcs','sk_stock_keluar_pcs')
    def _get_stock_akhir(self):
        for res in self:
            res.stock_akhir_pcs = res.stock_awal_pcs + res.gs_stock_masuk_pcs + res.re_stock_masuk_pcs - res.hot_stock_keluar_pcs - res.gs_stock_keluar_pcs - res.sk_stock_keluar_pcs

class PwkMutasiAssemblingFinishingUnsander(models.Model):
    _name = "pwk.mutasi.assembling.finishing.unsander"

    reference = fields.Many2one('pwk.mutasi.assembling.finishing', 'Reference')
    product_id = fields.Many2one('product.product', 'Product')
    tebal = fields.Float(compute="_get_product_attribute", string='Tebal')
    lebar = fields.Float(compute="_get_product_attribute", string='Lebar')
    panjang = fields.Float(compute="_get_product_attribute", string='Panjang')
    grade = fields.Many2one(compute="_get_product_attribute", comodel_name='pwk.grade', string='Grade')
    stock_awal_pcs = fields.Float(compute="_get_stock_awal", string='Stok Awal')
    stock_awal_vol = fields.Float(compute="_get_volume", string='Stok Awal', digits=dp.get_precision('FourDecimal'))
    
    hot_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Hot (Pcs)')
    hot_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Hot (M3)', digits=dp.get_precision('FourDecimal'))
    hot_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Hot')
    hot_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Hot', digits=dp.get_precision('FourDecimal'))

    re_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Re (Pcs)')
    re_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Re (M3)', digits=dp.get_precision('FourDecimal'))
    re_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Re')
    re_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Re', digits=dp.get_precision('FourDecimal'))
    
    sander_stock_keluar_pcs = fields.Float('Stok Keluar Sander (Pcs)')
    sander_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Sander (M3)', digits=dp.get_precision('FourDecimal'))
    sander_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Sander')
    sander_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Sander', digits=dp.get_precision('FourDecimal'))

    reproses_stock_keluar_pcs = fields.Float('Stok Keluar Reproses (Pcs)')
    reproses_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Reproses (M3)', digits=dp.get_precision('FourDecimal'))
    reproses_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Reproses')
    reproses_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Reproses', digits=dp.get_precision('FourDecimal'))

    qc_stock_keluar_pcs = fields.Float('Stok Keluar QC')
    qc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar QC', digits=dp.get_precision('FourDecimal'))
    qc_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar QC')
    qc_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar QC', digits=dp.get_precision('FourDecimal'))

    lain_stock_keluar_pcs = fields.Float('Stok Keluar Lain (Pcs)')
    lain_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Lain (M3)', digits=dp.get_precision('FourDecimal'))
    lain_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Lain')
    lain_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Lain', digits=dp.get_precision('FourDecimal'))

    re_stock_keluar_pcs = fields.Float('Stok Keluar Re (Pcs)')
    re_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Re (M3)', digits=dp.get_precision('FourDecimal'))
    re_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Re')
    re_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Re', digits=dp.get_precision('FourDecimal'))    

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

    @api.depends('stock_awal_pcs',
        'hot_stock_masuk_pcs','hot_acc_stock_masuk_pcs',
        're_stock_masuk_pcs','re_acc_stock_masuk_pcs',
        'sander_stock_keluar_pcs','sander_acc_stock_keluar_pcs',
        'reproses_stock_keluar_pcs','reproses_acc_stock_keluar_pcs',
        'qc_stock_keluar_pcs','qc_acc_stock_keluar_pcs',
        'lain_stock_keluar_pcs','lain_acc_stock_keluar_pcs',
        're_stock_keluar_pcs','re_acc_stock_keluar_pcs',
        'stock_akhir_pcs')
    def _get_volume(self):
        for res in self:
            res.stock_awal_vol = res.stock_awal_pcs * res.tebal * res.lebar * res.panjang / 1000000000

            res.hot_stock_masuk_vol = res.hot_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_stock_masuk_vol = res.re_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.hot_acc_stock_masuk_vol = res.hot_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_acc_stock_masuk_vol = res.re_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.sander_stock_keluar_vol = res.sander_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.reproses_stock_keluar_vol = res.reproses_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.qc_stock_keluar_pcs = res.qc_stock_keluar_vol * res.tebal * res.lebar * res.panjang / 1000000000
            res.lain_stock_keluar_vol = res.lain_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_stock_keluar_vol = res.lain_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.sander_acc_stock_keluar_vol = res.sander_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.reproses_acc_stock_keluar_vol = res.reproses_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.qc_acc_stock_keluar_pcs = res.qc_acc_stock_keluar_vol * res.tebal * res.lebar * res.panjang / 1000000000
            res.lain_acc_stock_keluar_vol = res.lain_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_acc_stock_keluar_vol = res.re_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.stock_akhir_vol = res.stock_akhir_pcs * res.tebal * res.lebar * res.panjang / 1000000000

    @api.depends('stock_awal_pcs',
        'hot_stock_masuk_pcs','re_stock_masuk_pcs',
        'sander_stock_keluar_pcs','reproses_stock_keluar_pcs','qc_stock_keluar_pcs','lain_stock_keluar_pcs','re_stock_keluar_pcs')
    def _get_acc(self):
        for res in self:
            hot_acc_stock_masuk_pcs = 0
            re_acc_stock_masuk_pcs = 0

            sander_acc_stock_keluar_pcs = 0
            reproses_acc_stock_keluar_pcs = 0
            qc_acc_stock_keluar_pcs = 0
            lain_acc_stock_keluar_pcs = 0
            re_acc_stock_keluar_pcs = 0

            if res.product_id:
                source_ids = self.env['pwk.mutasi.assembling.finishing.unsander'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.assembling.finishing.unsander'].search([
                        ('reference.date','<',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])

                if source_ids:
                    hot_acc_stock_masuk_pcs = source_ids[0].hot_acc_stock_masuk_pcs
                    re_acc_stock_masuk_pcs = source_ids[0].re_acc_stock_masuk_pcs
                    sander_acc_stock_keluar_pcs = source_ids[0].sander_acc_stock_keluar_pcs
                    reproses_acc_stock_keluar_pcs = source_ids[0].reproses_acc_stock_keluar_pcs
                    qc_acc_stock_keluar_pcs = source_ids[0].qc_acc_stock_keluar_pcs
                    lain_acc_stock_keluar_pcs = source_ids[0].lain_acc_stock_keluar_pcs
                    rer_acc_stock_keluar_pcs = source_ids[0].re_acc_stock_keluar_pcs

            res.hot_acc_stock_masuk_pcs = hot_acc_stock_masuk_pcs + res.hot_stock_masuk_pcs
            res.re_acc_stock_masuk_pcs = re_acc_stock_masuk_pcs + res.re_stock_masuk_pcs
            res.sander_acc_stock_keluar_pcs = sander_acc_stock_keluar_pcs + res.sander_stock_keluar_pcs
            res.reproses_acc_stock_keluar_pcs = reproses_acc_stock_keluar_pcs + res.reproses_stock_keluar_pcs
            res.qc_acc_stock_keluar_pcs = qc_acc_stock_keluar_pcs + res.qc_stock_keluar_pcs
            res.lain_acc_stock_keluar_pcs = lain_acc_stock_keluar_pcs + res.lain_stock_keluar_pcs
            res.re_acc_stock_keluar_pcs = re_acc_stock_keluar_pcs + res.re_stock_keluar_pcs

    @api.depends('product_id')
    def _get_stock_masuk(self):
        for res in self:
            hot_stock_masuk_pcs = 0

            if res.product_id:
                if res.reference.gs1_selection == "Veneer GS":
                    source_ids = self.env['pwk.mutasi.assembling.finishing.gs1'].search([
                        ('reference.date','=',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])

                    if source_ids:
                        hot_stock_masuk_pcs = source_ids[0].hot_stock_keluar_pcs
                
            res.hot_stock_masuk_pcs = hot_stock_masuk_pcs

    @api.depends('product_id')
    def _get_stock_awal(self):
        for res in self:
            stock_awal_pcs = 0

            if res.product_id:
                source_ids = self.env['pwk.mutasi.assembling.finishing.unsander'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.assembling.finishing.unsander'].search([
                        ('reference.date','<',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])
                            
                if source_ids:
                    stock_awal_pcs = source_ids[0].stock_akhir_pcs

            res.stock_awal_pcs = stock_awal_pcs

    @api.depends('stock_awal_pcs',
        'hot_stock_masuk_pcs','re_stock_masuk_pcs',
        'sander_stock_keluar_pcs','reproses_stock_keluar_pcs','qc_stock_keluar_pcs','lain_stock_keluar_pcs','re_stock_keluar_pcs')
    def _get_stock_akhir(self):
        for res in self:
            res.stock_akhir_pcs = res.stock_awal_pcs + res.hot_stock_masuk_pcs + res.re_stock_masuk_pcs - res.sander_stock_keluar_pcs - res.reproses_stock_keluar_pcs - res.qc_stock_keluar_pcs - res.lain_stock_keluar_pcs - res.re_stock_keluar_pcs

class PwkMutasiAssemblingFinishingProses1(models.Model):
    _name = "pwk.mutasi.assembling.finishing.proses1"

    reference = fields.Many2one('pwk.mutasi.assembling.finishing', 'Reference')
    product_id = fields.Many2one('product.product', 'Product')
    tebal = fields.Float(compute="_get_product_attribute", string='Tebal')
    lebar = fields.Float(compute="_get_product_attribute", string='Lebar')
    panjang = fields.Float(compute="_get_product_attribute", string='Panjang')
    grade = fields.Many2one(compute="_get_product_attribute", comodel_name='pwk.grade', string='Grade')
    stock_awal_pcs = fields.Float(compute="_get_stock_awal", string='Stok Awal')
    stock_awal_vol = fields.Float(compute="_get_volume", string='Stok Awal', digits=dp.get_precision('FourDecimal'))
    
    sander_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Sander (Pcs)')
    sander_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Sander (M3)', digits=dp.get_precision('FourDecimal'))
    sander_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Sander')
    sander_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Sander', digits=dp.get_precision('FourDecimal'))

    re_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Re (M3)', digits=dp.get_precision('FourDecimal'))
    re_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Re (Pcs)')
    re_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Re')
    re_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Re', digits=dp.get_precision('FourDecimal'))
    
    lup1_sander_stock_keluar_pcs = fields.Float('Stok Keluar LUP1 (Pcs)')
    lup1_sander_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar LUP1 (M3)', digits=dp.get_precision('FourDecimal'))
    lup1_sander_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar LUP1')
    lup1_sander_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar LUP1', digits=dp.get_precision('FourDecimal'))

    lup2_sander_stock_keluar_pcs = fields.Float('Stok Keluar LUP2 (Pcs)')
    lup2_sander_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar LUP2 (M3)', digits=dp.get_precision('FourDecimal'))
    lup2_sander_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar LUP2')
    lup2_sander_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar LUP2', digits=dp.get_precision('FourDecimal'))
    
    lain_stock_keluar_pcs = fields.Float('Stok Keluar Lain (Pcs)')
    lain_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Lain (M3)', digits=dp.get_precision('FourDecimal'))
    lain_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Lain')
    lain_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Lain', digits=dp.get_precision('FourDecimal'))

    re_stock_keluar_pcs = fields.Float('Stok Keluar Re (Pcs)')
    re_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Re (M3)', digits=dp.get_precision('FourDecimal'))
    re_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Re')
    re_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Re', digits=dp.get_precision('FourDecimal'))    

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

    @api.depends('stock_awal_pcs',
        'sander_stock_masuk_pcs','re_stock_masuk_pcs',
        'lup1_sander_stock_keluar_pcs','lup2_sander_stock_keluar_pcs','lain_stock_keluar_pcs','re_stock_keluar_pcs',
        'sander_acc_stock_masuk_pcs','re_acc_stock_masuk_pcs',
        'lup1_sander_acc_stock_keluar_pcs','lup2_sander_acc_stock_keluar_pcs','lain_acc_stock_keluar_pcs','re_acc_stock_keluar_pcs',
        'stock_akhir_pcs')
    def _get_volume(self):
        for res in self:
            res.stock_awal_vol = res.stock_awal_pcs * res.tebal * res.lebar * res.panjang / 1000000000

            res.sander_stock_masuk_vol = res.sander_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_stock_masuk_vol = res.re_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.sander_acc_stock_masuk_vol = res.sander_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_acc_stock_masuk_vol = res.re_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.lup1_sander_stock_keluar_vol = res.lup1_sander_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.lup2_sander_stock_keluar_vol = res.lup2_sander_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000            
            res.lain_stock_keluar_vol = res.lain_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_stock_keluar_vol = res.lain_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.lup1_sander_acc_stock_keluar_vol = res.lup1_sander_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000            
            res.lup2_sander_acc_stock_keluar_vol = res.lup2_sander_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000            
            res.lain_acc_stock_keluar_vol = res.lain_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_acc_stock_keluar_vol = res.re_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.stock_akhir_vol = res.stock_akhir_pcs * res.tebal * res.lebar * res.panjang / 1000000000

    @api.depends('stock_awal_pcs','sander_stock_masuk_pcs','re_stock_masuk_pcs','lup1_sander_stock_keluar_pcs','lup2_sander_stock_keluar_pcs','lain_stock_keluar_pcs','re_stock_keluar_pcs')
    def _get_acc(self):
        for res in self:
            sander_acc_stock_masuk_pcs = 0
            re_acc_stock_masuk_pcs = 0
            lup1_sander_acc_stock_keluar_pcs = 0
            lup2_sander_acc_stock_keluar_pcs = 0
            lain_acc_stock_keluar_pcs = 0
            re_acc_stock_keluar_pcs = 0

            if res.product_id:
                source_ids = self.env['pwk.mutasi.assembling.finishing.proses1'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.assembling.finishing.proses1'].search([
                        ('reference.date','<',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])

                if source_ids:
                    sander_acc_stock_masuk_pcs = source_ids[0].sander_acc_stock_masuk_pcs
                    re_acc_stock_masuk_pcs = source_ids[0].re_acc_stock_masuk_pcs
                    lup1_sander_acc_stock_keluar_pcs = source_ids[0].lup1_sander_acc_stock_keluar_pcs
                    lup2_sander_acc_stock_keluar_pcs = source_ids[0].lup2_sander_acc_stock_keluar_pcs
                    lain_acc_stock_keluar_pcs = source_ids[0].lain_acc_stock_keluar_pcs
                    rer_acc_stock_keluar_pcs = source_ids[0].re_acc_stock_keluar_pcs

            res.sander_acc_stock_masuk_pcs = sander_acc_stock_masuk_pcs + res.sander_stock_masuk_pcs
            res.re_acc_stock_masuk_pcs = re_acc_stock_masuk_pcs + res.re_stock_masuk_pcs
            res.lup1_sander_acc_stock_keluar_pcs = lup1_sander_acc_stock_keluar_pcs + res.lup1_sander_stock_keluar_pcs
            res.lup2_sander_acc_stock_keluar_pcs = lup2_sander_acc_stock_keluar_pcs + res.lup2_sander_stock_keluar_pcs
            res.lain_acc_stock_keluar_pcs = lain_acc_stock_keluar_pcs + res.lain_stock_keluar_pcs
            res.re_acc_stock_keluar_pcs = re_acc_stock_keluar_pcs + res.re_stock_keluar_pcs

    @api.depends('product_id')
    def _get_stock_masuk(self):
        for res in self:
            sander_stock_masuk_pcs = 0

            if res.product_id:
                if res.reference.gs1_selection == "Veneer GS":
                    source_ids = self.env['pwk.mutasi.assembling.finishing.unsander'].search([
                        ('reference.date','=',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])

                    if source_ids:
                        sander_stock_masuk_pcs = source_ids[0].reproses_stock_keluar_pcs
                
            res.sander_stock_masuk_pcs = sander_stock_masuk_pcs
            res.re_stock_masuk_pcs = res.re_stock_keluar_pcs

    @api.depends('product_id')
    def _get_stock_awal(self):
        for res in self:
            stock_awal_pcs = 0

            if res.product_id:
                source_ids = self.env['pwk.mutasi.assembling.finishing.proses1'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.assembling.finishing.proses1'].search([
                        ('reference.date','<',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])
                            
                if source_ids:
                    stock_awal_pcs = source_ids[0].stock_akhir_pcs

            res.stock_awal_pcs = stock_awal_pcs

    @api.depends('stock_awal_pcs','sander_stock_masuk_pcs','re_stock_masuk_pcs','lup1_sander_stock_keluar_pcs','lup2_sander_stock_keluar_pcs','lain_stock_keluar_pcs','re_stock_keluar_pcs')
    def _get_stock_akhir(self):
        for res in self:
            res.stock_akhir_pcs = res.stock_awal_pcs + res.sander_stock_masuk_pcs + res.re_stock_masuk_pcs - res.lup1_sander_stock_keluar_pcs - res.lup2_sander_stock_keluar_pcs - res.lain_stock_keluar_pcs - res.re_stock_keluar_pcs

class PwkMutasiAssemblingFinishingProses2(models.Model):
    _name = "pwk.mutasi.assembling.finishing.proses2"

    keterangan = fields.Char('Keterangan')
    reference = fields.Many2one('pwk.mutasi.assembling.finishing', 'Reference')
    new_product_id = fields.Many2one('product.product', 'Product')
    product_id = fields.Many2one('product.product', 'Product')
    tebal = fields.Float(compute="_get_product_attribute", string='Tebal')
    lebar = fields.Float(compute="_get_product_attribute", string='Lebar')
    panjang = fields.Float(compute="_get_product_attribute", string='Panjang')
    grade = fields.Many2one(compute="_get_product_attribute", comodel_name='pwk.grade', string='Grade')
    stock_awal_pcs = fields.Float(compute="_get_stock_awal", string='Stok Awal')
    stock_awal_vol = fields.Float(compute="_get_volume", string='Stok Awal', digits=dp.get_precision('FourDecimal'))
    
    sander_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Sander (Pcs)')
    sander_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Sander (M3)', digits=dp.get_precision('FourDecimal'))
    sander_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Sander')
    sander_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Sander', digits=dp.get_precision('FourDecimal'))

    re_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Re (M3)', digits=dp.get_precision('FourDecimal'))
    re_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Re (Pcs)')
    re_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Re')
    re_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Re', digits=dp.get_precision('FourDecimal'))
    
    gs_stock_keluar_pcs = fields.Float('Stok Keluar GS (Pcs)')
    gs_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar GS (M3)', digits=dp.get_precision('FourDecimal'))
    gs_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar GS')
    gs_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar GS', digits=dp.get_precision('FourDecimal'))
    
    lain_stock_keluar_pcs = fields.Float('Stok Keluar Lain (Pcs)')
    lain_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Lain (M3)', digits=dp.get_precision('FourDecimal'))
    lain_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Lain')
    lain_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Lain', digits=dp.get_precision('FourDecimal'))

    re_stock_keluar_pcs = fields.Float('Stok Keluar Re (Pcs)')
    re_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Re (M3)', digits=dp.get_precision('FourDecimal'))
    re_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Re')
    re_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Re', digits=dp.get_precision('FourDecimal'))    

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

    @api.depends('stock_awal_pcs',
        'sander_stock_masuk_pcs','re_stock_masuk_pcs',
        'gs_stock_keluar_pcs','lain_stock_keluar_pcs','re_stock_keluar_pcs',
        'sander_acc_stock_masuk_pcs','re_acc_stock_masuk_pcs',
        'gs_acc_stock_keluar_pcs','lain_acc_stock_keluar_pcs','re_acc_stock_keluar_pcs',
        'stock_akhir_pcs')
    def _get_volume(self):
        for res in self:
            res.stock_awal_vol = res.stock_awal_pcs * res.tebal * res.lebar * res.panjang / 1000000000

            res.sander_stock_masuk_vol = res.sander_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_stock_masuk_vol = res.re_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.sander_acc_stock_masuk_vol = res.sander_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_acc_stock_masuk_vol = res.re_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.gs_stock_keluar_vol = res.gs_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000            
            res.lain_stock_keluar_vol = res.lain_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_stock_keluar_vol = res.lain_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.gs_acc_stock_keluar_vol = res.gs_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000            
            res.lain_acc_stock_keluar_vol = res.lain_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_acc_stock_keluar_vol = res.re_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.stock_akhir_vol = res.stock_akhir_pcs * res.tebal * res.lebar * res.panjang / 1000000000

    @api.depends('stock_awal_pcs','sander_stock_masuk_pcs','re_stock_masuk_pcs','gs_stock_keluar_pcs','lain_stock_keluar_pcs','re_stock_keluar_pcs')
    def _get_acc(self):
        for res in self:
            sander_acc_stock_masuk_pcs = 0
            re_acc_stock_masuk_pcs = 0
            gs_acc_stock_keluar_pcs = 0
            lain_acc_stock_keluar_pcs = 0
            re_acc_stock_keluar_pcs = 0

            if res.product_id:
                source_ids = self.env['pwk.mutasi.assembling.finishing.proses2'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.assembling.finishing.proses2'].search([
                        ('reference.date','<',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])

                if source_ids:
                    sander_acc_stock_masuk_pcs = source_ids[0].sander_acc_stock_masuk_pcs
                    re_acc_stock_masuk_pcs = source_ids[0].re_acc_stock_masuk_pcs
                    gs_acc_stock_keluar_pcs = source_ids[0].gs_acc_stock_keluar_pcs
                    lain_acc_stock_keluar_pcs = source_ids[0].lain_acc_stock_keluar_pcs
                    rer_acc_stock_keluar_pcs = source_ids[0].re_acc_stock_keluar_pcs

            res.sander_acc_stock_masuk_pcs = sander_acc_stock_masuk_pcs + res.sander_stock_masuk_pcs
            res.re_acc_stock_masuk_pcs = re_acc_stock_masuk_pcs + res.re_stock_masuk_pcs
            res.gs_acc_stock_keluar_pcs = gs_acc_stock_keluar_pcs + res.gs_stock_keluar_pcs
            res.lain_acc_stock_keluar_pcs = lain_acc_stock_keluar_pcs + res.lain_stock_keluar_pcs
            res.re_acc_stock_keluar_pcs = re_acc_stock_keluar_pcs + res.re_stock_keluar_pcs

    @api.depends('product_id')
    def _get_stock_masuk(self):
        for res in self:
            sander_stock_masuk_pcs = 0

            if res.product_id:
                if res.reference.gs1_selection == "Veneer GS":
                    source_ids = self.env['pwk.mutasi.assembling.finishing.proses1'].search([
                        ('reference.date','=',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])

                    if source_ids:
                        if res.keterangan == "LUP1":
                            if source_ids[0].lup1_sander_stock_keluar_pcs > 0:
                                sander_stock_masuk_pcs = source_ids[0].lup1_sander_stock_keluar_pcs
                        elif res.keterangan == "LUP2":
                            if source_ids[0].lup2_sander_stock_keluar_pcs > 0:
                                sander_stock_masuk_pcs = source_ids[0].lup2_sander_stock_keluar_pcs
                
            res.sander_stock_masuk_pcs = sander_stock_masuk_pcs
            res.re_stock_masuk_pcs = res.re_stock_keluar_pcs

    @api.depends('product_id')
    def _get_stock_awal(self):
        for res in self:
            stock_awal_pcs = 0

            if res.product_id:
                source_ids = self.env['pwk.mutasi.assembling.finishing.proses2'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.assembling.finishing.proses2'].search([
                        ('reference.date','<',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])
                            
                if source_ids:
                    stock_awal_pcs = source_ids[0].stock_akhir_pcs

            res.stock_awal_pcs = stock_awal_pcs

    @api.depends('stock_awal_pcs','sander_stock_masuk_pcs','re_stock_masuk_pcs','gs_stock_keluar_pcs','lain_stock_keluar_pcs','re_stock_keluar_pcs')
    def _get_stock_akhir(self):
        for res in self:
            res.stock_akhir_pcs = res.stock_awal_pcs + res.sander_stock_masuk_pcs + res.re_stock_masuk_pcs - res.gs_stock_keluar_pcs - res.lain_stock_keluar_pcs - res.re_stock_keluar_pcs

class PwkMutasiAssemblingFinishingKalibrasi(models.Model):
    _name = "pwk.mutasi.assembling.finishing.kalibrasi"

    reference = fields.Many2one('pwk.mutasi.assembling.finishing', 'Reference')
    product_id = fields.Many2one('product.product', 'Product')
    tebal = fields.Float(compute="_get_product_attribute", string='Tebal')
    lebar = fields.Float(compute="_get_product_attribute", string='Lebar')
    panjang = fields.Float(compute="_get_product_attribute", string='Panjang')
    grade = fields.Many2one(compute="_get_product_attribute", comodel_name='pwk.grade', string='Grade')
    stock_awal_pcs = fields.Float(compute="_get_stock_awal", string='Stok Awal')
    stock_awal_vol = fields.Float(compute="_get_volume", string='Stok Awal', digits=dp.get_precision('FourDecimal'))
    
    sander_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Sander (Pcs)')
    sander_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Sander (M3)', digits=dp.get_precision('FourDecimal'))
    sander_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Sander')
    sander_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Sander', digits=dp.get_precision('FourDecimal'))

    re_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Re (M3)', digits=dp.get_precision('FourDecimal'))
    re_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Re (Pcs)')
    re_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Re')
    re_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Re', digits=dp.get_precision('FourDecimal'))
    
    gs_stock_keluar_pcs = fields.Float('Stok Keluar GS (Pcs)')
    gs_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar GS (M3)', digits=dp.get_precision('FourDecimal'))
    gs_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar GS')
    gs_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar GS', digits=dp.get_precision('FourDecimal'))
    
    lain_stock_keluar_pcs = fields.Float('Stok Keluar Lain (Pcs)')
    lain_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Lain (M3)', digits=dp.get_precision('FourDecimal'))
    lain_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Lain')
    lain_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Lain', digits=dp.get_precision('FourDecimal'))

    sander2_stock_keluar_pcs = fields.Float('Stok Keluar Sander2 (Pcs)')
    sander2_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Sander2 (M3)', digits=dp.get_precision('FourDecimal'))
    sander2_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Sander2')
    sander2_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Sander2', digits=dp.get_precision('FourDecimal'))

    re_stock_keluar_pcs = fields.Float('Stok Keluar Re (Pcs)')
    re_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Re (M3)', digits=dp.get_precision('FourDecimal'))
    re_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Re')
    re_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Re', digits=dp.get_precision('FourDecimal'))    

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

    @api.depends('stock_awal_pcs',
        'sander_stock_masuk_pcs','re_stock_masuk_pcs',
        'gs_stock_keluar_pcs','lain_stock_keluar_pcs','re_stock_keluar_pcs',
        'sander_acc_stock_masuk_pcs','re_acc_stock_masuk_pcs',
        'gs_acc_stock_keluar_pcs','lain_acc_stock_keluar_pcs','sander2_acc_stock_keluar_pcs','re_acc_stock_keluar_pcs',
        'stock_akhir_pcs')
    def _get_volume(self):
        for res in self:
            res.stock_awal_vol = res.stock_awal_pcs * res.tebal * res.lebar * res.panjang / 1000000000

            res.sander_stock_masuk_vol = res.sander_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_stock_masuk_vol = res.re_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.sander_acc_stock_masuk_vol = res.sander_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_acc_stock_masuk_vol = res.re_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.gs_stock_keluar_vol = res.gs_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000            
            res.lain_stock_keluar_vol = res.lain_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_stock_keluar_vol = res.lain_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.gs_acc_stock_keluar_vol = res.gs_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000            
            res.lain_acc_stock_keluar_vol = res.lain_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_acc_stock_keluar_vol = res.re_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.stock_akhir_vol = res.stock_akhir_pcs * res.tebal * res.lebar * res.panjang / 1000000000

    @api.depends('stock_awal_pcs','sander_stock_masuk_pcs','re_stock_masuk_pcs',
        'gs_stock_keluar_pcs','lain_stock_keluar_pcs','sander2_stock_keluar_pcs','re_stock_keluar_pcs')
    def _get_acc(self):
        for res in self:
            sander_acc_stock_masuk_pcs = 0
            re_acc_stock_masuk_pcs = 0
            gs_acc_stock_keluar_pcs = 0
            lain_acc_stock_keluar_pcs = 0
            sander2_acc_stock_keluar_pcs = 0
            re_acc_stock_keluar_pcs = 0

            if res.product_id:
                source_ids = self.env['pwk.mutasi.assembling.finishing.kalibrasi'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.assembling.finishing.kalibrasi'].search([
                        ('reference.date','<',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])

                if source_ids:
                    sander_acc_stock_masuk_pcs = source_ids[0].sander_acc_stock_masuk_pcs
                    re_acc_stock_masuk_pcs = source_ids[0].re_acc_stock_masuk_pcs
                    gs_acc_stock_keluar_pcs = source_ids[0].gs_acc_stock_keluar_pcs
                    lain_acc_stock_keluar_pcs = source_ids[0].lain_acc_stock_keluar_pcs
                    sander2_acc_stock_keluar_pcs = source_ids[0].sander2_acc_stock_keluar_pcs
                    rer_acc_stock_keluar_pcs = source_ids[0].re_acc_stock_keluar_pcs

            res.sander_acc_stock_masuk_pcs = sander_acc_stock_masuk_pcs + res.sander_stock_masuk_pcs
            res.re_acc_stock_masuk_pcs = re_acc_stock_masuk_pcs + res.re_stock_masuk_pcs
            res.gs_acc_stock_keluar_pcs = gs_acc_stock_keluar_pcs + res.gs_stock_keluar_pcs
            res.lain_acc_stock_keluar_pcs = lain_acc_stock_keluar_pcs + res.lain_stock_keluar_pcs
            res.sander2_acc_stock_keluar_pcs = sander2_acc_stock_keluar_pcs + res.sander2_stock_keluar_pcs
            res.re_acc_stock_keluar_pcs = re_acc_stock_keluar_pcs + res.re_stock_keluar_pcs

    @api.depends('product_id')
    def _get_stock_masuk(self):
        for res in self:
            sander_stock_masuk_pcs = 0

            if res.product_id:
                if res.reference.gs1_selection == "Veneer GS":
                    source_ids = self.env['pwk.mutasi.assembling.finishing.unsander'].search([
                        ('reference.date','=',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])

                    if source_ids:
                        sander_stock_masuk_pcs = source_ids[0].sander_stock_keluar_pcs
                
            res.sander_stock_masuk_pcs = sander_stock_masuk_pcs
            res.re_stock_masuk_pcs = res.re_stock_keluar_pcs

    @api.depends('product_id')
    def _get_stock_awal(self):
        for res in self:
            stock_awal_pcs = 0

            if res.product_id:
                source_ids = self.env['pwk.mutasi.assembling.finishing.kalibrasi'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.assembling.finishing.kalibrasi'].search([
                        ('reference.date','<',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])
                            
                if source_ids:
                    stock_awal_pcs = source_ids[0].stock_akhir_pcs

            res.stock_awal_pcs = stock_awal_pcs

    @api.depends('stock_awal_pcs','sander_stock_masuk_pcs','re_stock_masuk_pcs','gs_stock_keluar_pcs','lain_stock_keluar_pcs','re_stock_keluar_pcs')
    def _get_stock_akhir(self):
        for res in self:
            res.stock_akhir_pcs = res.stock_awal_pcs + res.sander_stock_masuk_pcs + res.re_stock_masuk_pcs - res.gs_stock_keluar_pcs - res.lain_stock_keluar_pcs - res.re_stock_keluar_pcs            

class PwkMutasiAssemblingFinishingKalibrasi2(models.Model):
    _name = "pwk.mutasi.assembling.finishing.kalibrasi2"

    reference = fields.Many2one('pwk.mutasi.assembling.finishing', 'Reference')
    product_id = fields.Many2one('product.product', 'Product')
    tebal = fields.Float(compute="_get_product_attribute", string='Tebal')
    lebar = fields.Float(compute="_get_product_attribute", string='Lebar')
    panjang = fields.Float(compute="_get_product_attribute", string='Panjang')
    grade = fields.Many2one(compute="_get_product_attribute", comodel_name='pwk.grade', string='Grade')
    stock_awal_pcs = fields.Float(compute="_get_stock_awal", string='Stok Awal')
    stock_awal_vol = fields.Float(compute="_get_volume", string='Stok Awal', digits=dp.get_precision('FourDecimal'))
    
    sander_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Sander (Pcs)')
    sander_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Sander (M3)', digits=dp.get_precision('FourDecimal'))
    sander_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Sander')
    sander_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Sander', digits=dp.get_precision('FourDecimal'))

    re_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Re (M3)', digits=dp.get_precision('FourDecimal'))
    re_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Re (Pcs)')
    re_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Re')
    re_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Re', digits=dp.get_precision('FourDecimal'))
    
    sizer_stock_keluar_pcs = fields.Float('Stok Keluar Sizer (Pcs)')
    sizer_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Sizer (M3)', digits=dp.get_precision('FourDecimal'))
    sizer_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Sizer')
    sizer_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Sizer', digits=dp.get_precision('FourDecimal'))
    
    tipis_stock_keluar_pcs = fields.Float('Stok Keluar Tipis (Pcs)')
    tipis_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Tipis (M3)', digits=dp.get_precision('FourDecimal'))
    tipis_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Tipis')
    tipis_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Tipis', digits=dp.get_precision('FourDecimal'))

    qc_stock_keluar_pcs = fields.Float('Stok Keluar QC')
    qc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar QC', digits=dp.get_precision('FourDecimal'))
    qc_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar QC')
    qc_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar QC', digits=dp.get_precision('FourDecimal'))

    re_stock_keluar_pcs = fields.Float('Stok Keluar Re (Pcs)')
    re_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Re (M3)', digits=dp.get_precision('FourDecimal'))
    re_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Re')
    re_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Re', digits=dp.get_precision('FourDecimal'))    

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

    @api.depends('stock_awal_pcs',
        'sander_stock_masuk_pcs','sander_acc_stock_masuk_pcs',
        're_stock_masuk_pcs','re_acc_stock_masuk_pcs',
        'sizer_stock_keluar_pcs','sizer_acc_stock_keluar_pcs',
        'tipis_stock_keluar_pcs','tipis_acc_stock_keluar_pcs',
        're_stock_keluar_pcs','re_acc_stock_keluar_pcs',
        'stock_akhir_pcs')
    def _get_volume(self):
        for res in self:
            res.stock_awal_vol = res.stock_awal_pcs * res.tebal * res.lebar * res.panjang / 1000000000

            res.sander_stock_masuk_vol = res.sander_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_stock_masuk_vol = res.re_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.sander_acc_stock_masuk_vol = res.sander_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_acc_stock_masuk_vol = res.re_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.sizer_stock_keluar_vol = res.sizer_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000            
            res.tipis_stock_keluar_vol = res.tipis_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.qc_stock_keluar_vol = res.qc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_stock_keluar_vol = res.lain_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.sizer_acc_stock_keluar_vol = res.sizer_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000            
            res.tipis_acc_stock_keluar_vol = res.tipis_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.qc_acc_stock_keluar_vol = res.qc_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_acc_stock_keluar_vol = res.re_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.stock_akhir_vol = res.stock_akhir_pcs * res.tebal * res.lebar * res.panjang / 1000000000

    @api.depends('stock_awal_pcs',
        'sander_stock_masuk_pcs','re_stock_masuk_pcs',
        'sizer_stock_keluar_pcs','tipis_stock_keluar_pcs','qc_stock_keluar_pcs','re_stock_keluar_pcs')
    def _get_acc(self):
        for res in self:
            sander_acc_stock_masuk_pcs = 0
            re_acc_stock_masuk_pcs = 0
            sizer_acc_stock_keluar_pcs = 0
            tipis_acc_stock_keluar_pcs = 0
            qc_acc_stock_keluar_pcs = 0
            re_acc_stock_keluar_pcs = 0

            if res.product_id:
                source_ids = self.env['pwk.mutasi.assembling.finishing.kalibrasi2'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.assembling.finishing.kalibrasi2'].search([
                        ('reference.date','<',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])

                if source_ids:
                    sander_acc_stock_masuk_pcs = source_ids[0].sander_acc_stock_masuk_pcs
                    re_acc_stock_masuk_pcs = source_ids[0].re_acc_stock_masuk_pcs
                    sizer_acc_stock_keluar_pcs = source_ids[0].sizer_acc_stock_keluar_pcs
                    tipis_acc_stock_keluar_pcs = source_ids[0].tipis_acc_stock_keluar_pcs
                    qc_acc_stock_keluar_pcs = source_ids[0].qc_acc_stock_keluar_pcs
                    rer_acc_stock_keluar_pcs = source_ids[0].re_acc_stock_keluar_pcs

            res.sander_acc_stock_masuk_pcs = sander_acc_stock_masuk_pcs + res.sander_stock_masuk_pcs
            res.re_acc_stock_masuk_pcs = re_acc_stock_masuk_pcs + res.re_stock_masuk_pcs
            res.sizer_acc_stock_keluar_pcs = sizer_acc_stock_keluar_pcs + res.sizer_stock_keluar_pcs
            res.tipis_acc_stock_keluar_pcs = tipis_acc_stock_keluar_pcs + res.tipis_stock_keluar_pcs
            res.qc_acc_stock_keluar_pcs = qc_acc_stock_keluar_pcs + res.qc_acc_stock_keluar_pcs
            res.re_acc_stock_keluar_pcs = re_acc_stock_keluar_pcs + res.re_stock_keluar_pcs

    @api.depends('product_id')
    def _get_stock_masuk(self):
        for res in self:
            sander_stock_masuk_pcs = 0

            if res.product_id:
                source_ids = self.env['pwk.mutasi.assembling.finishing.kalibrasi'].search([
                    ('reference.date','=',res.reference.date),
                    ('product_id','=',res.product_id.id)
                    ])

                if source_ids:
                    sander_stock_masuk_pcs += source_ids[0].sander2_stock_keluar_pcs

                gs2_source_ids = self.env['pwk.mutasi.assembling.finishing.gs2'].search([
                    ('reference.date','=',res.reference.date),
                    ('product_id','=',res.product_id.id)
                    ])

                if gs2_source_ids:
                    sander_stock_masuk_pcs += gs2_source_ids[0].sk_stock_keluar_pcs
                
            res.sander_stock_masuk_pcs = sander_stock_masuk_pcs
            res.re_stock_masuk_pcs = res.re_stock_keluar_pcs

    @api.depends('product_id')
    def _get_stock_awal(self):
        for res in self:
            stock_awal_pcs = 0

            if res.product_id:
                source_ids = self.env['pwk.mutasi.assembling.finishing.kalibrasi2'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.assembling.finishing.kalibrasi2'].search([
                        ('reference.date','<',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])
                            
                if source_ids:
                    stock_awal_pcs = source_ids[0].stock_akhir_pcs

            res.stock_awal_pcs = stock_awal_pcs

    @api.depends('stock_awal_pcs',
        'sander_stock_masuk_pcs','re_stock_masuk_pcs',
        'sizer_stock_keluar_pcs','tipis_stock_keluar_pcs','qc_stock_keluar_pcs','re_stock_keluar_pcs')
    def _get_stock_akhir(self):
        for res in self:
            res.stock_akhir_pcs = res.stock_awal_pcs + res.sander_stock_masuk_pcs + res.re_stock_masuk_pcs - res.sizer_stock_keluar_pcs - res.tipis_stock_keluar_pcs - res.qc_stock_keluar_pcs - res.re_stock_keluar_pcs            

class PwkMutasiAssemblingFinishingSizer(models.Model):
    _name = "pwk.mutasi.assembling.finishing.sizer"

    reference = fields.Many2one('pwk.mutasi.assembling.finishing', 'Reference')
    product_id = fields.Many2one('product.product', 'Product')
    tebal = fields.Float(compute="_get_product_attribute", string='Tebal')
    lebar = fields.Float(compute="_get_product_attribute", string='Lebar')
    panjang = fields.Float(compute="_get_product_attribute", string='Panjang')
    grade = fields.Many2one(compute="_get_product_attribute", comodel_name='pwk.grade', string='Grade')
    stock_awal_pcs = fields.Float(compute="_get_stock_awal", string='Stok Awal')
    stock_awal_vol = fields.Float(compute="_get_volume", string='Stok Awal', digits=dp.get_precision('FourDecimal'))
    
    sander2_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Sander2 (Pcs)')
    sander2_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Sander2 (M3)', digits=dp.get_precision('FourDecimal'))
    sander2_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Sander2')
    sander2_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Sander2', digits=dp.get_precision('FourDecimal'))

    manual_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Manual (Pcs)')
    manual_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Manual (M3)', digits=dp.get_precision('FourDecimal'))
    manual_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Manual')
    manual_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Manual', digits=dp.get_precision('FourDecimal'))

    hot_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Hot (Pcs)')
    hot_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Hot (M3)', digits=dp.get_precision('FourDecimal'))
    hot_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Hot')
    hot_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Hot', digits=dp.get_precision('FourDecimal'))

    re_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Re (M3)', digits=dp.get_precision('FourDecimal'))
    re_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Re (Pcs)')
    re_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Re')
    re_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Re', digits=dp.get_precision('FourDecimal'))
    
    sander_stock_keluar_pcs = fields.Float('Stok Keluar Sander (Pcs)')
    sander_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Sander (M3)', digits=dp.get_precision('FourDecimal'))
    sander_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Sander')
    sander_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Sander', digits=dp.get_precision('FourDecimal'))

    grading_stock_keluar_pcs = fields.Float('Stok Keluar Grading (Pcs)')
    grading_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Grading (M3)', digits=dp.get_precision('FourDecimal'))
    grading_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Grading')
    grading_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Grading', digits=dp.get_precision('FourDecimal'))
    
    lain_stock_keluar_pcs = fields.Float('Stok Keluar Lain (Pcs)')
    lain_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Lain (M3)', digits=dp.get_precision('FourDecimal'))
    lain_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Lain')
    lain_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Lain', digits=dp.get_precision('FourDecimal'))

    qc_stock_keluar_pcs = fields.Float('Stok Keluar QC')
    qc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar QC', digits=dp.get_precision('FourDecimal'))
    qc_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar QC')
    qc_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar QC', digits=dp.get_precision('FourDecimal'))

    re_stock_keluar_pcs = fields.Float('Stok Keluar Re (Pcs)')
    re_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Re (M3)', digits=dp.get_precision('FourDecimal'))
    re_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Re')
    re_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Re', digits=dp.get_precision('FourDecimal'))    

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

    @api.depends('stock_awal_pcs',
        'sander2_stock_masuk_pcs','sander2_stock_masuk_pcs',
        'manual_stock_masuk_pcs','manual_acc_stock_masuk_pcs',
        'hot_stock_masuk_pcs','hot_acc_stock_masuk_pcs',
        're_stock_masuk_pcs','re_acc_stock_masuk_pcs',
        'sander_stock_keluar_pcs','sander_acc_stock_keluar_pcs',
        'grading_stock_keluar_pcs','grading_acc_stock_keluar_pcs',
        'lain_stock_keluar_pcs','lain_acc_stock_keluar_pcs',
        're_stock_keluar_pcs','re_acc_stock_keluar_pcs',
        'qc_stock_keluar_pcs','qc_acc_stock_keluar_pcs',
        'stock_akhir_pcs')
    def _get_volume(self):
        for res in self:
            res.stock_awal_vol = res.stock_awal_pcs * res.tebal * res.lebar * res.panjang / 1000000000

            res.hot_stock_masuk_vol = res.hot_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.sander2_stock_masuk_vol = res.sander2_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.manual_stock_masuk_vol = res.manual_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_stock_masuk_vol = res.re_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.hot_acc_stock_masuk_vol = res.hot_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.sander2_acc_stock_masuk_vol = res.sander2_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.manual_acc_stock_masuk_vol = res.manual_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_acc_stock_masuk_vol = res.re_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.sander_stock_keluar_vol = res.sander_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000            
            res.grading_stock_keluar_vol = res.grading_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000            
            res.lain_stock_keluar_vol = res.lain_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.qc_stock_keluar_vol = res.qc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_stock_keluar_vol = res.lain_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.sander_acc_stock_keluar_vol = res.sander_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.grading_acc_stock_keluar_vol = res.grading_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.lain_acc_stock_keluar_vol = res.lain_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.qc_acc_stock_keluar_pcs = res.qc_acc_stock_keluar_vol * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_acc_stock_keluar_vol = res.re_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.stock_akhir_vol = res.stock_akhir_pcs * res.tebal * res.lebar * res.panjang / 1000000000

    @api.depends('stock_awal_pcs',
        'hot_stock_masuk_pcs','sander2_stock_masuk_pcs','manual_stock_masuk_pcs','re_stock_masuk_pcs',
        'sander_stock_keluar_pcs','grading_stock_keluar_pcs','lain_stock_keluar_pcs','qc_stock_keluar_pcs','re_stock_keluar_pcs')
    def _get_acc(self):
        for res in self:
            hot_acc_stock_masuk_pcs = 0
            sander2_acc_stock_masuk_pcs = 0
            manual_acc_stock_masuk_pcs = 0
            re_acc_stock_masuk_pcs = 0
            sander_acc_stock_keluar_pcs = 0
            grading_acc_stock_keluar_pcs = 0
            lain_acc_stock_keluar_pcs = 0
            qc_acc_stock_keluar_pcs = 0
            re_acc_stock_keluar_pcs = 0

            if res.product_id:
                source_ids = self.env['pwk.mutasi.assembling.finishing.sizer'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.assembling.finishing.sizer'].search([
                        ('reference.date','<',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])

                if source_ids:
                    hot_acc_stock_masuk_pcs = source_ids[0].hot_acc_stock_masuk_pcs
                    sander2_acc_stock_masuk_pcs = source_ids[0].sander2_acc_stock_masuk_pcs
                    manual_acc_stock_masuk_pcs = source_ids[0].manual_acc_stock_masuk_pcs
                    re_acc_stock_masuk_pcs = source_ids[0].re_acc_stock_masuk_pcs
                    sander_acc_stock_keluar_pcs = source_ids[0].sander_acc_stock_keluar_pcs
                    grading_acc_stock_keluar_pcs = source_ids[0].grading_acc_stock_keluar_pcs
                    lain_acc_stock_keluar_pcs = source_ids[0].lain_acc_stock_keluar_pcs
                    qc_acc_stock_keluar_pcs = source_ids[0].qc_acc_stock_keluar_pcs
                    rer_acc_stock_keluar_pcs = source_ids[0].re_acc_stock_keluar_pcs

            res.hot_acc_stock_masuk_pcs = hot_acc_stock_masuk_pcs + res.hot_stock_masuk_pcs
            res.sander2_acc_stock_masuk_pcs = sander2_acc_stock_masuk_pcs + res.sander2_stock_masuk_pcs
            res.manual_acc_stock_masuk_pcs = manual_acc_stock_masuk_pcs + res.manual_stock_masuk_pcs
            res.re_acc_stock_masuk_pcs = re_acc_stock_masuk_pcs + res.re_stock_masuk_pcs
            res.sander_acc_stock_keluar_pcs = sander_acc_stock_keluar_pcs + res.sander_stock_keluar_pcs
            res.grading_acc_stock_keluar_pcs = grading_acc_stock_keluar_pcs + res.grading_stock_keluar_pcs
            res.lain_acc_stock_keluar_pcs = lain_acc_stock_keluar_pcs + res.lain_stock_keluar_pcs
            res.qc_acc_stock_keluar_pcs = qc_acc_stock_keluar_pcs + res.qc_stock_keluar_pcs
            res.re_acc_stock_keluar_pcs = re_acc_stock_keluar_pcs + res.re_stock_keluar_pcs

    @api.depends('product_id')
    def _get_stock_masuk(self):
        for res in self:
            hot_stock_masuk_pcs = 0
            sander2_stock_masuk_pcs = 0
            manual_stock_masuk_pcs = 0

            if res.product_id:
                if res.reference.gs1_selection == "Veneer GS":
                    source_ids = self.env['pwk.mutasi.assembling.finishing.gs2'].search([
                        ('reference.date','=',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])

                    if source_ids:
                        hot_stock_masuk_pcs = source_ids[0].hot_stock_keluar_pcs

                sander2_source_ids = self.env['pwk.mutasi.assembling.finishing.kalibrasi2'].search([
                        ('reference.date','=',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])

                if sander2_source_ids:
                    sander2_stock_masuk_pcs = source_ids[0].sander2_stock_keluar_pcs
                    manual_stock_masuk_pcs = source_ids[0].manual_stock_keluar_pcs
                
            res.hot_stock_masuk_pcs = hot_stock_masuk_pcs
            res.re_stock_masuk_pcs = res.re_stock_keluar_pcs
            res.sander2_stock_masuk_pcs = sander2_stock_masuk_pcs
            res.manual_stock_masuk_pcs = manual_stock_masuk_pcs

    @api.depends('product_id')
    def _get_stock_awal(self):
        for res in self:
            stock_awal_pcs = 0

            if res.product_id:
                source_ids = self.env['pwk.mutasi.assembling.finishing.sizer'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.assembling.finishing.sizer'].search([
                        ('reference.date','<',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])
                            
                if source_ids:
                    stock_awal_pcs = source_ids[0].stock_akhir_pcs

            res.stock_awal_pcs = stock_awal_pcs

    @api.depends('stock_awal_pcs',
        'hot_stock_masuk_pcs','re_stock_masuk_pcs','manual_stock_masuk_pcs','sander2_stock_masuk_pcs'
        'sander_stock_keluar_pcs','grading_stock_keluar_pcs','lain_stock_keluar_pcs','qc_stock_keluar_pcs','re_stock_keluar_pcs')
    def _get_stock_akhir(self):
        for res in self:
            res.stock_akhir_pcs = res.stock_awal_pcs + res.hot_stock_masuk_pcs + res.re_stock_masuk_pcs + res.manual_stock_masuk_pcs + res.sander2_stock_masuk_pcs- res.sander_stock_keluar_pcs - res.grading_stock_keluar_pcs - res.lain_stock_keluar_pcs - res.qc_stock_keluar_pcs - res.re_stock_keluar_pcs

class PwkMutasiAssemblingFinishingFinish(models.Model):
    _name = "pwk.mutasi.assembling.finishing.finish"

    reference = fields.Many2one('pwk.mutasi.assembling.finishing', 'Reference')
    product_id = fields.Many2one('product.product', 'Product')
    tebal = fields.Float(compute="_get_product_attribute", string='Tebal')
    lebar = fields.Float(compute="_get_product_attribute", string='Lebar')
    panjang = fields.Float(compute="_get_product_attribute", string='Panjang')
    grade = fields.Many2one(compute="_get_product_attribute", comodel_name='pwk.grade', string='Grade')
    stock_awal_pcs = fields.Float(compute="_get_stock_awal", string='Stok Awal')
    stock_awal_vol = fields.Float(compute="_get_volume", string='Stok Awal', digits=dp.get_precision('FourDecimal'))
    
    sizer_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Sizer (Pcs)')
    sizer_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Sizer (M3)', digits=dp.get_precision('FourDecimal'))
    sizer_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Sizer')
    sizer_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Sizer', digits=dp.get_precision('FourDecimal'))

    re_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Re (M3)', digits=dp.get_precision('FourDecimal'))
    re_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Re (Pcs)')
    re_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Re')
    re_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Re', digits=dp.get_precision('FourDecimal'))
    
    grading_stock_keluar_pcs = fields.Float('Stok Keluar Grading (Pcs)')
    grading_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Grading (M3)', digits=dp.get_precision('FourDecimal'))
    grading_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Grading')
    grading_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Grading', digits=dp.get_precision('FourDecimal'))
    
    lain_stock_keluar_pcs = fields.Float('Stok Keluar Lain (Pcs)')
    lain_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Lain (M3)', digits=dp.get_precision('FourDecimal'))
    lain_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Lain')
    lain_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Lain', digits=dp.get_precision('FourDecimal'))

    re_stock_keluar_pcs = fields.Float('Stok Keluar Re (Pcs)')
    re_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Re (M3)', digits=dp.get_precision('FourDecimal'))
    re_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Re')
    re_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Re', digits=dp.get_precision('FourDecimal'))    

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

    @api.depends('stock_awal_pcs',
        'sizer_stock_masuk_pcs','re_stock_masuk_pcs',
        'grading_stock_keluar_pcs','lain_stock_keluar_pcs','re_stock_keluar_pcs',
        'sizer_acc_stock_masuk_pcs','re_acc_stock_masuk_pcs',
        'grading_acc_stock_keluar_pcs','lain_acc_stock_keluar_pcs','re_acc_stock_keluar_pcs',
        'stock_akhir_pcs')
    def _get_volume(self):
        for res in self:
            res.stock_awal_vol = res.stock_awal_pcs * res.tebal * res.lebar * res.panjang / 1000000000

            res.sizer_stock_masuk_vol = res.sizer_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_stock_masuk_vol = res.re_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.sizer_acc_stock_masuk_vol = res.sizer_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_acc_stock_masuk_vol = res.re_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
                    
            res.grading_stock_keluar_vol = res.grading_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000            
            res.lain_stock_keluar_vol = res.lain_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_stock_keluar_vol = res.lain_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000            
            res.grading_acc_stock_keluar_vol = res.grading_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.lain_acc_stock_keluar_vol = res.lain_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_acc_stock_keluar_vol = res.re_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.stock_akhir_vol = res.stock_akhir_pcs * res.tebal * res.lebar * res.panjang / 1000000000

    @api.depends('stock_awal_pcs','sizer_stock_masuk_pcs','re_stock_masuk_pcs','grading_stock_keluar_pcs','lain_stock_keluar_pcs','re_stock_keluar_pcs')
    def _get_acc(self):
        for res in self:
            sizer_acc_stock_masuk_pcs = 0
            re_acc_stock_masuk_pcs = 0
            grading_acc_stock_keluar_pcs = 0
            lain_acc_stock_keluar_pcs = 0
            re_acc_stock_keluar_pcs = 0

            if res.product_id:
                source_ids = self.env['pwk.mutasi.assembling.finishing.sizer'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.assembling.finishing.sizer'].search([
                        ('reference.date','<',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])

                if source_ids:
                    sizer_acc_stock_masuk_pcs = source_ids[0].hot_acc_stock_masuk_pcs
                    re_acc_stock_masuk_pcs = source_ids[0].re_acc_stock_masuk_pcs
                    grading_acc_stock_keluar_pcs = source_ids[0].grading_acc_stock_keluar_pcs
                    lain_acc_stock_keluar_pcs = source_ids[0].lain_acc_stock_keluar_pcs
                    rer_acc_stock_keluar_pcs = source_ids[0].re_acc_stock_keluar_pcs

            res.sizer_acc_stock_masuk_pcs = sizer_acc_stock_masuk_pcs + res.sizer_stock_masuk_pcs
            res.re_acc_stock_masuk_pcs = re_acc_stock_masuk_pcs + res.re_stock_masuk_pcs
            res.grading_acc_stock_keluar_pcs = grading_acc_stock_keluar_pcs + res.grading_stock_keluar_pcs
            res.lain_acc_stock_keluar_pcs = lain_acc_stock_keluar_pcs + res.lain_stock_keluar_pcs
            res.re_acc_stock_keluar_pcs = re_acc_stock_keluar_pcs + res.re_stock_keluar_pcs

    @api.depends('product_id')
    def _get_stock_masuk(self):
        for res in self:
            sizer_stock_masuk_pcs = 0

            if res.product_id:
                if res.reference.gs1_selection == "Veneer GS":
                    source_ids = self.env['pwk.mutasi.assembling.finishing.sizer'].search([
                        ('reference.date','=',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])

                    if source_ids:
                        sizer_stock_masuk_pcs = source_ids[0].sander_stock_keluar_pcs
                
            res.sizer_stock_masuk_pcs = sizer_stock_masuk_pcs
            res.re_stock_masuk_pcs = res.re_stock_keluar_pcs

    @api.depends('product_id')
    def _get_stock_awal(self):
        for res in self:
            stock_awal_pcs = 0

            if res.product_id:
                source_ids = self.env['pwk.mutasi.assembling.finishing.finish'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.assembling.finishing.finish'].search([
                        ('reference.date','<',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])
                            
                if source_ids:
                    stock_awal_pcs = source_ids[0].stock_akhir_pcs

            res.stock_awal_pcs = stock_awal_pcs

    @api.depends('stock_awal_pcs','sizer_stock_masuk_pcs','re_stock_masuk_pcs','grading_stock_keluar_pcs','lain_stock_keluar_pcs','re_stock_keluar_pcs')
    def _get_stock_akhir(self):
        for res in self:
            res.stock_akhir_pcs = res.stock_awal_pcs + res.sizer_stock_masuk_pcs + res.re_stock_masuk_pcs- res.grading_stock_keluar_pcs - res.lain_stock_keluar_pcs - res.re_stock_keluar_pcs

class PwkMutasiAssemblingFinishingReproses(models.Model):
    _name = "pwk.mutasi.assembling.finishing.reproses"

    reference = fields.Many2one('pwk.mutasi.assembling.finishing', 'Reference')
    product_id = fields.Many2one('product.product', 'Product')
    tebal = fields.Float(compute="_get_product_attribute", string='Tebal')
    lebar = fields.Float(compute="_get_product_attribute", string='Lebar')
    panjang = fields.Float(compute="_get_product_attribute", string='Panjang')
    grade = fields.Many2one(compute="_get_product_attribute", comodel_name='pwk.grade', string='Grade')
    stock_awal_pcs = fields.Float(compute="_get_stock_awal", string='Stok Awal')
    stock_awal_vol = fields.Float(compute="_get_volume", string='Stok Awal', digits=dp.get_precision('FourDecimal'))
    
    stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk (M3)', digits=dp.get_precision('FourDecimal'))
    stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk (Pcs)')
    acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk')
    acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk', digits=dp.get_precision('FourDecimal'))
    
    stock_keluar_pcs = fields.Float('Stok Keluar Grading (Pcs)')
    stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar (M3)', digits=dp.get_precision('FourDecimal'))
    acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar')
    acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar', digits=dp.get_precision('FourDecimal'))
    
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

    @api.depends('stock_awal_pcs','stock_masuk_pcs','stock_keluar_pcs','acc_stock_masuk_pcs','acc_stock_keluar_pcs','stock_akhir_pcs')
    def _get_volume(self):
        for res in self:
            res.stock_awal_vol = res.stock_awal_pcs * res.tebal * res.lebar * res.panjang / 1000000000

            res.stock_masuk_vol = res.stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000            
            res.acc_stock_masuk_vol = res.acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
                    
            res.stock_keluar_vol = res.stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000                        
            res.acc_stock_keluar_vol = res.acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.stock_akhir_vol = res.stock_akhir_pcs * res.tebal * res.lebar * res.panjang / 1000000000

    @api.depends('stock_masuk_pcs','stock_keluar_pcs','acc_stock_masuk_pcs','acc_stock_keluar_pcs')
    def _get_acc(self):
        for res in self:
            acc_stock_masuk_pcs = 0            
            acc_stock_keluar_pcs = 0

            if res.product_id:
                source_ids = self.env['pwk.mutasi.assembling.finishing.reproses'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.assembling.finishing.reproses'].search([
                        ('reference.date','<',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])

                if source_ids:
                    acc_stock_masuk_pcs = source_ids[0].acc_stock_masuk_pcs
                    acc_stock_keluar_pcs = source_ids[0].acc_stock_keluar_pcs

            res.acc_stock_masuk_pcs = acc_stock_masuk_pcs + res.stock_masuk_pcs            
            res.acc_stock_keluar_pcs = acc_stock_keluar_pcs + res.stock_keluar_pcs

    @api.depends('product_id')
    def _get_stock_masuk(self):
        for res in self:
            stock_masuk_pcs = 0

            if res.product_id:
                if res.reference.gs1_selection == "Veneer GS":
                    source_ids = self.env['pwk.mutasi.sf.grading.line.revisi'].search([
                        ('reference.date','=',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])

                    if source_ids:
                        stock_masuk_pcs = source_ids[0].sander_stock_keluar_pcs
                
            res.stock_masuk_pcs = stock_masuk_pcs

    @api.depends('product_id')
    def _get_stock_awal(self):
        for res in self:
            stock_awal_pcs = 0

            if res.product_id:
                source_ids = self.env['pwk.mutasi.assembling.finishing.reproses'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.assembling.finishing.reproses'].search([
                        ('reference.date','<',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])
                            
                if source_ids:
                    stock_awal_pcs = source_ids[0].stock_akhir_pcs

            res.stock_awal_pcs = stock_awal_pcs

    @api.depends('stock_awal_pcs','stock_masuk_pcs','stock_keluar_pcs')
    def _get_stock_akhir(self):
        for res in self:
            res.stock_akhir_pcs = res.stock_awal_pcs + res.stock_masuk_pcs - res.stock_keluar_pcs

class PwkMutasiAssemblingFinishingCover(models.Model):
    _name = "pwk.mutasi.assembling.finishing.cover"

    reference = fields.Many2one('pwk.mutasi.assembling.finishing', 'Reference')
    product_id = fields.Many2one('product.product', 'Product')
    tebal = fields.Float(compute="_get_product_attribute", string='Tebal')
    lebar = fields.Float(compute="_get_product_attribute", string='Lebar')
    panjang = fields.Float(compute="_get_product_attribute", string='Panjang')
    grade = fields.Many2one(compute="_get_product_attribute", comodel_name='pwk.grade', string='Grade')
    stock_awal_pcs = fields.Float(compute="_get_stock_awal", string='Stok Awal')
    stock_awal_vol = fields.Float(compute="_get_volume", string='Stok Awal', digits=dp.get_precision('FourDecimal'))
    
    stock_masuk_pcs = fields.Float(string='Stok Masuk (Pcs)')
    stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk (M3)', digits=dp.get_precision('FourDecimal'))    
    acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk')
    acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk', digits=dp.get_precision('FourDecimal'))
    
    stock_keluar_pcs = fields.Float('Stok Keluar Grading (Pcs)')
    stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar (M3)', digits=dp.get_precision('FourDecimal'))
    acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar')
    acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar', digits=dp.get_precision('FourDecimal'))
    
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

    @api.depends('stock_awal_pcs','stock_masuk_pcs','stock_keluar_pcs','acc_stock_masuk_pcs','acc_stock_keluar_pcs','stock_akhir_pcs')
    def _get_volume(self):
        for res in self:
            res.stock_awal_vol = res.stock_awal_pcs * res.tebal * res.lebar * res.panjang / 1000000000

            res.stock_masuk_vol = res.stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000            
            res.acc_stock_masuk_vol = res.acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
                    
            res.stock_keluar_vol = res.stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000                        
            res.acc_stock_keluar_vol = res.acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.stock_akhir_vol = res.stock_akhir_pcs * res.tebal * res.lebar * res.panjang / 1000000000

    @api.depends('stock_masuk_pcs','stock_keluar_pcs','acc_stock_masuk_pcs','acc_stock_keluar_pcs')
    def _get_acc(self):
        for res in self:
            acc_stock_masuk_pcs = 0            
            acc_stock_keluar_pcs = 0

            if res.product_id:
                source_ids = self.env['pwk.mutasi.assembling.finishing.cover'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.assembling.finishing.cover'].search([
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

            if res.product_id:
                source_ids = self.env['pwk.mutasi.assembling.finishing.cover'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.assembling.finishing.cover'].search([
                        ('reference.date','<',res.reference.date),
                        ('product_id','=',res.product_id.id)
                        ])
                            
                if source_ids:
                    stock_awal_pcs = source_ids[0].stock_akhir_pcs

            res.stock_awal_pcs = stock_awal_pcs

    @api.depends('stock_awal_pcs','stock_masuk_pcs','stock_keluar_pcs')
    def _get_stock_akhir(self):
        for res in self:
            res.stock_akhir_pcs = res.stock_awal_pcs + res.stock_masuk_pcs - res.stock_keluar_pcs            

class PwkMutasiAssemblingFinishing(models.Model):    
    _name = "pwk.mutasi.assembling.finishing"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char('No. Dokumen', track_visibility="always")
    date = fields.Date('Tanggal', default=fields.Date.today(), track_visibility="always")
    user_id = fields.Many2one('res.users', string="Dibuat Oleh", default=lambda self: self.env.user, track_visibility="always")
    state = fields.Selection([('Draft','Draft'),('Approved','Approved')], string="Status", default="Draft", track_visibility="always")
    gs1_ids = fields.One2many('pwk.mutasi.assembling.finishing.gs1', 'reference', string="GS 1", track_visibility="always")
    gs2_ids = fields.One2many('pwk.mutasi.assembling.finishing.gs2', 'reference', string="GS 2", track_visibility="always")
    unsander_ids = fields.One2many('pwk.mutasi.assembling.finishing.unsander', 'reference', string="Unsander Kalibrasi", track_visibility="always")
    proses1_ids = fields.One2many('pwk.mutasi.assembling.finishing.proses1', 'reference', string="Proses Ulang 1", track_visibility="always")
    proses2_ids = fields.One2many('pwk.mutasi.assembling.finishing.proses2', 'reference', string="Proses Ulang 2", track_visibility="always")
    kalibrasi_ids = fields.One2many('pwk.mutasi.assembling.finishing.kalibrasi', 'reference', string="OK Kalibrasi", track_visibility="always")
    kalibrasi2_ids = fields.One2many('pwk.mutasi.assembling.finishing.kalibrasi2', 'reference', string="OK Kalibrasi 2", track_visibility="always")
    sizer_ids = fields.One2many('pwk.mutasi.assembling.finishing.sizer', 'reference', string="Double Sizer", track_visibility="always")
    finish_ids = fields.One2many('pwk.mutasi.assembling.finishing.finish', 'reference', string="Sander Finish", track_visibility="always")
    reproses_ids = fields.One2many('pwk.mutasi.assembling.finishing.reproses', 'reference', string="Re-Proses", track_visibility="always")
    cover_ids = fields.One2many('pwk.mutasi.assembling.finishing.cover', 'reference', string="Alas/Cover", track_visibility="always")
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
            existing_ids = self.env['pwk.mutasi.assembling.finishing.gs1'].search([
                ('reference', '=', self.id)
            ])
            
            if existing_ids:
                for existing in existing_ids:
                    existing.unlink()
                    
            source_ids = self.env['pwk.pemakaian.veneer.gs.line'].search([
                ('reference.date','=',res.date),
                ('keterangan','=','P1'),
                ])

            if not source_ids:
                source_ids = self.env['pwk.pemakaian.veneer.gs.line'].search([
                    ('reference.date','<',res.date - timedelta(1)),
                    ('keterangan','=','P1'),
                    ])

            if source_ids:
                for source in source_ids:
                    self.env['pwk.mutasi.assembling.finishing.gs1'].create({
                        'reference': res.id,
                        'product_id': source.bj_product_id.id,
                        })

    @api.multi
    def button_reload_gs2(self):
        for res in self:
            existing_ids = self.env['pwk.mutasi.assembling.finishing.gs2'].search([
                ('reference', '=', self.id)
            ])
            
            if existing_ids:
                for existing in existing_ids:
                    existing.unlink()
                    
            source_ids = self.env['pwk.pemakaian.veneer.gs.line'].search([
                ('reference.date','=',res.date),
                ('keterangan','=','P2'),
                ])

            if not source_ids:
                source_ids = self.env['pwk.pemakaian.veneer.gs.line'].search([
                    ('reference.date','<',res.date - timedelta(1)),
                    ('keterangan','=','P2'),
                    ])

            if source_ids:
                for source in source_ids:
                    self.env['pwk.mutasi.assembling.finishing.gs2'].create({
                        'reference': res.id,
                        'product_id': source.bj_product_id.id,
                        })

    @api.multi
    def button_reload_unsander(self):
        for res in self:
            existing_ids = self.env['pwk.mutasi.assembling.finishing.unsander'].search([
                ('reference', '=', self.id)
            ])
            
            if existing_ids:
                for existing in existing_ids:
                    existing.unlink()
                    
            source_ids = self.env['pwk.mutasi.assembling.finishing.gs1'].search([
                ('reference.date','=',res.date),
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.assembling.finishing.gs1'].search([
                    ('reference.date','<',res.date - timedelta(1)),
                    ])

            if source_ids:
                for source in source_ids:
                    self.env['pwk.mutasi.assembling.finishing.unsander'].create({
                        'reference': res.id,
                        'product_id': source.product_id.id,
                        })

    @api.multi
    def button_reload_proses1(self):
        for res in self:
            existing_ids = self.env['pwk.mutasi.assembling.finishing.proses1'].search([
                ('reference', '=', self.id)
            ])
            
            if existing_ids:
                for existing in existing_ids:
                    existing.unlink()
                    
            source_ids = self.env['pwk.mutasi.assembling.finishing.gs1'].search([
                ('reference.date','=',res.date),
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.assembling.finishing.gs1'].search([
                    ('reference.date','<',res.date - timedelta(1)),
                    ])

            if source_ids:
                for source in source_ids:
                    self.env['pwk.mutasi.assembling.finishing.proses1'].create({
                        'reference': res.id,
                        'product_id': source.product_id.id,
                        })

    @api.multi
    def button_reload_proses2(self):
        for res in self:
            existing_ids = self.env['pwk.mutasi.assembling.finishing.proses2'].search([
                ('reference', '=', self.id)
            ])
            
            if existing_ids:
                for existing in existing_ids:
                    existing.unlink()
                    
            source_ids = self.env['pwk.mutasi.assembling.finishing.proses1'].search([
                ('reference.date','=',res.date),
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.assembling.finishing.proses1'].search([
                    ('reference.date','<',res.date - timedelta(1)),
                    ])

            if source_ids:
                for source in source_ids:
                    if source.lup1_sander_stock_keluar_pcs > 0:
                        new_product_ids = self.env['product.product'].search([
                            ('goods_type', '=', source.product_id.goods_type),
                            ('jenis_core', '=', source.product_id.jenis_core.id),
                            ('tebal', '=', source.product_id.tebal - 1.5),
                            ('lebar', '=', source.product_id.lebar),
                            ('panjang', '=', source.product_id.panjang),
                            ('glue', '=', source.product_id.glue.id),
                            ('grade', '=', source.product_id.grade.id),
                        ])

                        if not new_product_ids:
                            new_product_ids = self.env['product.product'].create({
                                'goods_type': source.product_id.goods_type,
                                'jenis_core': source.product_id.jenis_core.id,
                                'tebal': source.product_id.tebal - 1.5,
                                'lebar': source.product_id.lebar,
                                'panjang' : source.product_id.panjang,
                                'glue': source.product_id.glue.id,
                                'grade': source.product_id.grade.id,
                                'name': source.product_id.goods_type + ' ' + source.product_id.jenis_core.name + ' ' + str(source.product_id.tebal) + 'mm x ' + str(source.product_id.lebar) + ' x ' + str(source.product_id.panjang) + ' ' + source.product_id.glue.name + ' ' + source.product_id.grade.name
                            })

                            if new_product_ids:
                                self.env['pwk.mutasi.assembling.finishing.proses2'].create({
                                    'reference': res.id,
                                    'product_id': source.product_id.id,
                                    'new_product_id': new_product_ids[0].id,
                                    'keterangan': 'LUP1'
                                    })

                    if source.lup2_sander_stock_keluar_pcs > 0:
                        new_product_ids = self.env['product.product'].search([
                            ('goods_type', '=', source.product_id.goods_type),
                            ('jenis_core', '=', source.product_id.jenis_core.id),
                            ('tebal', '=', source.product_id.tebal - 1.2),
                            ('lebar', '=', source.product_id.lebar),
                            ('panjang', '=', source.product_id.panjang),
                            ('glue', '=', source.product_id.glue.id),
                            ('grade', '=', source.product_id.grade.id),
                        ])

                        if not new_product_ids:
                            new_product_ids = self.env['product.product'].create({
                                'goods_type': source.product_id.goods_type,
                                'jenis_core': source.product_id.jenis_core.id,
                                'tebal': source.product_id.tebal - 1.2,
                                'lebar': source.product_id.lebar,
                                'panjang' : source.product_id.panjang,
                                'glue': source.product_id.glue.id,
                                'grade': source.product_id.grade.id,
                                'name': source.product_id.goods_type + ' ' + source.product_id.jenis_core.name + ' ' + str(source.product_id.tebal) + 'mm x ' + str(source.product_id.lebar) + ' x ' + str(source.product_id.panjang) + ' ' + source.product_id.glue.name + ' ' + source.product_id.grade.name
                            })

                            if new_product_ids:
                                self.env['pwk.mutasi.assembling.finishing.proses2'].create({
                                    'reference': res.id,
                                    'product_id': source.product_id.id,
                                    'new_product_id': new_product_ids[0].id,
                                    'keterangan': 'LUP2'
                                    })

    @api.multi
    def button_reload_kalibrasi(self):
        for res in self:
            existing_ids = self.env['pwk.mutasi.assembling.finishing.kalibrasi'].search([
                ('reference', '=', self.id)
            ])
            
            if existing_ids:
                for existing in existing_ids:
                    existing.unlink()
                    
            source_ids = self.env['pwk.mutasi.assembling.finishing.gs1'].search([
                ('reference.date','=',res.date),
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.assembling.finishing.gs1'].search([
                    ('reference.date','<',res.date - timedelta(1)),
                    ])

            if source_ids:
                for source in source_ids:
                    self.env['pwk.mutasi.assembling.finishing.kalibrasi'].create({
                        'reference': res.id,
                        'product_id': source.product_id.id,
                        })

    @api.multi
    def button_reload_kalibrasi2(self):
        for res in self:
            existing_ids = self.env['pwk.mutasi.assembling.finishing.kalibrasi2'].search([
                ('reference', '=', self.id)
            ])
            
            if existing_ids:
                for existing in existing_ids:
                    existing.unlink()
                    
            source_ids = self.env['pwk.mutasi.assembling.finishing.kalibrasi'].search([
                ('reference.date','=',res.date),
                ('sander2_stock_keluar_pcs','>',0)
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.assembling.finishing.kalibrasi'].search([
                    ('reference.date','<',res.date - timedelta(1)),
                    ('sander2_stock_keluar_pcs', '>', 0)
                    ])

            if source_ids:
                for source in source_ids:
                    self.env['pwk.mutasi.assembling.finishing.kalibrasi2'].create({
                        'reference': res.id,
                        'product_id': source.product_id.id,
                        })

            source_gsp2_ids = self.env['pwk.mutasi.assembling.finishing.gs2'].search([
                ('reference.date','=',res.date),
                ('sk_stock_keluar_pcs', '>', 0)
                ])

            if not source_gsp2_ids:
                source_gsp2_ids = self.env['pwk.mutasi.assembling.finishing.gs2'].search([
                    ('reference.date','<',res.date - timedelta(1)),
                    ('sk_stock_keluar_pcs', '>', 0)
                    ])

            if source_gsp2_ids:
                for source in source_gsp2_ids:
                    self.env['pwk.mutasi.assembling.finishing.kalibrasi2'].create({
                        'reference': res.id,
                        'product_id': source.product_id.id,
                        })

    @api.multi
    def button_reload_sizer(self):
        for res in self:
            existing_ids = self.env['pwk.mutasi.assembling.finishing.sizer'].search([
                ('reference', '=', self.id)
            ])
            
            if existing_ids:
                for existing in existing_ids:
                    existing.unlink()
                    
            source_ids = self.env['pwk.mutasi.assembling.finishing.gs2'].search([
                ('reference.date','=',res.date),
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.assembling.finishing.gs2'].search([
                    ('reference.date','<',res.date - timedelta(1)),
                    ])

            # if source_ids:
            #     for source in source_ids:
            #         self.env['pwk.mutasi.assembling.finishing.sizer'].create({
            #             'reference': res.id,
            #             'product_id': source.product_id.id,
            #             })

            kalibrasi2_source_ids = self.env['pwk.mutasi.assembling.finishing.kalibrasi2'].search([
                ('reference.date','=',res.date),'|',
                ('sander2_stock_keluar_pcs', '>', 0),
                ('tipis_stock_keluar_pcs', '>', 0)
            ])

            if not kalibrasi2_source_ids:
                kalibrasi2_source_ids = self.env['pwk.mutasi.assembling.finishing.gs2'].search([
                    ('reference.date','<',res.date - timedelta(1)),'|',
                    ('sander2_stock_keluar_pcs', '>', 0),
                    ('tipis_stock_keluar_pcs', '>', 0)
                ])

            
            if kalibrasi2_source_ids:
                for source in kalibrasi2_source_ids:
                    self.env['pwk.mutasi.assembling.finishing.sizer'].create({
                        'reference': res.id,
                        'product_id': source.product_id.id,
                        })

    @api.multi
    def button_reload_finish(self):
        for res in self:
            existing_ids = self.env['pwk.mutasi.assembling.finishing.finish'].search([
                ('reference', '=', self.id)
            ])
            
            if existing_ids:
                for existing in existing_ids:
                    existing.unlink()
                    
            source_ids = self.env['pwk.mutasi.assembling.finishing.sizer'].search([
                ('reference.date','=',res.date),
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.assembling.finishing.sizer'].search([
                    ('reference.date','<',res.date - timedelta(1)),
                    ])

            if source_ids:
                for source in source_ids:
                    self.env['pwk.mutasi.assembling.finishing.finish'].create({
                        'reference': res.id,
                        'product_id': source.product_id.id,
                        })

    @api.multi
    def button_reload_reproses(self):
        for res in self:
            existing_ids = self.env['pwk.mutasi.assembling.finishing.reproses'].search([
                ('reference', '=', self.id)
            ])
            
            if existing_ids:
                for existing in existing_ids:
                    existing.unlink()
                    
            source_ids = self.env['pwk.mutasi.sf.grading.line.revisi'].search([
                ('reference.date','=',res.date),
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.sf.grading.line.revisi'].search([
                    ('reference.date','<',res.date - timedelta(1)),
                    ])

            if source_ids:
                for source in source_ids:
                    if source.sander_stock_keluar_pcs > 0:
                        self.env['pwk.mutasi.assembling.finishing.reproses'].create({
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
