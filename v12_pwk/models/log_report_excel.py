# -*- coding: utf-8 -*-

import datetime
from datetime import datetime
from datetime import date,timedelta
import pytz
from odoo import models


class LogReportXls(models.AbstractModel):
    _name = 'report.v12_pwk.log_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_invoice(self, data):        
        start_date = data.start_date
        end_date = data.end_date        
        lines = []
        vals = {}                

        while start_date < end_date:
            start_date += timedelta(days=1)
            qty_albasia_masuk = volume_albasia_masuk = 0
            qty_jabon_masuk = volume_jabon_masuk = 0
            qty_jenitri_masuk = volume_jenitri_masuk = 0
            qty_albasia_total = volume_albasia_total = 0
            qty_jabon_total = volume_jabon_total = 0
            qty_jenitri_total = volume_jenitri_total= 0

            albasia_ids = self.env['purchase.order.line'].search([
                ('product_id.jenis_kayu.name','>=','Albasia'),
                ('order_id.state','=','purchase'),
                ('order_id.purchase_type','=','Rotary'),
                ('order_id.date_order','=',start_date)
                ], order="id asc")

            jabon_ids = self.env['purchase.order.line'].search([
                ('product_id.jenis_kayu.name','>=','Jabon'),
                ('order_id.state','=','purchase'),
                ('order_id.purchase_type','=','Rotary'),
                ('order_id.date_order','=',start_date)
                ], order="id asc")

            jenitri_ids = self.env['purchase.order.line'].search([
                ('product_id.jenis_kayu.name','>=','Jenitri'),
                ('order_id.state','=','purchase'),
                ('order_id.purchase_type','=','Rotary'),
                ('order_id.date_order','=',start_date)
                ], order="id asc")

            if albasia_ids:
                for albasia in albasia_ids:
                    qty_albasia_masuk += albasia.product_qty
                    volume_albasia_masuk += albasia.volume_real

            if jabon_ids:
                for jabon in jabon_ids:
                    qty_jabon_masuk += jabon.product_qty
                    volume_jabon_masuk += jabon.volume_real

            if jenitri_ids:
                for jenitri in jenitri_ids:
                    qty_jenitri_masuk += jenitri.product_qty
                    volume_jenitri_masuk += jenitri.volume_real

            vals = {
                'date' : start_date,
                'qty_albasia_masuk' : qty_albasia_masuk,
                'volume_albasia_masuk' : volume_albasia_masuk,
                'qty_jabon_masuk' : qty_jabon_masuk,
                'volume_jabon_masuk' : volume_jabon_masuk,
                'qty_jenitri_masuk' : qty_jenitri_masuk,
                'volume_jenitri_masuk' : volume_jenitri_masuk,
                'qty_albasia_keluar' : 0,
                'volume_albasia_keluar' : 0,
                'qty_jabon_keluar' : 0,
                'volume_jabon_keluar' : 0,
                'qty_jenitri_keluar' : 0,
                'volume_jenitri_keluar' : 0,
                'qty_albasia_total' : qty_albasia_total,
                'volume_albasia_total' : volume_albasia_total,
                'qty_jabon_total' : qty_jabon_total,
                'volume_jabon_total' : volume_jabon_total,
                'qty_jenitri_total' : qty_jenitri_total,
                'volume_jenitri_total' : volume_jenitri_total,
            }

            lines.append(vals)

        return lines

    def generate_xlsx_report(self, workbook, data, lines):
        get_invoice = self.get_invoice(lines)        
        start_date = lines.start_date
        end_date = lines.end_date        
        alamat = ' Jl. Raya Krangan - Pringsurat, Karanglo, Kupen, Kec. Pringsurat, Kabupaten Temanggung, Jawa Tengah 56272'

        sheet = workbook.add_worksheet('Laporan Harian Stock Log')
        format0 = workbook.add_format({'font_size': 20, 'align': 'center', 'bold': True})
        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        formatHeaderCompany = workbook.add_format({'font_size': 12, 'align': 'left', 'bold': True})
        formatHeader = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left', 'bold': False, 'text_wrap': True})
        formatHeaderCenter12 = workbook.add_format({'font_size': 12, 'valign':'vcenter', 'align': 'center', 'bold': True, 'text_wrap': True})
        formatHeaderCenter = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'center', 'bold': True, 'text_wrap': True})
        formatHeaderCenterDate = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': 'dd-mm-yyyy'})
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
        
        formatHeaderCenter.set_border(1)
        formatHeaderCenter12.set_border(1)
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
        sheet.set_column(1, 1, 10)
        sheet.set_column(2, 2, 10)
        sheet.set_column(3, 3, 10)
        sheet.set_column(4, 4, 10)
        sheet.set_column(5, 5, 10)
        sheet.set_column(6, 6, 10)
        sheet.set_column(7, 7, 10)
        sheet.set_column(8, 8, 10)
        sheet.set_column(9, 9, 10)
        sheet.set_column(10, 10, 10)
        sheet.set_column(11, 11, 10)
        sheet.set_column(12, 12, 10)
        sheet.set_column(13, 13, 10)
        sheet.set_column(14, 14, 10)
        sheet.set_column(15, 15, 10)
        sheet.set_column(16, 16, 10)
        sheet.set_column(17, 17, 10)        
        sheet.set_column(18, 18, 10)        
        sheet.set_column(19, 19, 10)                

        # Header                
        sheet.merge_range(0, 0, 0, 3, 'PT. PRIMA WANA KREASI WOOD INDUSTRY', formatHeader)
        sheet.merge_range(1, 0, 1, 3, 'TEMANGGUNG', formatHeader)
        sheet.merge_range(3, 0, 3, 19, 'LAPORAN HARIAN STOCK LOG', formatHeaderCenter12)
        sheet.merge_range(4, 0, 4, 19, str(start_date) + ' s/d ' + str(end_date), formatHeaderCenter12)

        # Table Header
        sheet.merge_range(5, 0, 5, 1, '', formatHeaderTable)
        sheet.merge_range(5, 2, 5, 7, 'ALBASIA 130', formatHeaderTable)
        sheet.merge_range(5, 8, 5, 13, 'JABON', formatHeaderTable)
        sheet.merge_range(5, 14, 5, 19, 'JENITRI', formatHeaderTable)

        sheet.merge_range(6, 0, 7, 0, 'NO', formatHeaderCenter)
        sheet.merge_range(6, 1, 7, 1, 'TANGGAL', formatHeaderCenter)
        sheet.merge_range(6, 2, 6, 3, 'LOG MASUK', formatHeaderCenter)
        sheet.merge_range(6, 4, 6, 5, 'LOG KELUAR', formatHeaderCenter)
        sheet.merge_range(6, 6, 6, 7, 'STOCK LOG', formatHeaderCenter)
        sheet.merge_range(6, 8, 6, 9, 'LOG MASUK', formatHeaderCenter)
        sheet.merge_range(6, 10, 6, 11, 'LOG KELUAR', formatHeaderCenter)
        sheet.merge_range(6, 12, 6, 13, 'STOCK LOG', formatHeaderCenter)
        sheet.merge_range(6, 14, 6, 15, 'LOG MASUK', formatHeaderCenter)
        sheet.merge_range(6, 16, 6, 17, 'LOG KELUAR', formatHeaderCenter)
        sheet.merge_range(6, 18, 6, 19, 'STOCK LOG', formatHeaderCenter)

        sheet.write(7, 2, 'BTG', formatHeaderCenter)
        sheet.write(7, 3, 'M3', formatHeaderCenter)
        sheet.write(7, 4, 'BTG', formatHeaderCenter)
        sheet.write(7, 5, 'M3', formatHeaderCenter)
        sheet.write(7, 6, 'BTG', formatHeaderCenter)
        sheet.write(7, 7, 'M3', formatHeaderCenter)
        sheet.write(7, 8, 'BTG', formatHeaderCenter)
        sheet.write(7, 9, 'M3', formatHeaderCenter)
        sheet.write(7, 10, 'BTG', formatHeaderCenter)
        sheet.write(7, 11, 'M3', formatHeaderCenter)
        sheet.write(7, 12, 'BTG', formatHeaderCenter)
        sheet.write(7, 13, 'M3', formatHeaderCenter)
        sheet.write(7, 14, 'BTG', formatHeaderCenter)
        sheet.write(7, 15, 'M3', formatHeaderCenter)
        sheet.write(7, 16, 'BTG', formatHeaderCenter)
        sheet.write(7, 17, 'M3', formatHeaderCenter)
        sheet.write(7, 18, 'BTG', formatHeaderCenter)
        sheet.write(7, 19, 'M3', formatHeaderCenter)

        row = 8
        number = 1   
        for i in get_invoice:     
            sheet.write(row, 0, number, formatHeaderDetailCenter)
            sheet.write(row, 1, i['date'], formatHeaderDetailCenterDate)            
            sheet.write(row, 2, i['qty_albasia_masuk'] or '', formatHeaderDetailCenterNumber)
            sheet.write(row, 3, i['volume_albasia_masuk'] or '', formatHeaderDetailCenterNumber)
            sheet.write(row, 4, i['qty_albasia_keluar'] or '', formatHeaderDetailCenterNumber)
            sheet.write(row, 5, i['volume_albasia_keluar'] or '', formatHeaderDetailCenterNumber)
            sheet.write(row, 6, i['qty_albasia_total'] or '', formatHeaderDetailCenterNumber)
            sheet.write(row, 7, i['volume_albasia_total'] or '', formatHeaderDetailCenterNumber)
            sheet.write(row, 8, i['qty_jabon_masuk'] or '', formatHeaderDetailCenterNumber)
            sheet.write(row, 9, i['volume_jabon_masuk'] or '', formatHeaderDetailCenterNumber)
            sheet.write(row, 10, i['qty_jabon_keluar'] or '', formatHeaderDetailCenterNumber)
            sheet.write(row, 11, i['volume_jabon_keluar'] or '', formatHeaderDetailCenterNumber)
            sheet.write(row, 12, i['qty_jabon_total'] or '', formatHeaderDetailCenterNumber)
            sheet.write(row, 13, i['volume_jabon_total'] or '', formatHeaderDetailCenterNumber)
            sheet.write(row, 14, i['qty_jenitri_masuk'] or '', formatHeaderDetailCenterNumber)
            sheet.write(row, 15, i['volume_jenitri_masuk'] or '', formatHeaderDetailCenterNumber)
            sheet.write(row, 16, i['qty_jenitri_keluar'] or '', formatHeaderDetailCenterNumber)
            sheet.write(row, 17, i['volume_jenitri_keluar'] or '', formatHeaderDetailCenterNumber)
            sheet.write(row, 18, i['qty_jenitri_total'] or '', formatHeaderDetailCenterNumber)
            sheet.write(row, 19, i['volume_jenitri_total'] or '', formatHeaderDetailCenterNumber)

            row += 1
            number += 1

