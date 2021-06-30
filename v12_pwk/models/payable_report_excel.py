# -*- coding: utf-8 -*-

import datetime
from datetime import datetime
import pytz
from odoo import models


class PayableReportXls(models.AbstractModel):
    _name = 'report.v12_pwk.payable_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_invoice(self, data):        
        invoice_ids = self.env['account.invoice'].search([                                                    
            ('state','=','open'),
            ('invoice_type_id','=','in_invoice')
        ], order="id asc")

        lines = []
        vals = {}                

        for invoice in invoice_ids:                    
            vals = {
                'tanggal_penerimaan' : invoice.date_invoice,
                'supplier' : invoice.partner_id.name,
                'nomor_invoice' : invoice.number,
                'tanggal_invoice' : invoice.date_invoice,
                'tanggal_jatuh_tempo' : invoice.date_due,
                'umur_jatuh_tempo' : due_days,
                'nilai_invoice' : invoice.amount_total,
                'deskripsi_barang' : product_type,
                'keterangan' : invoice.note,
            }

            lines.append(vals)

        return lines

    def generate_xlsx_report(self, workbook, data, lines):
        get_invoice = self.get_invoice(lines)          
        title = 'Rekap Hutang ' + str(fields.Date.today())      
        alamat = ' Jl. Raya Krangan - Pringsurat, Karanglo, Kupen, Kec. Pringsurat, Kabupaten Temanggung, Jawa Tengah 56272'

        sheet = workbook.add_worksheet(title)
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
        sheet.set_column(1, 1, 15)
        sheet.set_column(2, 2, 35)
        sheet.set_column(3, 3, 15)
        sheet.set_column(4, 4, 15)
        sheet.set_column(5, 5, 15)
        sheet.set_column(6, 6, 15)
        sheet.set_column(7, 7, 15)
        sheet.set_column(8, 8, 15)
        sheet.set_column(9, 9, 15)
        sheet.set_column(10, 10, 15)
        
        # Header        
        sheet.merge_range(0, 0, 0, 4, 'PT PRIMA WANA KREASI INDUSTRY', formatHeaderCenter)
        
        # Table Header
        # sheet.merge_range(8, 0, 9, 0, 'NO', formatHeaderTable)
        # sheet.merge_range(8, 1, 9, 1, 'NAMA', formatHeaderTable)
        # sheet.merge_range(8, 2, 9, 2, 'NO. TDP', formatHeaderTable)
        # sheet.merge_range(8, 3, 9, 3, 'ALAMAT', formatHeaderTable)
        # sheet.merge_range(8, 4, 8, 6, 'Dokumen Pelengkap Ekspor', formatHeaderTable)
        # sheet.merge_range(8, 7, 8, 10, 'Data Barang Ekspor Sesuai PEB', formatHeaderTable)
        # sheet.merge_range(8, 11, 9, 11, 'BUYER', formatHeaderTable)
        # sheet.merge_range(8, 12, 9, 12, 'LC / TT', formatHeaderTable)
        # sheet.merge_range(8, 13, 9, 13, 'CNF / FOB', formatHeaderTable)
        # sheet.merge_range(8, 14, 9, 14, 'Kurs BI', formatHeaderTable)
        # sheet.merge_range(8, 15, 9, 15, 'Kurs MK', formatHeaderTable)
        # sheet.merge_range(8, 16, 9, 16, 'TOTAL ( Kurs MK x Volume )', formatHeaderTable)

        # sheet.write(9, 4, 'No. & Tgl. Dokumen V-Legal', formatHeaderTable)
        # sheet.write(9, 5, 'No. & Tgl. PEB', formatHeaderTable)
        # sheet.write(9, 6, 'Lokasi Stuffing', formatHeaderTable)
        # sheet.write(9, 7, 'Volume ( M3 )', formatHeaderTable)
        # sheet.write(9, 8, 'Netto ( Kg )', formatHeaderTable)
        # sheet.write(9, 9, 'Jumlah ( Unit )', formatHeaderTable)
        # sheet.write(9, 10, 'Nilai ( USD )', formatHeaderTable)                

        # row = 10
        # number = 1
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

