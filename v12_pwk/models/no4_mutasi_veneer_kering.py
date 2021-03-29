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

class PwkMutasiVeneerKeringLine2(models.Model):
    _name = "pwk.mutasi.veneer.kering.line2"

    reference = fields.Many2one('pwk.mutasi.veneer.kering', 'Reference')
    product_id = fields.Many2one('product.product', 'Bahan Baku')
    new_product_id = fields.Many2one('product.product', 'WIP')
    tebal = fields.Float(compute="_get_product_attribute", string='Tebal')
    lebar = fields.Float(compute="_get_product_attribute", string='Lebar')
    panjang = fields.Float(compute="_get_product_attribute", string='Panjang')
    grade = fields.Many2one(compute="_get_product_attribute", comodel_name='pwk.grade', string='Grade')
    stock_awal_pcs = fields.Float(compute="_get_stock_awal", string='Stok Awal')
    stock_awal_vol = fields.Float(compute="_get_volume", string='Stok Awal', digits=dp.get_precision('FourDecimal'))
        
    supp_stock_masuk_pcs = fields.Float(string='Stok Masuk Supp')
    supp_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Supp', digits=dp.get_precision('FourDecimal'))
    supp_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Supp')
    supp_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Supp', digits=dp.get_precision('FourDecimal'))
    
    repair_stock_keluar_pcs = fields.Float('Stok Keluar Rep')
    repair_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Rep', digits=dp.get_precision('FourDecimal'))
    repair_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Rep')
    repair_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Rep', digits=dp.get_precision('FourDecimal'))
    
    re_stacking_stock_keluar_pcs = fields.Float('Stok Keluar Stack')
    re_stacking_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Re-Stack', digits=dp.get_precision('FourDecimal'))
    re_stacking_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Re-Stack')
    re_stacking_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Re-Stack', digits=dp.get_precision('FourDecimal'))
    
    re_rd_stock_keluar_pcs = fields.Float('Stok Keluar Roll')
    re_rd_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Re-Roll', digits=dp.get_precision('FourDecimal'))
    re_rd_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Re-Roll')
    re_rd_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Re-Roll', digits=dp.get_precision('FourDecimal'))
    
    lain_stock_keluar_pcs = fields.Float('Stok Keluar Lain')
    lain_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Lain', digits=dp.get_precision('FourDecimal'))
    lain_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Lain')
    lain_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Lain', digits=dp.get_precision('FourDecimal'))
    
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

    @api.depends('stock_awal_pcs', 'supp_stock_masuk_pcs', 'repair_stock_keluar_pcs', 're_stacking_stock_keluar_pcs', 're_rd_stock_keluar_pcs', 'lain_stock_keluar_pcs')
    def _get_volume(self):
        for res in self:
            res.stock_awal_vol = res.stock_awal_pcs * res.tebal * res.lebar * res.panjang / 1000000000
                        
            res.supp_stock_masuk_vol = res.supp_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000                    
            res.supp_acc_stock_masuk_vol = res.supp_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.repair_stock_keluar_vol = res.repair_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_stacking_stock_keluar_vol = res.re_stacking_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_rd_stock_keluar_vol = res.re_rd_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.lain_stock_keluar_vol = res.lain_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.repair_acc_stock_keluar_vol = res.repair_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_stacking_acc_stock_keluar_vol = res.re_stacking_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_rd_acc_stock_keluar_vol = res.re_rd_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.lain_acc_stock_keluar_vol = res.lain_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.stock_akhir_vol = res.stock_akhir_pcs * res.tebal * res.lebar * res.panjang / 1000000000

    @api.depends('stock_awal_pcs', 'supp_stock_masuk_pcs', 'repair_stock_keluar_pcs', 're_stacking_stock_keluar_pcs', 're_rd_stock_keluar_pcs', 'lain_stock_keluar_pcs',)
    def _get_acc(self):
        for res in self:            
            supp_acc_stock_masuk_pcs = 0
            repair_acc_stock_keluar_pcs = 0
            re_stacking_acc_stock_keluar_pcs = 0
            re_rd_acc_stock_keluar_pcs = 0
            lain_acc_stock_keluar_pcs = 0

            source_ids = self.env['pwk.mutasi.veneer.kering.line'].search([
                ('reference.date','=',res.reference.date - timedelta(1)),
                ('product_id','=',res.product_id.id)
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.veneer.kering.line'].search([
                    ('reference.date','<',res.reference.date),
                    ('product_id','=',res.product_id.id)
                    ])

            if source_ids:                
                supp_acc_stock_masuk_pcs = source_ids[0].supp_acc_stock_masuk_pcs
                repair_acc_stock_keluar_pcs = source_ids[0].repair_acc_stock_keluar_pcs
                re_stacking_acc_stock_keluar_pcs = source_ids[0].re_stacking_acc_stock_keluar_pcs
                re_rd_acc_stock_keluar_pcs = source_ids[0].re_rd_acc_stock_keluar_pcs
                lain_acc_stock_keluar_pcs = source_ids[0].lain_acc_stock_keluar_pcs
            
            res.supp_acc_stock_masuk_pcs = supp_acc_stock_masuk_pcs + res.supp_stock_masuk_pcs
            res.repair_acc_stock_keluar_pcs = repair_acc_stock_keluar_pcs + res.repair_stock_keluar_pcs
            res.re_stacking_acc_stock_keluar_pcs = re_stacking_acc_stock_keluar_pcs + res.re_stacking_stock_keluar_pcs
            res.re_rd_acc_stock_keluar_pcs = re_rd_acc_stock_keluar_pcs + res.re_rd_stock_keluar_pcs
            res.lain_acc_stock_keluar_pcs = lain_acc_stock_keluar_pcs + res.lain_stock_keluar_pcs

    @api.depends('product_id')
    def _get_stock_awal(self):
        for res in self:
            stock_awal_pcs = 0
            source_ids = self.env['pwk.mutasi.veneer.kering.line2'].search([
                ('reference.date','=',res.reference.date - timedelta(1)),
                ('product_id','=',res.product_id.id)
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.veneer.kering.line2'].search([
                    ('reference.date','<',res.reference.date),
                    ('product_id','=',res.product_id.id)
                    ])
                        
            if source_ids:
                stock_awal_pcs = source_ids[0].stock_akhir_pcs

            res.stock_awal_pcs = stock_awal_pcs

    @api.depends('stock_awal_pcs', 'supp_stock_masuk_pcs', 'repair_stock_keluar_pcs', 're_stacking_stock_keluar_pcs', 're_rd_stock_keluar_pcs', 'lain_stock_keluar_pcs',)
    def _get_stock_akhir(self):
        for res in self:
            additional_stock = res.supp_stock_masuk_pcs
            deduction_stock = res.repair_stock_keluar_pcs + res.re_stacking_stock_keluar_pcs + res.re_rd_stock_keluar_pcs + res.lain_stock_keluar_pcs 
            res.stock_akhir_pcs = res.stock_awal_pcs + additional_stock - deduction_stock


class PwkMutasiVeneerKeringLine(models.Model):
    _name = "pwk.mutasi.veneer.kering.line"

    reference = fields.Many2one('pwk.mutasi.veneer.kering', 'Reference')
    product_id = fields.Many2one('product.product', 'Bahan Baku')
    new_product_id = fields.Many2one('product.product', 'WIP')
    tebal = fields.Float(compute="_get_product_attribute", string='Tebal')
    lebar = fields.Float(compute="_get_product_attribute", string='Lebar')
    panjang = fields.Float(compute="_get_product_attribute", string='Panjang')
    grade = fields.Many2one(compute="_get_product_attribute", comodel_name='pwk.grade', string='Grade')
    stock_awal_pcs = fields.Float(compute="_get_stock_awal", string='Stok Awal')
    stock_awal_vol = fields.Float(compute="_get_volume", string='Stok Awal', digits=dp.get_precision('FourDecimal'))
    
    kd_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk KD')
    kd_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk KD', digits=dp.get_precision('FourDecimal'))
    kd_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk KD')
    kd_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk KD', digits=dp.get_precision('FourDecimal'))
    
    rd_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Roll')
    rd_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Roll', digits=dp.get_precision('FourDecimal'))
    rd_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Roll')
    rd_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Roll', digits=dp.get_precision('FourDecimal'))
    
    re_kd_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Re-KD')
    re_kd_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Re-KD', digits=dp.get_precision('FourDecimal'))
    re_kd_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Re-KD')
    re_kd_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Re-KD', digits=dp.get_precision('FourDecimal'))
    
    re_rd_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Re-Roll')
    re_rd_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Re-Roll', digits=dp.get_precision('FourDecimal'))
    re_rd_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Re-Roll')
    re_rd_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Re-Roll', digits=dp.get_precision('FourDecimal'))
    
    supp_stock_masuk_pcs = fields.Float(string='Stok Masuk Supp')
    supp_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Supp', digits=dp.get_precision('FourDecimal'))
    supp_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Supp')
    supp_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Supp', digits=dp.get_precision('FourDecimal'))
    
    repair_stock_keluar_pcs = fields.Float('Stok Keluar Rep')
    repair_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Rep', digits=dp.get_precision('FourDecimal'))
    repair_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Rep')
    repair_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Rep', digits=dp.get_precision('FourDecimal'))
    
    re_stacking_stock_keluar_pcs = fields.Float('Stok Keluar Stack')
    re_stacking_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Re-Stack', digits=dp.get_precision('FourDecimal'))
    re_stacking_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Re-Stack')
    re_stacking_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Re-Stack', digits=dp.get_precision('FourDecimal'))
    
    re_rd_stock_keluar_pcs = fields.Float('Stok Keluar Roll')
    re_rd_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Re-Roll', digits=dp.get_precision('FourDecimal'))
    re_rd_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Re-Roll')
    re_rd_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Re-Roll', digits=dp.get_precision('FourDecimal'))
    
    lain_stock_keluar_pcs = fields.Float('Stok Keluar Lain')
    lain_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Lain', digits=dp.get_precision('FourDecimal'))
    lain_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Lain')
    lain_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Lain', digits=dp.get_precision('FourDecimal'))
    
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

    @api.depends('stock_awal_pcs','kd_stock_masuk_pcs', 'rd_stock_masuk_pcs', 're_kd_stock_masuk_pcs', 're_rd_stock_masuk_pcs', 
                 'supp_stock_masuk_pcs', 'repair_stock_keluar_pcs', 're_stacking_stock_keluar_pcs', 're_rd_stock_keluar_pcs', 'lain_stock_keluar_pcs')
    def _get_volume(self):
        for res in self:
            res.stock_awal_vol = res.stock_awal_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.kd_stock_masuk_vol = res.kd_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000      
            res.rd_stock_masuk_vol = res.rd_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_kd_stock_masuk_vol = res.re_kd_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_rd_stock_masuk_vol = res.re_rd_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.supp_stock_masuk_vol = res.supp_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.kd_acc_stock_masuk_vol = res.kd_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.rd_acc_stock_masuk_vol = res.rd_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_kd_acc_stock_masuk_vol = res.re_kd_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_rd_acc_stock_masuk_vol = res.re_rd_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.supp_acc_stock_masuk_vol = res.supp_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.repair_stock_keluar_vol = res.repair_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_stacking_stock_keluar_vol = res.re_stacking_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_rd_stock_keluar_vol = res.re_rd_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.lain_stock_keluar_vol = res.lain_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.repair_acc_stock_keluar_vol = res.repair_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_stacking_acc_stock_keluar_vol = res.re_stacking_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_rd_acc_stock_keluar_vol = res.re_rd_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.lain_acc_stock_keluar_vol = res.lain_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.stock_akhir_vol = res.stock_akhir_pcs * res.tebal * res.lebar * res.panjang / 1000000000

    @api.depends('stock_awal_pcs', 'kd_stock_masuk_pcs', 'rd_stock_masuk_pcs', 're_kd_stock_masuk_pcs', 're_rd_stock_masuk_pcs', 'supp_stock_masuk_pcs',
                 'repair_stock_keluar_pcs', 're_stacking_stock_keluar_pcs', 're_rd_stock_keluar_pcs', 'lain_stock_keluar_pcs',)
    def _get_acc(self):
        for res in self:
            kd_acc_stock_masuk_pcs = 0
            rd_acc_stock_masuk_pcs = 0
            re_kd_acc_stock_masuk_pcs = 0
            re_rd_acc_stock_masuk_pcs = 0
            supp_acc_stock_masuk_pcs = 0
            repair_acc_stock_keluar_pcs = 0
            re_stacking_acc_stock_keluar_pcs = 0
            re_rd_acc_stock_keluar_pcs = 0
            lain_acc_stock_keluar_pcs = 0

            source_ids = self.env['pwk.mutasi.veneer.kering.line'].search([
                ('reference.date','=',res.reference.date - timedelta(1)),
                ('product_id','=',res.product_id.id)
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.veneer.kering.line'].search([
                    ('reference.date','<',res.reference.date),
                    ('product_id','=',res.product_id.id)
                    ])

            if source_ids:
                kd_acc_stock_masuk_pcs = source_ids[0].kd_acc_stock_masuk_pcs
                rd_acc_stock_masuk_pcs = source_ids[0].rd_acc_stock_masuk_pcs
                re_kd_acc_stock_masuk_pcs = source_ids[0].re_kd_acc_stock_masuk_pcs
                re_rd_acc_stock_masuk_pcs = source_ids[0].re_rd_acc_stock_masuk_pcs
                supp_acc_stock_masuk_pcs = source_ids[0].supp_acc_stock_masuk_pcs
                repair_acc_stock_keluar_pcs = source_ids[0].repair_acc_stock_keluar_pcs
                re_stacking_acc_stock_keluar_pcs = source_ids[0].re_stacking_acc_stock_keluar_pcs
                re_rd_acc_stock_keluar_pcs = source_ids[0].re_rd_acc_stock_keluar_pcs
                lain_acc_stock_keluar_pcs = source_ids[0].lain_acc_stock_keluar_pcs

            res.kd_acc_stock_masuk_pcs = kd_acc_stock_masuk_pcs + res.kd_stock_masuk_pcs
            res.rd_acc_stock_masuk_pcs = rd_acc_stock_masuk_pcs + res.rd_stock_masuk_pcs
            res.re_kd_acc_stock_masuk_pcs = re_kd_acc_stock_masuk_pcs + res.re_kd_stock_masuk_pcs
            res.re_rd_acc_stock_masuk_pcs = re_rd_acc_stock_masuk_pcs + res.re_rd_stock_masuk_pcs
            res.supp_acc_stock_masuk_pcs = supp_acc_stock_masuk_pcs + res.supp_stock_masuk_pcs
            res.repair_acc_stock_keluar_pcs = repair_acc_stock_keluar_pcs + res.repair_stock_keluar_pcs
            res.re_stacking_acc_stock_keluar_pcs = re_stacking_acc_stock_keluar_pcs + res.re_stacking_stock_keluar_pcs
            res.re_rd_acc_stock_keluar_pcs = re_rd_acc_stock_keluar_pcs + res.re_rd_stock_keluar_pcs
            res.lain_acc_stock_keluar_pcs = lain_acc_stock_keluar_pcs + res.lain_stock_keluar_pcs

    @api.depends('product_id')
    def _get_stock_awal(self):
        for res in self:
            stock_awal_pcs = 0
            source_ids = self.env['pwk.mutasi.veneer.kering.line'].search([
                ('reference.date','=',res.reference.date - timedelta(1)),
                ('product_id','=',res.product_id.id)
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.veneer.kering.line'].search([
                    ('reference.date','<',res.reference.date),
                    ('product_id','=',res.product_id.id)
                    ])
                        
            if source_ids:
                stock_awal_pcs = source_ids[0].stock_akhir_pcs

            res.stock_awal_pcs = stock_awal_pcs

    @api.depends('product_id')
    def _get_stock_masuk(self):
        for res in self:
            kd_stock_masuk_pcs = 0
            rd_stock_masuk_pcs = 0
            re_kd_stock_masuk_pcs = 0
            re_rd_stock_masuk_pcs = 0
            supp_stock_masuk_pcs = 0
            
            kd_source_ids = self.env['pwk.mutasi.veneer.klindry.line'].search([
                ('reference.date','=',res.reference.date),
                ('product_id','=',res.product_id.id)
                ])
            
            re_kd_source_ids = self.env['pwk.mutasi.veneer.klindry.reline'].search([
                ('reference.date','=',res.reference.date),
                ('product_id','=',res.product_id.id)
                ])
            
            rd_source_ids = self.env['pwk.mutasi.veneer.roler.line'].search([
                ('reference.date','=',res.reference.date),
                ('product_id','=',res.product_id.id)
                ])
            
            re_rd_source_ids = self.env['pwk.mutasi.veneer.roler.reline'].search([
                ('reference.date','=',res.reference.date),
                ('product_id','=',res.product_id.id)
                ])
                        
            if kd_source_ids:
                kd_stock_masuk_pcs = kd_source_ids[0].stock_keluar_pcs 
               
            if rd_source_ids:
                rd_stock_masuk_pcs = rd_source_ids[0].stock_keluar_pcs 
                
            if re_kd_source_ids:
                re_kd_stock_masuk_pcs = re_kd_source_ids[0].stock_keluar_pcs
                
            if re_rd_source_ids:
                re_rd_stock_masuk_pcs = re_rd_source_ids[0].stock_keluar_pcs

            res.kd_stock_masuk_pcs = kd_stock_masuk_pcs
            res.rd_stock_masuk_pcs = rd_stock_masuk_pcs
            res.re_kd_stock_masuk_pcs = re_kd_stock_masuk_pcs
            res.re_rd_stock_masuk_pcs = re_rd_stock_masuk_pcs

    @api.depends('stock_awal_pcs', 'kd_stock_masuk_pcs', 'rd_stock_masuk_pcs', 're_kd_stock_masuk_pcs', 're_rd_stock_masuk_pcs', 'supp_stock_masuk_pcs',
                 'repair_stock_keluar_pcs', 're_stacking_stock_keluar_pcs', 're_rd_stock_keluar_pcs', 'lain_stock_keluar_pcs',)
    def _get_stock_akhir(self):
        for res in self:
            additional_stock = res.kd_stock_masuk_pcs + res.rd_stock_masuk_pcs + res.re_kd_stock_masuk_pcs + res.re_rd_stock_masuk_pcs + res.supp_stock_masuk_pcs
            deduction_stock = res.repair_stock_keluar_pcs + res.re_stacking_stock_keluar_pcs + res.re_rd_stock_keluar_pcs + res.lain_stock_keluar_pcs 
            res.stock_akhir_pcs = res.stock_awal_pcs + additional_stock - deduction_stock

class PwkMutasiVeneerKering(models.Model):    
    _name = "pwk.mutasi.veneer.kering"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char('No. Dokumen', track_visibility="always")
    date = fields.Date('Tanggal', default=fields.Date.today(), track_visibility="always")
    user_id = fields.Many2one('res.users', string="Dibuat Oleh", default=lambda self: self.env.user, track_visibility="always")
    state = fields.Selection([('Draft','Draft'),('Approved','Approved')], string="Status", default="Draft", track_visibility="always")
    line_ids = fields.One2many('pwk.mutasi.veneer.kering.line', 'reference', string="Veneer Kering", track_visibility="always")
    line_ids2 = fields.One2many('pwk.mutasi.veneer.kering.line2', 'reference', string="MDF / Faceback", track_visibility="always")    

    def get_sequence(self, name=False, obj=False, context=None):
        sequence_id = self.env['ir.sequence'].search([
            ('name', '=', name),
            ('code', '=', obj),
            ('suffix', '=', '.MVKR.%(month)s.%(year)s')
        ])
        if not sequence_id :
            sequence_id = self.env['ir.sequence'].sudo().create({
                'name': name,
                'code': obj,
                'implementation': 'no_gap',
                'suffix': '.MVKR.%(month)s.%(year)s',
                'padding': 3
            })
        return sequence_id.next_by_id()

    @api.multi
    def button_reload(self):
        for res in self:
            existing_ids = self.env['pwk.mutasi.veneer.kering.line'].search([
                ('reference', '=', self.id)
            ])
            
            if existing_ids:
                for existing in existing_ids:
                    existing.unlink()
            
            source_ids = self.env['pwk.mutasi.veneer.klindry.line'].search([
                ('reference.date','=',res.date),
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.veneer.klindry.line'].search([
                    ('reference.date','=',res.date - timedelta(1)),
                    ])

            if source_ids:
                for source in source_ids:
                    print(source.product_id.tebal)
                    print(source.product_id.panjang)
                    print(source.product_id.lebar)
                    print(source.product_id.grade.name)
                    print(source.product_id.jenis_kayu.name)
                    new_product_name = 'Veneer Kering ' + str(source.product_id.tebal) + ' x ' + str(int(source.product_id.lebar)) + ' x ' + str(int(source.product_id.panjang)) + ' ' + source.product_id.jenis_kayu.name + ' ' + source.product_id.grade.name
                    print(new_product_name)
                    new_product_ids = self.env['product.product'].search([
                        ('name', '=', new_product_name)
                    ])

                    print(new_product_ids)

                    if new_product_ids:
                        self.env['pwk.mutasi.veneer.kering.line'].create({
                            'reference': res.id,
                            'product_id': source.product_id.id,
                            'new_product_id': new_product_ids[0].id,
                            })
                    else:
                        raise UserError(_('Product %s tidak ditemukan' % new_product_name))

    @api.model
    def create(self, vals):
        vals['name'] = self.get_sequence('Mutasi Veneer Kering', 'pwk.mutasi.veneer.kering')
        return super(PwkMutasiVeneerKering, self).create(vals)

    @api.multi
    def button_approve(self):
        for res in self:
            res.state = "Approved"

    @api.multi
    def button_draft(self):
        for res in self:
            res.state = 'Draft'
