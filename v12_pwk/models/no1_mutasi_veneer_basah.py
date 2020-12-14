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
from xlsxwriter.workbook import Workbook
from odoo.tools.misc import xlwt

class PwkMutasiVeneerBasahKd(models.Model):    
    _name = "pwk.mutasi.veneer.basah.kd"    

    reference = fields.Many2one('pwk.mutasi.veneer.basah', 'Reference')
    product_id = fields.Many2one('product.product', 'Product')
    tebal = fields.Float(compute="_get_product_attribute", string='Tebal')
    lebar = fields.Float(compute="_get_product_attribute", string='Lebar')
    panjang = fields.Float(compute="_get_product_attribute", string='Panjang')
    grade = fields.Many2one(compute="_get_product_attribute", comodel_name='pwk.grade', string='Grade')
    stock_awal_pcs = fields.Float(compute="_get_stock_awal", string='Stok Awal (Pcs)')
    stock_awal_vol = fields.Float(compute="_get_volume", string='Stok Awal (M3)', digits=dp.get_precision('FourDecimal'))
    stock_masuk_pcs = fields.Float(compute="_get_stock_masuk", string='Stok Masuk (Pcs)')    
    stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk (M3)', digits=dp.get_precision('FourDecimal'))
    acc_stock_masuk_pcs = fields.Float(compute="_get_acc", string='Stok Masuk')
    acc_stock_masuk_vol = fields.Float(compute="_get_volume", string='Stok Masuk', digits=dp.get_precision('FourDecimal'))    
    stock_keluar_pcs = fields.Float('Stok Keluar (Pcs)')    
    stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar (M3)', digits=dp.get_precision('FourDecimal'))
    acc_stock_keluar_pcs = fields.Float(compute="_get_acc", string='Stok Keluar')
    acc_stock_keluar_vol = fields.Float(compute="_get_volume", string='Stok Keluar', digits=dp.get_precision('FourDecimal'))
    stock_akhir_pcs = fields.Float(compute="_get_stock_akhir", string='Stok Akhir (Pcs)')
    stock_akhir_vol = fields.Float(compute="_get_volume", string='Stok Akhir (M3)', digits=dp.get_precision('FourDecimal'))

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

    @api.depends('product_id')
    def _get_stock_awal(self):
        for res in self:
            for res in self:
                stock_awal_pcs = 0
                source_ids = self.env['pwk.mutasi.veneer.basah.kd'].search([
                    ('reference.date','=',res.reference.date - timedelta(1)),
                    ('product_id','=',res.product_id.id)
                    ])

                if not source_ids:
                    source_ids = self.env['pwk.mutasi.veneer.basah.kd'].search([
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
            source_ids = self.env['pwk.mutasi.veneer.basah.stacking'].search([
                ('reference.date','=',res.reference.date),
                ('product_id','=',res.product_id.id)
                ])
                        
            if source_ids:
                stock_masuk_pcs = source_ids[0].stock_keluar_stacking_pcs

            res.stock_masuk_pcs = stock_masuk_pcs

    @api.depends('stock_awal_pcs','stock_masuk_pcs','stock_keluar_pcs')
    def _get_acc(self):
        for res in self:
            acc_stock_masuk_pcs = 0            
            acc_stock_keluar_pcs = 0

            source_ids = self.env['pwk.mutasi.veneer.basah.kd'].search([
                ('reference.date','=',res.reference.date - timedelta(1)),
                ('product_id','=',res.product_id.id)
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.veneer.basah.kd'].search([
                    ('reference.date','<',res.reference.date),
                    ('product_id','=',res.product_id.id)
                    ])

            if source_ids:
                acc_stock_masuk_pcs = source_ids[0].acc_stock_masuk_pcs
                acc_stock_keluar_pcs = source_ids[0].acc_stock_keluar_pcs

            res.acc_stock_masuk_pcs = acc_stock_masuk_pcs + res.stock_masuk_pcs
            res.acc_stock_keluar_pcs = acc_stock_keluar_pcs + res.stock_keluar_pcs

    @api.depends('stock_awal_pcs','stock_masuk_pcs','stock_keluar_pcs')
    def _get_stock_akhir(self):
        for res in self:
            res.stock_akhir_pcs = res.stock_awal_pcs + res.stock_masuk_pcs - res.stock_keluar_pcs

class PwkMutasiVeneerBasahStacking(models.Model):    
    _name = "pwk.mutasi.veneer.basah.stacking"

    reference = fields.Many2one('pwk.mutasi.veneer.basah', 'Reference')
    product_id = fields.Many2one('product.product', 'Product')
    tebal = fields.Float(compute="_get_product_attribute", string='Tebal')
    lebar = fields.Float(compute="_get_product_attribute", string='Lebar')
    panjang = fields.Float(compute="_get_product_attribute", string='Panjang')
    grade = fields.Many2one(compute="_get_product_attribute", comodel_name='pwk.grade', string='Grade')
    stock_awal_pcs = fields.Float(compute="_get_stock_awal", string='Stok Awal (Pcs)')
    stock_awal_vol = fields.Float(compute="_get_volume", string='Stok Awal (M3)', digits=dp.get_precision('FourDecimal'))
    stock_masuk_supplier_pcs = fields.Float('Stok Masuk Supplier (Pcs)')
    stock_masuk_supplier_vol = fields.Float(compute="_get_volume", string='Stok Masuk Supplier (M3)', digits=dp.get_precision('FourDecimal'))
    acc_stock_masuk_supplier_pcs = fields.Float(compute="_get_acc", string='Stok Masuk Supplier')
    acc_stock_masuk_supplier_vol = fields.Float(compute="_get_volume", string='Stok Masuk Supplier', digits=dp.get_precision('FourDecimal'))
    stock_masuk_rotary_pcs = fields.Float('Stok Masuk Rotary (Pcs)')    
    stock_masuk_rotary_vol = fields.Float(compute="_get_volume", string='Stok Masuk Rotary (M3)', digits=dp.get_precision('FourDecimal'))
    acc_stock_masuk_rotary_pcs = fields.Float(compute="_get_acc", string='Stock Masuk Rotary')
    acc_stock_masuk_rotary_vol = fields.Float(compute="_get_volume", string='Stock Masuk Rotary (M3)', digits=dp.get_precision('FourDecimal'))
    stock_keluar_stacking_pcs = fields.Float('Stok Keluar Stacking (Pcs)')    
    stock_keluar_stacking_vol = fields.Float(compute="_get_volume", string='Stok Keluar Stacking (M3)', digits=dp.get_precision('FourDecimal'))
    acc_stock_keluar_stacking_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Stacking')
    acc_stock_keluar_stacking_vol = fields.Float(compute="_get_volume", string='Stok Keluar Stacking', digits=dp.get_precision('FourDecimal'))
    stock_keluar_roler_pcs = fields.Float('Stok Keluar Roler (Pcs)')    
    stock_keluar_roler_vol = fields.Float(compute="_get_volume", string='Stok Keluar Roler', digits=dp.get_precision('FourDecimal'))
    acc_stock_keluar_roler_pcs = fields.Float(compute="_get_acc", string='Stok Keluar Roler')
    acc_stock_keluar_roler_vol = fields.Float(compute="_get_volume", string='Stok Keluar Roler', digits=dp.get_precision('FourDecimal'))
    stock_akhir_pcs = fields.Float(compute="_get_stock_akhir", string='Stok Akhir (Pcs)')
    stock_akhir_vol = fields.Float(compute="_get_volume", string='Stok Akhir (M3)', digits=dp.get_precision('FourDecimal'))

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
            res.stock_awal_vol = res.stock_awal_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.stock_masuk_rotary_vol = res.stock_masuk_rotary_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.stock_masuk_supplier_vol = res.stock_masuk_supplier_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.stock_keluar_roler_vol = res.stock_keluar_roler_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.stock_keluar_stacking_vol = res.stock_keluar_stacking_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.acc_stock_masuk_rotary_vol = res.acc_stock_masuk_rotary_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.acc_stock_masuk_supplier_vol = res.acc_stock_masuk_supplier_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.acc_stock_keluar_roler_vol = res.acc_stock_keluar_roler_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.acc_stock_keluar_stacking_vol = res.acc_stock_keluar_stacking_pcs * res.tebal * res.lebar * res.panjang / 1000000000
            res.stock_akhir_vol = res.stock_akhir_pcs * res.tebal * res.lebar * res.panjang / 1000000000

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
            res.acc_stock_keluar_roler_pcs = acc_stock_keluar_roler_pcs + res.stock_keluar_roler_pcs
            res.acc_stock_keluar_stacking_pcs = acc_stock_keluar_stacking_pcs + res.stock_keluar_stacking_pcs

    @api.depends('stock_awal_pcs','stock_masuk_rotary_pcs','stock_masuk_supplier_pcs','stock_keluar_roler_pcs','stock_keluar_stacking_pcs')
    def _get_stock_akhir(self):
        for res in self:
            res.stock_akhir_pcs = res.stock_awal_pcs + res.stock_masuk_rotary_pcs + res.stock_masuk_supplier_pcs - res.stock_keluar_roler_pcs - res.stock_keluar_stacking_pcs

class PwkMutasiVeneerBasah(models.Model):    
    _name = "pwk.mutasi.veneer.basah"
    _inherit = ["mail.thread", "mail.activity.mixin", "report.report_xlsx.abstract"]


    name = fields.Char('No. Dokumen', track_visibility="always")
    date = fields.Date('Tanggal', default=fields.Date.today(), track_visibility="always")
    user_id = fields.Many2one('res.users', string="Dibuat Oleh", default=lambda self: self.env.user, track_visibility="always")
    state = fields.Selection([('Draft','Draft'),('Approved','Approved')], string="Status", default="Draft", track_visibility="always")
    stacking_ids = fields.One2many('pwk.mutasi.veneer.basah.stacking', 'reference', string="Stacking", track_visibility="always")
    kd_ids = fields.One2many('pwk.mutasi.veneer.basah.kd', 'reference', string="In KD", track_visibility="always")

    def get_sequence(self, name=False, obj=False, context=None):
        sequence_id = self.env['ir.sequence'].search([
            ('name', '=', name),
            ('code', '=', obj),
            ('suffix', '=', '.MVBS.%(month)s.%(year)s')
        ])
        if not sequence_id :
            sequence_id = self.env['ir.sequence'].sudo().create({
                'name': name,
                'code': obj,
                'implementation': 'no_gap',
                'suffix': '.MVBS.%(month)s.%(year)s',
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

    @api.multi
    def button_cancel(self):
        for res in self:
            res.state = "Draft"

    @api.multi
    def button_reload_kd(self):
        for res in self:
            source_ids = self.env['pwk.mutasi.veneer.basah.stacking'].search([
                ('reference.date','=',res.date),
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.veneer.basah.stacking'].search([
                    ('reference.date','<',res.date),
                    ])

            if source_ids:
                for source in source_ids:
                    self.env['pwk.mutasi.veneer.basah.kd'].create({
                        'reference': res.id,
                        'product_id': source.product_id.id,
                        })

    @api.multi
    def button_reload_line(self):
        for res in self:
            source_ids = self.env['pwk.mutasi.veneer.basah.stacking'].search([
                ('reference.date','=',res.date - timedelta(1)),
                ])

            if not source_ids:
                source_ids = self.env['pwk.mutasi.veneer.basah.stacking'].search([
                    ('reference.date','<',res.date),
                    ])

            if source_ids:
                for source in source_ids:
                    self.env['pwk.mutasi.veneer.basah.stacking'].create({
                        'reference': res.id,
                        'product_id': source.product_id.id,
                        })

    @api.multi
    def button_print(self, workbook, data, lines):
        alamat = ' Jl. Raya Krangan - Pringsurat, Karanglo, Kupen, Kec. Pringsurat, Kabupaten Temanggung, Jawa Tengah 56272'

        sheet = workbook.add_worksheet('Laporan PEB')
        format0 = workbook.add_format({'font_size': 20, 'align': 'center', 'bold': True})
        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        formatHeaderCompany = workbook.add_format({'font_size': 12, 'align': 'left', 'bold': True})
        formatHeader = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left', 'bold': False, 'text_wrap': True})
        formatHeaderCenter = workbook.add_format({'font_size': 14, 'valign':'vcenter', 'align': 'center', 'bold': True, 'text_wrap': True})
        formatHeaderRight = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left', 'num_format': '#,##0'})
        formatHeaderTable = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'bold': True, 'bg_color':'#4ead2f', 'color':'white', 'text_wrap': True})
        formatHeaderTableRight = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'right', 'bold': True, 'bg_color':'#3eaec2', 'text_wrap': True, 'num_format': '#,##0'})
        formatHeaderDetailCenter = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True})
        formatHeaderDetailCenterNumber = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': '#,##0'})
        formatHeaderDetailCenterNumberFour = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': '#,##4'})
        formatHeaderDetailLeft = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left'})
        formatHeaderDetailRight = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'right', 'num_format': '#,##0'})
        format11 = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True})
        format21 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True})
        format3 = workbook.add_format({'bottom': True, 'top': True, 'font_size': 12})
        format4 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold': True})
        font_size_8 = workbook.add_format({'font_size': 8, 'align': 'center'})
        font_size_8_l = workbook.add_format({'font_size': 8, 'align': 'left'})
        font_size_8_r = workbook.add_format({'font_size': 8, 'align': 'right'})
        red_mark = workbook.add_format({'font_size': 8, 'bg_color': 'red'})
        justify = workbook.add_format({'font_size': 12})
        
        formatHeaderTable.set_border(1)
        formatHeaderTableRight.set_border(1)
        formatHeaderDetailCenter.set_border(1)
        formatHeaderDetailCenterNumber.set_border(1)
        formatHeaderDetailCenterNumberFour.set_border(1)
        formatHeaderDetailRight.set_border(1)
        formatHeaderDetailLeft.set_border(1)

        formatHeaderTable.set_text_wrap()
        formatHeaderTableRight.set_text_wrap()
        formatHeaderDetailCenter.set_text_wrap()
        formatHeaderDetailRight.set_text_wrap()
        formatHeaderDetailLeft.set_text_wrap()
        
        # Set Column Width
        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 1, 35)
        sheet.set_column(2, 2, 15)
        sheet.set_column(3, 3, 25)
        sheet.set_column(4, 4, 15)
        sheet.set_column(5, 5, 15)
        sheet.set_column(6, 6, 25)
        sheet.set_column(7, 7, 15)
        sheet.set_column(8, 8, 15)
        sheet.set_column(9, 9, 15)
        sheet.set_column(10, 10, 15)
        sheet.set_column(11, 11, 15)
        sheet.set_column(12, 12, 15)
        sheet.set_column(13, 13, 15)
        sheet.set_column(14, 14, 15)
        sheet.set_column(15, 15, 15)
        sheet.set_column(16, 16, 15)
        sheet.set_column(17, 17, 15)        

        sheet.set_row(8, 25)
        sheet.set_row(9, 30)

        # Header        
        sheet.merge_range(4, 0, 4, 16, 'REKAPITULASI LAPORAN PEMBERITAHUAN EKSPOR BARANG (PEB)', formatHeaderCenter)
        sheet.merge_range(5, 0, 5, 16, 'PT. PRIMA WANA KREASI WOOD INDUSTRY', formatHeaderCenter)
        sheet.merge_range(6, 0, 6, 16, 'BULAN : MARET', formatHeaderCenter)        

        # Table Header
        sheet.merge_range(8, 0, 9, 0, 'NO', formatHeaderTable)
        sheet.merge_range(8, 1, 9, 1, 'NAMA', formatHeaderTable)
        sheet.merge_range(8, 2, 9, 2, 'NO. TDP', formatHeaderTable)
        sheet.merge_range(8, 3, 9, 3, 'ALAMAT', formatHeaderTable)
        sheet.merge_range(8, 4, 8, 6, 'Dokumen Pelengkap Ekspor', formatHeaderTable)
        sheet.merge_range(8, 7, 8, 10, 'Data Barang Ekspor Sesuai PEB', formatHeaderTable)
        sheet.merge_range(8, 11, 9, 11, 'BUYER', formatHeaderTable)
        sheet.merge_range(8, 12, 9, 12, 'LC / TT', formatHeaderTable)
        sheet.merge_range(8, 13, 9, 13, 'CNF / FOB', formatHeaderTable)
        sheet.merge_range(8, 14, 9, 14, 'Kurs BI', formatHeaderTable)
        sheet.merge_range(8, 15, 9, 15, 'Kurs MK', formatHeaderTable)
        sheet.merge_range(8, 16, 9, 16, 'TOTAL ( Kurs MK x Volume )', formatHeaderTable)

        sheet.write(9, 4, 'No. & Tgl. Dokumen V-Legal', formatHeaderTable)
        sheet.write(9, 5, 'No. & Tgl. PEB', formatHeaderTable)
        sheet.write(9, 6, 'Lokasi Stuffing', formatHeaderTable)
        sheet.write(9, 7, 'Volume ( M3 )', formatHeaderTable)
        sheet.write(9, 8, 'Netto ( Kg )', formatHeaderTable)
        sheet.write(9, 9, 'Jumlah ( Unit )', formatHeaderTable)
        sheet.write(9, 10, 'Nilai ( USD )', formatHeaderTable)                

        row = 10
        number = 1
        # for i in get_invoice:         
        #     sheet.set_row(row, 55)
        #     sheet.write(row, 0, number, formatHeaderDetailCenter)
        #     sheet.write(row, 1, 'PT. PRIMA WANA KREASI WOOD INDUSTRY', formatHeaderDetailCenter)            
        #     sheet.write(row, 2, i['tdp'], formatHeaderDetailCenter)
        #     sheet.write(row, 3, alamat, formatHeaderDetailCenter)
        #     sheet.write(row, 4, '', formatHeaderDetailCenter)
        #     sheet.write(row, 5, '', formatHeaderDetailCenter)
        #     sheet.write(row, 6, alamat, formatHeaderDetailCenter)
        #     sheet.write(row, 7, i['volume'], formatHeaderDetailCenterNumberFour)
        #     sheet.write(row, 8, i['netto'], formatHeaderDetailCenterNumber)
        #     sheet.write(row, 9, i['jumlah'], formatHeaderDetailCenterNumber)
        #     sheet.write(row, 10, i['nilai'], formatHeaderDetailCenterNumber)
        #     sheet.write(row, 11, i['buyer'], formatHeaderDetailCenter)
        #     sheet.write(row, 12, i['lc_tt'], formatHeaderDetailCenter)
        #     sheet.write(row, 13, i['cnf_fob'], formatHeaderDetailCenter)
        #     sheet.write(row, 14, i['kurs_bi'], formatHeaderDetailCenterNumber)
        #     sheet.write(row, 15, i['kurs_mk'], formatHeaderDetailCenterNumber)
        #     sheet.write(row, 16, i['total'], formatHeaderDetailCenterNumber)
        #     # sheet.write_formula(row, 16, '{=SUM(B1:C1*B2:C2)}', cell_format, 2005)
        #     row += 1
        #     number += 1