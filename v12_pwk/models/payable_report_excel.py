# -*- coding: utf-8 -*-

import datetime
from datetime import datetime
import pytz
from odoo import models, fields


class PayableReportXls(models.AbstractModel):
    _name = 'report.v12_pwk.payable_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_invoice(self, data):        
        invoice_ids = self.env['account.invoice'].search([                                                    
            ('state','=','open'),
            ('type','=','in_invoice')
        ], order="partner_id asc")

        lines = []
        vals = {}                

        for invoice in invoice_ids:
            due_days = (fields.Date.today() - invoice.date_due).days                    
            vals = {
                'tanggal_penerimaan' : invoice.date_invoice,
                'supplier' : invoice.partner_id.name,
                'nomor_invoice' : invoice.number,
                'tanggal_invoice' : invoice.date_invoice,
                'tanggal_jatuh_tempo' : invoice.date_due,
                'umur_jatuh_tempo' : due_days,
                'nilai_invoice' : invoice.amount_total,
                'deskripsi_barang' : '',
                'keterangan' : '',
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
        formatHeaderLeft = workbook.add_format({'font_size': 14, 'valign':'vcenter', 'align': 'left', 'bold': True, 'text_wrap': True})
        formatHeaderRight = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left', 'num_format': '#,##0'})
        formatHeaderTable = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'bold': True, 'bg_color':'#4ead2f', 'color':'white', 'text_wrap': True})
        formatHeaderTableRight = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'right', 'bold': True, 'bg_color':'#3eaec2', 'text_wrap': True, 'num_format': '#,##0'})
        formatHeaderDetailCenter = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True})
        formatHeaderDetailCenterNumber = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': '#,##0'})
        formatHeaderDetailCenterDate = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': 'dd-mm-yyyy'})
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
        
        # Red for Due Invoices
        formatHeaderDetailCenterRed = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'color':'red'})
        formatHeaderDetailCenterNumberRed = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': '#,##0', 'color':'red'})
        formatHeaderDetailCenterDateRed = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': 'dd-mm-yyyy', 'color':'red'})
        formatHeaderDetailLeftRed = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left', 'color': 'red'})

        formatHeaderTable.set_border(1)
        formatHeaderTableRight.set_border(1)
        formatHeaderDetailCenter.set_border(1)
        formatHeaderDetailCenterNumber.set_border(1)
        formatHeaderDetailCenterNumberFour.set_border(1)
        formatHeaderDetailRight.set_border(1)
        formatHeaderDetailLeft.set_border(1)
        formatHeaderDetailCenterDate.set_border(1)

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
        sheet.merge_range(0, 0, 0, 4, 'PT PRIMA WANA KREASI INDUSTRY', formatHeaderLeft)
        sheet.merge_range(1, 0, 1, 4, 'REKAP HUTANG PRODUKSI', formatHeaderLeft)
        
        # Table Header
        sheet.write(2, 0, 'NO', formatHeaderTable)
        sheet.write(2, 1, 'Tanggal Penerimaan Invoice', formatHeaderTable)
        sheet.write(2, 2, 'Nama Supplier', formatHeaderTable)
        sheet.write(2, 3, 'No. Invoice', formatHeaderTable)
        sheet.write(2, 4, 'Tanggal Invoice', formatHeaderTable)
        sheet.write(2, 5, 'Jatuh Tempo', formatHeaderTable)
        sheet.write(2, 6, 'Outstanding (+/-)', formatHeaderTable)
        sheet.write(2, 7, 'Nilai Invoice', formatHeaderTable)
        sheet.write(2, 8, 'Nama Deskripsi Barang', formatHeaderTable)
        sheet.write(2, 9, 'Keterangan Invoice', formatHeaderTable)
        sheet.write(2, 10, 'Notes', formatHeaderTable)               

        row = 3
        number = 1
        for i in get_invoice:
            if i['umur_jatuh_tempo'] < 0:
                sheet.write(row, 0, number, formatHeaderDetailCenter)
                sheet.write(row, 1, i['tanggal_penerimaan'], formatHeaderDetailCenterDate)            
                sheet.write(row, 2, i['supplier'], formatHeaderDetailCenter)
                sheet.write(row, 3, i['nomor_invoice'], formatHeaderDetailCenter)
                sheet.write(row, 4, i['tanggal_invoice'], formatHeaderDetailCenterDate)
                sheet.write(row, 5, i['tanggal_jatuh_tempo'], formatHeaderDetailCenterDate)
                sheet.write(row, 6, i['umur_jatuh_tempo'], formatHeaderDetailCenter)
                sheet.write(row, 7, i['nilai_invoice'], formatHeaderDetailCenterNumber)
                sheet.write(row, 8, i['deskripsi_barang'], formatHeaderDetailLeft)
                sheet.write(row, 9, i['keterangan'], formatHeaderDetailLeft)
                sheet.write(row, 10, '', formatHeaderDetailCenter)
            elif i['umur_jatuh_tempo'] < 0:
                sheet.write(row, 0, number, formatHeaderDetailCenterRed)
                sheet.write(row, 1, i['tanggal_penerimaan'], formatHeaderDetailCenterDateRed)            
                sheet.write(row, 2, i['supplier'], formatHeaderDetailCenterRed)
                sheet.write(row, 3, i['nomor_invoice'], formatHeaderDetailCenterRed)
                sheet.write(row, 4, i['tanggal_invoice'], formatHeaderDetailCenterDateRed)
                sheet.write(row, 5, i['tanggal_jatuh_tempo'], formatHeaderDetailCenterDateRed)
                sheet.write(row, 6, i['umur_jatuh_tempo'], formatHeaderDetailCenterRed)
                sheet.write(row, 7, i['nilai_invoice'], formatHeaderDetailCenterNumberRed)
                sheet.write(row, 8, i['deskripsi_barang'], formatHeaderDetailLeftRed)
                sheet.write(row, 9, i['keterangan'], formatHeaderDetailLeftRed)
                sheet.write(row, 10, '', formatHeaderDetailCenterRed)
            
            row += 1
            number += 1

