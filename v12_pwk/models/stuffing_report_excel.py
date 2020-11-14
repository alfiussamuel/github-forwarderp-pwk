# -*- coding: utf-8 -*-

import datetime
from datetime import datetime
import pytz
from odoo import models


class StuffingReportXls(models.AbstractModel):
    _name = 'report.v12_pwk.stuffing_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_invoice(self, data):        
        start_date = data.start_date
        end_date = data.end_date

        if data.report_type == "Export":
            invoice_ids = self.env['account.invoice.line'].search([                                                    
                            ('invoice_id.date_invoice','>=',start_date),
                            ('invoice_id.date_invoice','<=',end_date),
                            ('invoice_id.invoice_type','=','Export'),
                            ('invoice_id.state','in',('open','paid')),
                            ], order="id asc")

        elif data.report_type == "Local":
            invoice_ids = self.env['account.invoice.line'].search([                                                    
                            ('invoice_id.date_invoice','>=',start_date),
                            ('invoice_id.date_invoice','<=',end_date),
                            ('invoice_id.invoice_type','=','Lokal'),
                            ('invoice_id.state','in',('open','paid')),
                            ], order="id asc")

        lines = []
        vals = {}                

        for invoice in invoice_ids:                    
            vals = {
                'tanggal' : invoice.invoice_id.date_invoice,
                'produk' : invoice.product_id.name,
                'grade' : invoice.product_id.grade_id.name,
                'tebal' : invoice.product_id.tebal,
                'lebar' : invoice.product_id.lebar,
                'panjang' : invoice.product_id.panjang,
                'pcs' : invoice.sheets,
                'volume' : invoice.quantity,
                'invoice' : invoice.invoice_id.number,
                'tujuan' : invoice.invoice_id.destination.name,
                'nota_perusahaan' : '',
                'surat_jalan' : '',
                'nomor_polisi' : invoice.invoice_id.vessel_name,
                'nomor_container' : invoice.invoice_id.container_no,
                'nomor_seal' : invoice.invoice_id.seal_no,
                'jumlah_container' : invoice.invoice_id.container_number,
                'keterangan' : invoice.remarks,
            }

            lines.append(vals)

        return lines

    def generate_xlsx_report(self, workbook, data, lines):
        get_invoice = self.get_invoice(lines)        
        start_date = lines.start_date
        end_date = lines.end_date    
        report_type = lines.report_type        
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
        formatHeaderDetailCenterDate = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': 'dd-mm-yyyy'})
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
        formatHeaderDetailCenterDate.set_border(1)
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
        sheet.set_column(2, 2, 50)
        sheet.set_column(3, 3, 10)
        sheet.set_column(4, 4, 10)
        sheet.set_column(5, 5, 10)
        sheet.set_column(6, 6, 10)
        sheet.set_column(7, 7, 12)
        sheet.set_column(8, 8, 12)
        sheet.set_column(9, 9, 20)
        sheet.set_column(10, 10, 18)
        sheet.set_column(11, 11, 18)
        sheet.set_column(12, 12, 18)
        sheet.set_column(13, 13, 18)
        sheet.set_column(14, 14, 18)
        sheet.set_column(15, 15, 18)
        sheet.set_column(16, 16, 18)

        sheet.set_row(6, 25)        

        # Header        
        if report_type == "Export":
            sheet.merge_range(4, 0, 4, 16, 'RECORD STUFFING EXPORT', formatHeaderCenter)        
        else:
            sheet.merge_range(4, 0, 4, 16, 'RECORD STUFFING LOCAL', formatHeaderCenter)        

        # Table Header        
        if report_type == "Export":
            sheet.write(6, 0, 'NO.', formatHeaderTable)
            sheet.write(6, 1, 'TANGGAL', formatHeaderTable)
            sheet.write(6, 2, 'PRODUK', formatHeaderTable)
            sheet.write(6, 3, 'GRADE', formatHeaderTable)
            sheet.write(6, 4, 'T', formatHeaderTable)
            sheet.write(6, 5, 'W', formatHeaderTable)
            sheet.write(6, 6, 'L', formatHeaderTable)
            sheet.write(6, 7, 'PCS', formatHeaderTable)
            sheet.write(6, 8, 'VOL ( M3 )', formatHeaderTable)
            sheet.write(6, 9, 'NO. INV', formatHeaderTable)
            sheet.write(6, 10, 'TUJUAN', formatHeaderTable)
            sheet.write(6, 11, 'NO. NP', formatHeaderTable)
            sheet.write(6, 12, 'NO. SJ', formatHeaderTable)
            sheet.write(6, 13, 'NO. POL', formatHeaderTable)
            sheet.write(6, 14, 'NO. CONT', formatHeaderTable)
            sheet.write(6, 15, 'NO. SEAL', formatHeaderTable)
            sheet.write(6, 16, 'JML CONT', formatHeaderTable)
            sheet.write(6, 17, 'THC / Ocean Freight', formatHeaderTable)
        else:
            sheet.write(6, 0, 'NO.', formatHeaderTable)
            sheet.write(6, 1, 'TANGGAL', formatHeaderTable)
            sheet.write(6, 2, 'PRODUK', formatHeaderTable)
            sheet.write(6, 3, 'GRADE', formatHeaderTable)
            sheet.write(6, 4, 'T', formatHeaderTable)
            sheet.write(6, 5, 'W', formatHeaderTable)
            sheet.write(6, 6, 'L', formatHeaderTable)
            sheet.write(6, 7, 'PCS', formatHeaderTable)
            sheet.write(6, 8, 'VOL ( M3 )', formatHeaderTable)
            sheet.write(6, 9, 'NO. INV', formatHeaderTable)
            sheet.write(6, 10, 'TUJUAN', formatHeaderTable)
            sheet.write(6, 11, 'NO. NP', formatHeaderTable)
            sheet.write(6, 12, 'NO. SJ', formatHeaderTable)
            sheet.write(6, 13, 'NO. POLISI TRUCK ANGKUT', formatHeaderTable)
            sheet.write(6, 14, 'KETERANGAN', formatHeaderTable)
            sheet.write(6, 15, 'BIAYA TRUCKING', formatHeaderTable)

        row = 7
        number = 1
        for i in get_invoice:
            sheet.set_row(row, 20)
            sheet.write(row, 0, number, formatHeaderDetailCenter)
            sheet.write(row, 1, i['tanggal'], formatHeaderDetailCenterDate)            
            sheet.write(row, 2, i['produk'], formatHeaderDetailCenter)
            sheet.write(row, 3, i['grade'], formatHeaderDetailCenter)
            sheet.write(row, 4, i['tebal'], formatHeaderDetailCenterNumber)
            sheet.write(row, 5, i['lebar'], formatHeaderDetailCenterNumber)
            sheet.write(row, 6, i['panjang'], formatHeaderDetailCenterNumber)
            sheet.write(row, 7, i['pcs'], formatHeaderDetailCenterNumber)
            sheet.write(row, 8, i['volume'], formatHeaderDetailCenterNumberFour)
            sheet.write(row, 9, i['invoice'], formatHeaderDetailCenter)
            sheet.write(row, 10, i['tujuan'], formatHeaderDetailCenter)
            sheet.write(row, 11, i['nota_perusahaan'], formatHeaderDetailCenter)
            sheet.write(row, 12, i['surat_jalan'], formatHeaderDetailCenter)
            sheet.write(row, 13, i['nomor_polisi'], formatHeaderDetailCenter)            
            if report_type == "Export":
                sheet.write(row, 14, i['nomor_container'], formatHeaderDetailCenter)
                sheet.write(row, 15, i['nomor_seal'], formatHeaderDetailCenter)
                sheet.write(row, 16, i['jumlah_container'], formatHeaderDetailCenter)
                sheet.write(row, 17, '', formatHeaderDetailCenter)
            else:
                sheet.write(row, 14, i['keterangan'], formatHeaderDetailCenter)
                sheet.write(row, 15, '', formatHeaderDetailCenter)
                
            row += 1
            number += 1

