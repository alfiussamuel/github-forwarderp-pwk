# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from cStringIO import StringIO
import base64
import xlsxwriter
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError, except_orm, Warning, RedirectWarning, ValidationError


class ExcelLaporanPertanggungjawaban(models.TransientModel):
    _name = 'bc.laporan.posisi'

    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date', default=fields.Date.today())
    state_position = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    data = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)

    @api.multi
    def generate_report(self):
        filename = 'Laporan Posisi.xlsx'

        fp = StringIO()
        workbook = xlsxwriter.Workbook(fp)
        #################################################################################
        center_title = workbook.add_format({'bold': 1, 'valign':'vcenter', 'align':'center'})
        center_title.set_font_size('13')
        center_title.set_bg_color('#eff0f2')
        center_title.set_border()
        #################################################################################
        left_title = workbook.add_format({'bold': 1, 'valign':'vcenter', 'align':'left'})
        left_title.set_font_size('13')
        left_title.set_bg_color('#eff0f2')
        left_title.set_border()
        #################################################################################
        bold_font = workbook.add_format({'bold': 1, 'valign':'vcenter', 'align':'left'})
        bold_font.set_text_wrap()
        #################################################################################
        header_table = workbook.add_format({'bold': 1, 'valign':'vcenter', 'align':'center'})
        header_table.set_text_wrap()
        header_table.set_bg_color('#eff0f2')
        header_table.set_border()
        #################################################################################
        footer_table = workbook.add_format({'bold': 1, 'valign':'vcenter', 'align':'right'})
        footer_table.set_text_wrap()
        footer_table.set_border()
        #################################################################################
        set_right = workbook.add_format({'valign':'vcenter', 'align':'right'})
        set_right.set_text_wrap()
        set_right.set_border()
        #################################################################################
        set_center = workbook.add_format({'valign':'vcenter', 'align':'center'})
        set_center.set_text_wrap()
        set_center.set_border()
        #################################################################################
        set_border = workbook.add_format({'valign':'vcenter', 'align':'left'})
        set_border.set_text_wrap()
        set_border.set_border()

        product_ids = self.env['product.product'].search([
            ('active','=',True)
            ])
                  
        worksheet1 = workbook.add_worksheet('All Account')
        worksheet1.set_column('A:A', 5)
        worksheet1.set_column('B:B', 7)
        worksheet1.set_column('C:C', 10)
        worksheet1.set_column('D:D', 10)
        worksheet1.set_column('E:E', 10)
        worksheet1.set_column('F:F', 10)
        worksheet1.set_column('G:G', 10)
        worksheet1.set_column('H:H', 20)
        worksheet1.set_column('I:I', 10)
        worksheet1.set_column('J:J', 10)
        worksheet1.set_column('K:K', 10)
        worksheet1.set_column('L:L', 10)
        worksheet1.set_column('M:M', 10)
        worksheet1.set_column('N:N', 10)
        worksheet1.set_column('O:O', 10)
        worksheet1.set_column('P:P', 10)
        worksheet1.set_column('Q:Q', 10)
        worksheet1.set_column('R:R', 20)
        worksheet1.set_column('S:S', 10)
        worksheet1.set_column('T:T', 10)
        worksheet1.set_column('U:U', 10)
        worksheet1.set_column('V:V', 10)
        worksheet1.set_column('W:W', 10)
        worksheet1.set_row(1, 50)
        worksheet1.set_row(3, 30)

        bc_type = self.env['ir.config_parameter'].sudo().get_param('bc_type')
        kbgb = ""
        if bc_type==0:
            kbgb = "Kawasan Berikat"
        else:
            kbgb = "Gudang Berikat"


        worksheet1.merge_range('A2:X2', 'Laporan Posisi Barang Per Dokumen Pabean', left_title)
        worksheet1.merge_range('A3:X3', kbgb+' ' + self.env.user.company_id.name, left_title)
        worksheet1.merge_range('A4:X4', 'Periode: ' + datetime.strptime(self.date_from, '%Y-%m-%d').strftime('%d %m %Y') + ' s.d ' + datetime.strptime(self.date_from, '%Y-%m-%d').strftime('%d %m %Y'), left_title) 
        row = 4
        # worksheet1.write(row, 0, 'No', header_table)
        worksheet1.merge_range('A5:A6', 'No', header_table)
        worksheet1.merge_range('B5:K5', 'Dokumen Pemasukan', header_table)
        worksheet1.merge_range('L5:U5', 'Dokumen Pengeluaran', header_table)
        worksheet1.merge_range('V5:X5', 'Saldo', header_table)
        worksheet1.write(row+1, 1, 'Jenis', header_table)
        worksheet1.write(row+1, 2, 'Nomor', header_table)
        worksheet1.write(row+1, 3, 'Tanggal', header_table)
        worksheet1.write(row+1, 4, 'Tanggal Masuk', header_table)
        worksheet1.write(row+1, 5, 'Kode Barang', header_table)
        worksheet1.write(row+1, 6, 'Seri Barang', header_table)
        worksheet1.write(row+1, 7, 'Nama Barang', header_table)
        worksheet1.write(row+1, 8, 'Satuan', header_table)
        worksheet1.write(row+1, 9, 'Jumlah', header_table)
        worksheet1.write(row+1, 10, 'Nilai Pabean', header_table)
        worksheet1.write(row+1, 11, 'Jenis', header_table)
        worksheet1.write(row+1, 12, 'Nomor', header_table)
        worksheet1.write(row+1, 13, 'Tanggal', header_table)
        worksheet1.write(row+1, 14, 'Tanggal Keluar', header_table)
        worksheet1.write(row+1, 15, 'Kode Barang', header_table)
        worksheet1.write(row+1, 16, 'Seri Barang', header_table)
        worksheet1.write(row+1, 17, 'Nama Barang', header_table)
        worksheet1.write(row+1, 18, 'Satuan', header_table)
        worksheet1.write(row+1, 19, 'Jumlah', header_table)
        worksheet1.write(row+1, 20, 'Nilai Pabean', header_table)
        worksheet1.write(row+1, 21, 'Jumlah', header_table)
        worksheet1.write(row+1, 22, 'Satuan', header_table)
        worksheet1.write(row+1, 23, 'Nilai PAB', header_table)
        row = row+1
        i = 0
        pemasukan_ids = self.env['beacukai.incoming.line'].search([
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ])
        if pemasukan_ids:
            for product in pemasukan_ids:
                row += 1
                i += 1
                saldo_jumlah = 0
                saldo_pab = 0
                worksheet1.write(row,0,i,set_center)
                worksheet1.write(row, 1, product.reference.document_type_id.name, set_border)
                worksheet1.write(row, 2, product.reference.submission_no, set_border)
                worksheet1.write(row, 3, product.reference.date, set_border)
                if product.reference.delivery_note_date:
                    worksheet1.write(row, 4, product.reference.delivery_note_date, set_border)    
                else:
                    worksheet1.write(row, 4, "", set_border)    
                worksheet1.write(row, 5, product.product_hs_code, set_border)
                worksheet1.write(row, 6, "", set_border)
                worksheet1.write(row, 7, product.product_name, set_border)
                worksheet1.write(row, 8, product.product_uom_id.name, set_border)
                worksheet1.write(row, 9, product.product_amount, set_border)
                worksheet1.write(row, 10, product.product_price, set_border)
                saldo_jumlah = saldo_jumlah + product.product_amount
                saldo_pab = saldo_pab + product.product_price
                if len(product.outgoing_ids)>0:
                    for outgoing in product.outgoing_ids:
                        worksheet1.write(row, 11, outgoing.reference.document_type_id.name, set_border)
                        worksheet1.write(row, 12, outgoing.reference.submission_no, set_border)
                        if outgoing.reference.date:
                            worksheet1.write(row, 13, outgoing.reference.date, set_border)
                        else:
                            worksheet1.write(row, 13, "", set_border)
                        if outgoing.reference.delivery_note_date:
                            worksheet1.write(row, 14, outgoing.reference.delivery_note_date, set_border)
                        else:
                            worksheet1.write(row, 14, "", set_border)
                        if outgoing.product_hs_code:
                            worksheet1.write(row, 15, outgoing.product_hs_code, set_border)
                        else:
                            worksheet1.write(row, 15, "", set_border)
                        worksheet1.write(row, 16, "", set_border)
                        worksheet1.write(row, 17, outgoing.product_name, set_border)
                        worksheet1.write(row, 18, outgoing.product_uom_id.name, set_border)
                        worksheet1.write(row, 19, outgoing.product_amount, set_border)
                        worksheet1.write(row, 20, outgoing.product_price, set_border)    
                        saldo_jumlah = saldo_jumlah + outgoing.product_amount
                        saldo_pab = saldo_pab + outgoing.product_price
                        worksheet1.write(row, 21, '', set_border)    
                        worksheet1.write(row, 22, '', set_border)
                        worksheet1.write(row, 23, '', set_border)
                        row+=1
                        worksheet1.merge_range("A%s:U%s"%(row,row), '', left_title)
                        worksheet1.write(row, 21, saldo_jumlah, set_border)    
                        worksheet1.write(row, 22, product.product_uom_id.name, set_border)
                        worksheet1.write(row, 23, saldo_pab, set_border)
                else:    
                    worksheet1.write(row, 11, "", set_border)
                    worksheet1.write(row, 12, "", set_border)
                    worksheet1.write(row, 13, "", set_border)
                    worksheet1.write(row, 14, "", set_border)
                    worksheet1.write(row, 15, "", set_border)
                    worksheet1.write(row, 16, "", set_border)
                    worksheet1.write(row, 17, "", set_border)
                    worksheet1.write(row, 18, "", set_border)
                    worksheet1.write(row, 19, "", set_border)
                    worksheet1.write(row, 20, "", set_border)    
                    saldo_jumlah = saldo_jumlah + outgoing.product_amount
                    saldo_pab = saldo_pab + outgoing.product_price
                    row+=1
                    worksheet1.write(row, 21, "", set_border)    
                    worksheet1.write(row, 22, "", set_border)
                    worksheet1.write(row, 23, "", set_border)

        pengusaha = self.env['beacukai.apiu'].search([],limit=1)                    
        worksheet1.write(row+3,18, 'KAMI BERTANGGUNG JAWAB')
        worksheet1.write(row+4,18, 'ATAS KEBENARAN LAPORAN INI')
        worksheet1.write(row+5,18, str(self.env.user.company_id.city).upper()+', ' + datetime.today().strftime('%d %m %Y'))
        worksheet1.write(row+6,18, 'PENGUSAHA DI '+str(kbgb).upper())
        worksheet1.write(row+10,18, str(pengusaha.name).upper())
        worksheet1.write(row+11,18, str(pengusaha.jabatan).upper())
    
        workbook.close()
        out = base64.encodestring(fp.getvalue())
        self.write({'data':out, 'name': filename, 'state_position': 'get'})
        fp.close()
        ir_model_data = self.env['ir.model.data']
        form_res = ir_model_data.get_object_reference(
            'v10_bsc_beacukai', 'bc_laporan_posisi_form')
        form_id = form_res and form_res[1] or False
        return {
            'name': ('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'bc.laporan.posisi',
            'res_id': self.id,
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }
