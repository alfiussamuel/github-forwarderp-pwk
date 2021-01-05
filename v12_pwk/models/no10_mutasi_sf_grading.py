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

class PwkMutasiSfGradingLineRevisi(models.Model):
    _name = "pwk.mutasi.sf.grading.line.revisi"

    reference = fields.Many2one('pwk.mutasi.sf.grading', 'Reference')
    product_id = fields.Many2one('product.product', 'Product')
    new_product_id = fields.Many2one('product.product', 'Product')
    tebal = fields.Float(compute="_get_product_attribute", string='Tebal')
    lebar = fields.Float(compute="_get_product_attribute", string='Lebar')
    panjang = fields.Float(compute="_get_product_attribute", string='Panjang')
    grade = fields.Many2one(compute="_get_product_attribute", comodel_name='pwk.grade', string='Grade')
    stock_awal_pcs = fields.Float(compute="_get_stock_awal", string='Stok Awal')
    stock_awal_vol = fields.Float(compute="_get_volume", string='Stok Awal', digits=dp.get_precision('FourDecimal'))
    
    grading_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Grading (Pcs)')
    grading_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Grading (M3)', digits=dp.get_precision('FourDecimal'))
    grading_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Grading')
    grading_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Grading', digits=dp.get_precision('FourDecimal'))

    sander_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Sander (Pcs)')
    sander_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Sander (M3)', digits=dp.get_precision('FourDecimal'))
    sander_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Sander')
    sander_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Sander', digits=dp.get_precision('FourDecimal'))

    lain_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Lain (Pcs)')
    lain_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Lain (M3)', digits=dp.get_precision('FourDecimal'))
    lain_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Lain')
    lain_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Lain', digits=dp.get_precision('FourDecimal'))
    
    grading_stock_keluar_pcs = fields.Float('Stok Keluar Grading (Pcs)')
    grading_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Lain (M3)', digits=dp.get_precision('FourDecimal'))
    grading_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Lain')
    grading_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Lain', digits=dp.get_precision('FourDecimal'))

    sander_stock_keluar_pcs = fields.Float('Stok Keluar Sander (Pcs)')
    sander_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Sander (M3)', digits=dp.get_precision('FourDecimal'))
    sander_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Sander')
    sander_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Sander', digits=dp.get_precision('FourDecimal'))

    lain_stock_keluar_pcs = fields.Float('Stok Keluar Lain (Pcs)')
    lain_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Lain (M3)', digits=dp.get_precision('FourDecimal'))
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

    @api.depends('stock_awal_pcs',
        'grading_stock_masuk_pcs','sander_stock_masuk_pcs','lain_stock_masuk_pcs',
        'grading_stock_keluar_pcs','sander_stock_keluar_pcs','lain_stock_keluar_pcs',
        'grading_acc_stock_masuk_pcs','sander_acc_stock_masuk_pcs','lain_acc_stock_masuk_pcs',
        'grading_acc_stock_keluar_pcs','sander_acc_stock_keluar_pcs','lain_acc_stock_keluar_pcs',
        'stock_akhir_pcs'
        )
    def _get_volume(self):
        for res in self:
            res.stock_awal_vol = res.stock_awal_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.grading_stock_masuk_vol = res.grading_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.sander_stock_masuk_vol = res.sander_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.lain_stock_masuk_vol = res.lain_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.grading_stock_keluar_vol = res.grading_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.sander_stock_keluar_vol = res.sander_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.lain_stock_keluar_vol = res.lain_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.grading_acc_stock_masuk_vol = res.grading_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.sander_acc_stock_masuk_vol = res.sander_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.lain_acc_stock_masuk_vol = res.lain_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000

            res.grading_acc_stock_keluar_vol = res.grading_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.sander_acc_stock_keluar_vol = res.sander_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.lain_acc_stock_keluar_vol = res.lain_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.stock_akhir_vol = res.stock_akhir_pcs * res.tebal * res.lebar * res.panjang / 1000000000

    @api.depends('stock_awal_pcs',
        'grading_stock_masuk_pcs','sander_stock_masuk_pcs','lain_stock_masuk_pcs',
        'grading_stock_keluar_pcs','sander_stock_keluar_pcs','lain_stock_keluar_pcs')
    def _get_acc(self):
        for res in self:
            grading_acc_stock_masuk_pcs = 0
            sander_acc_stock_masuk_pcs = 0
            lain_acc_stock_masuk_pcs = 0
            sander_acc_stock_keluar_pcs = 0
            grading_acc_stock_keluar_pcs = 0
            lain_acc_stock_keluar_pcs = 0

            source_ids = self.env['pwk.mutasi.sf.grading.line.revisi'].search([
                ('reference.date','=',res.reference.date - timedelta(1)),
                ('product_id','=',res.product_id.id)
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.sf.grading.line.revisi'].search([
                    ('reference.date','<',res.reference.date),
                    ('product_id','=',res.product_id.id)
                    ])

            if source_ids:
                grading_acc_stock_masuk_pcs = source_ids[0].grading_acc_stock_masuk_pcs
                sander_acc_stock_masuk_pcs = source_ids[0].sander_acc_stock_masuk_pcs
                lain_acc_stock_masuk_pcs = source_ids[0].lain_acc_stock_masuk_pcs
                grading_acc_stock_keluar_pcs = source_ids[0].grading_acc_stock_keluar_pcs
                sander_acc_stock_keluar_pcs = source_ids[0].sander_acc_stock_keluar_pcs
                lain_acc_stock_keluar_pcs = source_ids[0].lain_acc_stock_keluar_pcs

            res.grading_acc_stock_masuk_pcs = grading_acc_stock_masuk_pcs + res.grading_stock_masuk_pcs
            res.sander_acc_stock_masuk_pcs = sander_acc_stock_masuk_pcs + res.sander_stock_masuk_pcs
            res.lain_acc_stock_masuk_pcs = lain_acc_stock_masuk_pcs + res.lain_stock_masuk_pcs
            res.grading_acc_stock_keluar_pcs = grading_acc_stock_keluar_pcs + res.grading_stock_keluar_pcs
            res.sander_acc_stock_keluar_pcs = sander_acc_stock_keluar_pcs + res.sander_stock_keluar_pcs
            res.lain_acc_stock_keluar_pcs = lain_acc_stock_keluar_pcs + res.lain_stock_keluar_pcs

    @api.depends('product_id')
    def _get_stock_awal(self):
        for res in self:
            stock_awal_pcs = 0
            source_ids = self.env['pwk.mutasi.sf.grading.line.revisi'].search([
                ('reference.date','=',res.reference.date - timedelta(1)),
                ('product_id','=',res.product_id.id)
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.sf.grading.line.revisi'].search([
                    ('reference.date','<',res.reference.date),
                    ('product_id','=',res.product_id.id)
                    ])
                        
            if source_ids:
                stock_awal_pcs = source_ids[0].stock_akhir_pcs

            res.stock_awal_pcs = stock_awal_pcs

    @api.depends('product_id')
    def _get_stock_masuk(self):
        for res in self:
            grading_stock_masuk_pcs = 0
            sander_stock_masuk_pcs = 0
            lain_stock_masuk_pcs = 0

            grading_source_ids = self.env['pwk.mutasi.harian.grading.line'].search([
                ('reference.date','=',res.reference.date),
                ('product_id','=',res.product_id.id)
                ])
            
            print ("Grading Source ", grading_source_ids)
            if grading_source_ids:
                for grading in grading_source_ids:
                    grading_stock_masuk_pcs += grading.repair_stock_keluar_pcs

            revisi_source_ids = self.env['pwk.mutasi.sf.grading.line.revisi'].search([
                ('reference.date','=',res.reference.date),
                ('product_id','=',res.product_id.id)
            ])
            
            if revisi_source_ids:
                lain_stock_masuk_pcs = revisi_source_ids[0].lain_stock_keluar_pcs

            sander_stock_masuk_pcs = res.sander_stock_keluar_pcs

            res.grading_stock_masuk_pcs = grading_stock_masuk_pcs
            res.sander_stock_masuk_pcs = sander_stock_masuk_pcs
            res.lain_stock_masuk_pcs = res.lain_stock_keluar_pcs

    @api.depends('stock_awal_pcs',
        'grading_stock_masuk_pcs','sander_stock_masuk_pcs','lain_stock_masuk_pcs',
        'grading_stock_keluar_pcs','sander_stock_keluar_pcs','lain_stock_keluar_pcs')
    def _get_stock_akhir(self):
        for res in self:
            res.stock_akhir_pcs = res.stock_awal_pcs + res.grading_stock_masuk_pcs + res.sander_stock_masuk_pcs + res.lain_stock_masuk_pcs - res.grading_stock_keluar_pcs - res.sander_stock_keluar_pcs - res.lain_stock_keluar_pcs


class PwkMutasiSfGradingLine(models.Model):
    _name = "pwk.mutasi.sf.grading.line"

    reference = fields.Many2one('pwk.mutasi.sf.grading', 'Reference')
    product_id = fields.Many2one('product.product', 'Product')
    new_product_id = fields.Many2one('product.product', 'Product')
    tebal = fields.Float(compute="_get_product_attribute", string='Tebal')
    lebar = fields.Float(compute="_get_product_attribute", string='Lebar')
    panjang = fields.Float(compute="_get_product_attribute", string='Panjang')
    grade = fields.Many2one(compute="_get_product_attribute", comodel_name='pwk.grade', string='Grade')
    stock_awal_pcs = fields.Float(compute="_get_stock_awal", string='Stok Awal')
    stock_awal_vol = fields.Float(compute="_get_volume", string='Stok Awal', digits=dp.get_precision('FourDecimal'))
    
    finish_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk SF (Pcs)')
    finish_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk SF (M3)', digits=dp.get_precision('FourDecimal'))
    finish_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk SF')
    finish_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk SF', digits=dp.get_precision('FourDecimal'))

    sizer_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Sizer (Pcs)')
    sizer_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Sizer (M3)', digits=dp.get_precision('FourDecimal'))
    sizer_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Sizer')
    sizer_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Sizer', digits=dp.get_precision('FourDecimal'))

    lain_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Lain (Pcs)')
    lain_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Lain (M3)', digits=dp.get_precision('FourDecimal'))
    lain_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Lain')
    lain_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Lain', digits=dp.get_precision('FourDecimal'))

    re_stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk Re (Pcs)')
    re_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Re (M3)', digits=dp.get_precision('FourDecimal'))
    re_acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Re')
    re_acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk Re', digits=dp.get_precision('FourDecimal'))
    
    ok_stock_keluar_pcs = fields.Float('Stok Keluar OK (Pcs)')
    ok_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar OK (M3)', digits=dp.get_precision('FourDecimal'))
    ok_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar OK')
    ok_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar OK', digits=dp.get_precision('FourDecimal'))

    grading_stock_keluar_pcs = fields.Float('Stok Keluar Grading (Pcs)')
    grading_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Grading (M3)', digits=dp.get_precision('FourDecimal'))
    grading_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Grading')
    grading_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Grading', digits=dp.get_precision('FourDecimal'))

    repair_stock_keluar_pcs = fields.Float('Stok Keluar Repair (Pcs)')
    repair_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Repair (M3)', digits=dp.get_precision('FourDecimal'))
    repair_acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Repair')
    repair_acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar Repair', digits=dp.get_precision('FourDecimal'))

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
        'finish_stock_masuk_pcs','sizer_stock_masuk_pcs','lain_stock_masuk_pcs','re_stock_masuk_pcs',
        'ok_stock_keluar_pcs','grading_stock_keluar_pcs','repair_stock_keluar_pcs','re_stock_keluar_pcs',
        'finish_acc_stock_masuk_pcs','sizer_acc_stock_masuk_pcs','lain_acc_stock_masuk_pcs','re_acc_stock_masuk_pcs',
        'ok_acc_stock_keluar_pcs','grading_acc_stock_keluar_pcs','repair_acc_stock_keluar_pcs','re_acc_stock_keluar_pcs',
        'stock_akhir_pcs'
        )
    def _get_volume(self):
        for res in self:
            res.stock_awal_vol = res.stock_awal_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.finish_stock_masuk_vol = res.finish_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.sizer_stock_masuk_vol = res.sizer_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.lain_stock_masuk_vol = res.lain_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_stock_masuk_vol = res.re_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.ok_stock_keluar_vol = res.ok_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.grading_stock_keluar_vol = res.grading_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.repair_stock_keluar_vol = res.repair_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_stock_keluar_vol = res.re_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.finish_acc_stock_masuk_vol = res.finish_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.sizer_acc_stock_masuk_vol = res.sizer_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.lain_acc_stock_masuk_vol = res.lain_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_acc_stock_masuk_vol = res.re_acc_stock_masuk_pcs * res.tebal * res.lebar * res.panjang / 1000000000

            res.ok_acc_stock_keluar_vol = res.ok_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.grading_acc_stock_keluar_vol = res.grading_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.repair_acc_stock_keluar_vol = res.repair_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.re_acc_stock_keluar_vol = res.re_acc_stock_keluar_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            
            res.stock_akhir_vol = res.stock_akhir_pcs * res.tebal * res.lebar * res.panjang / 1000000000

    @api.depends('stock_awal_pcs',
        'finish_stock_masuk_pcs','sizer_stock_masuk_pcs','lain_stock_masuk_pcs','re_stock_masuk_pcs',
        'ok_stock_keluar_pcs','grading_stock_keluar_pcs','repair_stock_keluar_pcs','re_stock_keluar_pcs')
    def _get_acc(self):
        for res in self:
            finish_acc_stock_masuk_pcs = 0
            sizer_acc_stock_masuk_pcs = 0
            lain_acc_stock_masuk_pcs = 0
            re_acc_stock_masuk_pcs = 0
            ok_acc_stock_keluar_pcs = 0
            grading_acc_stock_keluar_pcs = 0
            repair_acc_stock_keluar_pcs = 0
            re_acc_stock_keluar_pcs = 0

            source_ids = self.env['pwk.mutasi.sf.grading.line'].search([
                ('reference.date','=',res.reference.date - timedelta(1)),
                ('product_id','=',res.product_id.id)
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.sf.grading.line'].search([
                    ('reference.date','<',res.reference.date),
                    ('product_id','=',res.product_id.id)
                    ])

            if source_ids:
                finish_acc_stock_masuk_pcs = source_ids[0].finish_acc_stock_masuk_pcs
                sizer_acc_stock_masuk_pcs = source_ids[0].sizer_acc_stock_masuk_pcs
                lain_acc_stock_masuk_pcs = source_ids[0].lain_acc_stock_masuk_pcs
                re_acc_stock_masuk_pcs = source_ids[0].re_acc_stock_masuk_pcs
                ok_acc_stock_keluar_pcs = source_ids[0].ok_acc_stock_keluar_pcs
                grading_acc_stock_keluar_pcs = source_ids[0].grading_acc_stock_keluar_pcs
                repair_acc_stock_keluar_pcs = source_ids[0].repair_acc_stock_keluar_pcs
                re_acc_stock_keluar_pcs = source_ids[0].re_acc_stock_keluar_pcs

            res.finish_acc_stock_masuk_pcs = finish_acc_stock_masuk_pcs + res.finish_stock_masuk_pcs
            res.sizer_acc_stock_masuk_pcs = sizer_acc_stock_masuk_pcs + res.sizer_stock_masuk_pcs
            res.lain_acc_stock_masuk_pcs = lain_acc_stock_masuk_pcs + res.lain_stock_masuk_pcs
            res.re_acc_stock_masuk_pcs = re_acc_stock_masuk_pcs + res.re_stock_masuk_pcs
            res.ok_acc_stock_keluar_pcs = ok_acc_stock_keluar_pcs + res.ok_stock_keluar_pcs
            res.grading_acc_stock_keluar_pcs = grading_acc_stock_keluar_pcs + res.grading_stock_keluar_pcs
            res.repair_acc_stock_keluar_pcs = repair_acc_stock_keluar_pcs + res.repair_stock_keluar_pcs
            res.re_acc_stock_keluar_pcs = re_acc_stock_keluar_pcs + res.re_stock_keluar_pcs

    @api.depends('product_id')
    def _get_stock_awal(self):
        for res in self:
            stock_awal_pcs = 0
            source_ids = self.env['pwk.mutasi.sf.grading.line'].search([
                ('reference.date','=',res.reference.date - timedelta(1)),
                ('product_id','=',res.product_id.id)
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.sf.grading.line'].search([
                    ('reference.date','<',res.reference.date),
                    ('product_id','=',res.product_id.id)
                    ])
                        
            if source_ids:
                stock_awal_pcs = source_ids[0].stock_akhir_pcs

            res.stock_awal_pcs = stock_awal_pcs

    @api.depends('product_id')
    def _get_stock_masuk(self):
        for res in self:
            finish_stock_masuk_pcs = 0
            sizer_stock_masuk_pcs = 0
            lain_stock_masuk_pcs = 0

            finish_source_ids = self.env['pwk.mutasi.assembling.finishing.finish'].search([
                ('reference.date','=',res.reference.date),
                ('product_id','=',res.product_id.id)
                ])

            sizer_source_ids = self.env['pwk.mutasi.assembling.finishing.sizer'].search([
                ('reference.date','=',res.reference.date),
                ('product_id','=',res.product_id.id)
                ])            

            revisi_source_ids = self.env['pwk.mutasi.sf.grading.line.revisi'].search([
                ('reference.date','=',res.reference.date),
                ('product_id','=',res.product_id.id)
                ])
                        
            if finish_source_ids:
                finish_stock_masuk_pcs = finish_source_ids[0].grading_stock_keluar_pcs

            if sizer_source_ids:
                sizer_stock_masuk_pcs = sizer_source_ids[0].grading_stock_keluar_pcs
        
            if revisi_source_ids:
                lain_stock_masuk_pcs += revisi_source_ids[0].sander_stock_keluar_pcs
                lain_stock_masuk_pcs += revisi_source_ids[0].grading_stock_keluar_pcs

            res.finish_stock_masuk_pcs = finish_stock_masuk_pcs
            res.sizer_stock_masuk_pcs = sizer_stock_masuk_pcs
            res.lain_stock_masuk_pcs = lain_stock_masuk_pcs
            res.re_stock_masuk_pcs = res.re_stock_keluar_pcs

    @api.depends('stock_awal_pcs',
        'finish_stock_masuk_pcs','sizer_stock_masuk_pcs','lain_stock_masuk_pcs','re_stock_masuk_pcs',
        'ok_stock_keluar_pcs','grading_stock_keluar_pcs','repair_stock_keluar_pcs','re_stock_keluar_pcs')
    def _get_stock_akhir(self):
        for res in self:
            additional = res.finish_stock_masuk_pcs + res.lain_stock_masuk_pcs + res.sizer_stock_masuk_pcs + res.re_stock_masuk_pcs
            deduction = res.ok_stock_keluar_pcs + res.grading_stock_keluar_pcs + res.repair_stock_keluar_pcs + res.re_stock_keluar_pcs
            res.stock_akhir_pcs = res.stock_awal_pcs + additional - deduction


class PwkMutasiSfGrading(models.Model):    
    _name = "pwk.mutasi.sf.grading"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char('No. Dokumen', track_visibility="always")
    date = fields.Date('Tanggal', default=fields.Date.today(), track_visibility="always")
    user_id = fields.Many2one('res.users', string="Dibuat Oleh", default=lambda self: self.env.user, track_visibility="always")
    state = fields.Selection([('Draft','Draft'),('Approved','Approved')], string="Status", default="Draft", track_visibility="always")
    line_ids = fields.One2many('pwk.mutasi.sf.grading.line', 'reference', string="Mutasi SF Grading", track_visibility="always")
    line_revisi_ids = fields.One2many('pwk.mutasi.sf.grading.line.revisi', 'reference', string="Mutasi Revisi", track_visibility="always")

    def get_sequence(self, name=False, obj=False, context=None):
        sequence_id = self.env['ir.sequence'].search([
            ('name', '=', name),
            ('code', '=', obj),
            ('suffix', '=', '.MSGR.%(month)s.%(year)s')
        ])
        if not sequence_id :
            sequence_id = self.env['ir.sequence'].sudo().create({
                'name': name,
                'code': obj,
                'implementation': 'no_gap',
                'suffix': '.MSGR.%(month)s.%(year)s',
                'padding': 3
            })
        return sequence_id.next_by_id()

    @api.model
    def create(self, vals):
        vals['name'] = self.get_sequence('Mutasi SF Grading', 'pwk.mutasi.sf.grading')
        return super(PwkMutasiSfGrading, self).create(vals)

    @api.multi
    def button_reload(self):
        for res in self:
            existing_ids = self.env['pwk.mutasi.sf.grading.line'].search([
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
                    ('reference.date','=',res.date - timedelta(1)),
                    ])

            if source_ids:
                for source in source_ids:
                    self.env['pwk.mutasi.sf.grading.line'].create({
                        'reference': res.id,
                        'product_id': source.product_id.id,
                        })

    @api.multi
    def button_reload_revisi(self):
        for res in self:
            existing_ids = self.env['pwk.mutasi.sf.grading.line.revisi'].search([
                ('reference', '=', self.id)
            ])
            
            if existing_ids:
                for existing in existing_ids:
                    existing.unlink()
                    
            source_ids = self.env['pwk.mutasi.sf.grading.line'].search([
                ('reference.date','=',res.date),
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.sf.grading.line'].search([
                    ('reference.date','=',res.date - timedelta(1)),
                    ])

            if source_ids:
                for source in source_ids:
                    self.env['pwk.mutasi.sf.grading.line.revisi'].create({
                        'reference': res.id,
                        'product_id': source.product_id.id,
                        })

    @api.multi
    def button_approve(self):
        for res in self:
            res.state = "Approved"            

    @api.multi
    def button_draft(self):
        for res in self:
            res.state = 'Draft'
