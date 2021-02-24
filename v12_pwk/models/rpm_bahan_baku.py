# -*- coding: utf-8 -*-

import datetime
from datetime import datetime, timedelta
import pytz
from odoo import models


class RpmBahanBakuReportXls(models.AbstractModel):
    _name = 'report.v12_pwk.rpm_bahan_baku_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_data(self, data):        
        lines = []
        if data.bahan_baku_ids:
            for line in data.bahan_baku_ids:
                vals = {
                    'product_id': line.product_id.goods_type,
                    'glue_id': line.glue_id.name,
                    'grade_id': line.grade_id.name,
                    'tebal': line.thick,
                    'lebar': line.width,
                    'panjang': line.length,
                    'quantity_available': line.quantity_available,
                    'quantity': line.quantity,
                    'volume': line.volume,
                    'quantity_needed': line.quantity_needed,
                    'volume_needed': line.volume_needed,
                    'quantity_spare': line.quantity_spare,
                    'volume_spare': line.volume_spare
                }

                lines.append(vals)

        return lines

    def generate_xlsx_report(self, workbook, data, lines):        
        get_data = self.get_data(lines)
        alamat = ' Jl. Raya Krangan - Pringsurat, Karanglo, Kupen, Kec. Pringsurat, Kabupaten Temanggung, Jawa Tengah 56272'

        sheet = workbook.add_worksheet('Sheet 1')
        format0 = workbook.add_format({'font_size': 20, 'align': 'center', 'bold': True})
        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        formatHeaderCompany = workbook.add_format({'font_size': 12, 'align': 'left', 'bold': True})
        formatHeader = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left', 'bold': False, 'text_wrap': True})
        formatHeaderCenter = workbook.add_format({'font_size': 14, 'valign':'vcenter', 'align': 'center', 'bold': True, 'text_wrap': True})
        formatHeaderCenterNumber = workbook.add_format({'font_size': 14, 'valign':'vcenter', 'align': 'center', 'bold': True, 'text_wrap': True, 'num_format': '#,##0'})
        formatHeaderLeft = workbook.add_format({'font_size': 14, 'valign':'vcenter', 'align': 'left', 'bold': True, 'text_wrap': True})
        formatHeaderRight = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left', 'num_format': '#,##0'})
        formatHeaderTable = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'bold': True, 'bg_color':'#4ead2f', 'color':'white', 'text_wrap': True})
        formatHeaderTablePlain = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'bold': True, 'text_wrap': True})
        formatHeaderTableRight = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'right', 'bold': True, 'bg_color':'#3eaec2', 'text_wrap': True, 'num_format': '#,##0'})
        formatHeaderTableCenterWhite = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'center', 'bold': True, 'text_wrap': True, 'num_format': '#,##0'})
        formatHeaderDetailCenter = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True})
        formatHeaderDetailCenterColor = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'bg_color':'#3eaec2'})
        formatHeaderDetailCenterNumber = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': '#,##0'})
        formatHeaderDetailCenterNumberFour = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': '#,##4'})
        formatHeaderDetailLeft = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left', 'text_wrap': True})
        formatHeaderDetailRight = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'right', 'num_format': '#,##0'})
        formatHeaderDetailRightFour = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'right', 'num_format': '#,##0.0000'})
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
        formatHeaderTableCenterWhite.set_border(1)
        formatHeaderDetailCenter.set_border(1)
        formatHeaderDetailLeft.set_border(1)
        formatHeaderDetailCenterNumber.set_border(1)
        formatHeaderDetailCenterNumberFour.set_border(1)
        formatHeaderDetailRight.set_border(1)
        formatHeaderDetailRightFour.set_border(1)

        formatHeaderTable.set_text_wrap()
        formatHeaderTableRight.set_text_wrap()
        formatHeaderDetailCenter.set_text_wrap()
        formatHeaderDetailRight.set_text_wrap()
        # formatHeaderDetailLeft.set_text_wrap()
        
        # Set Column Width
        sheet.set_column(0, 0, 10)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 6)
        sheet.set_column(3, 3, 6)
        sheet.set_column(4, 4, 6)
        sheet.set_column(5, 5, 10)
        sheet.set_column(6, 6, 10)
        sheet.set_column(7, 7, 10)
        sheet.set_column(8, 8, 10)
        sheet.set_column(9, 9, 10)
        sheet.set_column(10, 10, 10)
        sheet.set_column(11, 11, 10)
        sheet.set_column(12, 12, 10)
        sheet.set_column(13, 13, 30)
        
        # Set default Row height
        # sheet.set_default_row(40)
        # sheet.set_row(4, 16)
        
        # Data 1
        row = 3

        sheet.merge_range(row-2, 0, row - 2, 18, 'KEBUTUHAN BAHAN BAKU', formatHeaderCenter)

        # merge 1 - 3
        sheet.merge_range(3, 0, 4, 5, 'DESCRIPTION', formatHeaderTable)
        sheet.merge_range(3, 6, 5, 6, 'All Stock', formatHeaderTable)
        sheet.merge_range(3, 7, 3, 10, 'Kebutuhan Jan 21', formatHeaderTable)
        sheet.merge_range(3, 11, 5, 11, '+/- Bahan Baku (Pcs)', formatHeaderTable)
        sheet.merge_range(3, 12, 5, 12, '+/- Bahan Baku (M3)', formatHeaderTable)
        sheet.merge_range(3, 13, 5, 13, 'Ket', formatHeaderTable)

        # Row 2
        sheet.merge_range(4, 7, 4, 8, 'Order', formatHeaderTable)
        sheet.merge_range(4, 9, 4, 10, 'Bahan Baku', formatHeaderTable)

        # Row 3
        sheet.write(5, 0, 'Jenis Kayu', formatHeaderTable)
        sheet.write(5, 1, 'Item', formatHeaderTable)
        sheet.write(5, 2, 'T', formatHeaderTable)
        sheet.write(5, 3, 'L', formatHeaderTable)
        sheet.write(5, 4, 'P', formatHeaderTable)
        sheet.write(5, 5, 'Grade', formatHeaderTable)
        sheet.write(5, 7, 'Pcs', formatHeaderTable)
        sheet.write(5, 8, 'M3', formatHeaderTable)
        sheet.write(5, 9, 'Pcs', formatHeaderTable)
        sheet.write(5, 10, 'M3', formatHeaderTable)

        row = 6
        
        if lines.bahan_baku_ids:
            for bahan_baku in lines.bahan_baku_ids:
                sheet.write(row, 0, bahan_baku.product_id.jenis_kayu.name, formatHeaderDetailCenter)
                sheet.write(row, 1, bahan_baku.product_id.name, formatHeaderDetailCenter)
                sheet.write(row, 2, bahan_baku.product_id.tebal, formatHeaderDetailCenter)            
                sheet.write(row, 3, bahan_baku.product_id.lebar, formatHeaderDetailCenter)            
                sheet.write(row, 4, bahan_baku.product_id.panjang, formatHeaderDetailCenter)
                sheet.write(row, 5, bahan_baku.product_id.grade.name, formatHeaderDetailCenter)
                sheet.write(row, 6, bahan_baku.quantity_available, formatHeaderDetailCenter)
                sheet.write(row, 7, bahan_baku.quantity, formatHeaderDetailCenter)
                sheet.write(row, 8, bahan_baku.volume, formatHeaderDetailCenter)
                sheet.write(row, 9, bahan_baku.quantity_needed, formatHeaderDetailCenter)
                sheet.write(row, 10, bahan_baku.volume_needed, formatHeaderDetailCenterNumber)
                sheet.write(row, 11, bahan_baku.quantity_spare, formatHeaderDetailCenterNumber)
                sheet.write(row, 12, bahan_baku.volume_spare, formatHeaderDetailCenterNumber)
                sheet.write(row, 13, (bahan_baku.notes or ''), formatHeaderDetailCenterNumber)
                row += 1    