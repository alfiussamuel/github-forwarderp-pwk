# -*- coding: utf-8 -*-

import datetime
from datetime import datetime, timedelta
import pytz
from odoo import models


class RpmMonitoringReportXls(models.AbstractModel):
    _name = 'report.v12_pwk.rpm_monitoring_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_data(self, data):        
        lines = []
        if data.line_ids:
            for line in data.line_ids:
                vals = {
                    'id': line.id,
                    'partner_id': line.partner_id.name,
                    'po_number': line.po_number,
                    'product_id': line.product_id.goods_type,
                    'glue_id': line.glue_id.name,
                    'grade_id': line.product_id.grade.name,
                    'tebal': line.thick,
                    'lebar': line.width,
                    'panjang': line.length,
                    'total_qty': line.total_qty,
                    'total_volume': line.total_volume
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
        sheet.set_column(0, 0, 4)
        sheet.set_column(1, 1, 5)
        sheet.set_column(2, 2, 8)
        sheet.set_column(3, 3, 25)
        sheet.set_column(4, 4, 8)
        sheet.set_column(5, 5, 10)
        sheet.set_column(6, 6, 7)
        sheet.set_column(7, 7, 6)
        sheet.set_column(8, 8, 6)
        sheet.set_column(9, 9, 6)
        sheet.set_column(10, 10, 8)
        sheet.set_column(11, 11, 8)
        sheet.set_column(12, 12, 10)
        sheet.set_column(13, 13, 10)
        sheet.set_column(14, 14, 10)
        sheet.set_column(15, 15, 10)
        sheet.set_column(16, 16, 10)
        sheet.set_column(17, 17, 10)
        sheet.set_column(18, 18, 10)
        sheet.set_column(19, 19, 10)

        # Set default Row height
        sheet.set_default_row(40)
        sheet.set_row(4, 16)
        
        # Data 1
        row = 3

        sheet.merge_range(row-2, 0, row-2, 18, 'RENCANA PRODUKSI MINGGUAN', formatHeaderCenter)

        # merge 1 - 4 
        sheet.merge_range(row, 0, row+1, 0, 'No', formatHeaderTable)
        sheet.merge_range(row, 1, row+1, 1, 'Cont', formatHeaderTable)
        sheet.merge_range(row, 2, row+1, 2, 'No. SO', formatHeaderTable)
        sheet.merge_range(row, 3, row+1, 3, 'Buyer', formatHeaderTable)
        sheet.merge_range(row, 4, row+1, 4, 'Product', formatHeaderTable)
        sheet.merge_range(row, 5, row+1, 5, 'Glue Type', formatHeaderTable)
        sheet.merge_range(row, 6, row+1, 6, 'Grade', formatHeaderTable)
        sheet.merge_range(row, 7, row, 9, 'Size (mm)', formatHeaderTable)
        sheet.merge_range(row, 10, row, 11, 'Order', formatHeaderTable)
        sheet.merge_range(row, 12, row, 17, 'TANGGAL (P1) & PCS', formatHeaderTable)
        sheet.merge_range(row, 18, row+1, 18, 'Jumlah', formatHeaderTable)

        # Merge 3 and 4
        sheet.write(row+1, 7, 'T', formatHeaderTable)
        sheet.write(row+1, 8, 'L', formatHeaderTable)
        sheet.write(row+1, 9, 'P', formatHeaderTable)
        sheet.write(row+1, 10, 'Pcs', formatHeaderTable)
        sheet.write(row+1, 11, 'M3', formatHeaderTable)    
        
        date_start = lines.date_start
        column = 12

        while date_start <= lines.date_end:
            sheet.write(row+1, column, date_start.day, formatHeaderTable)
            date_start = date_start + timedelta(days = 1)
            column += 1

        row = 5
        number = 1        
        
        if lines.container_ids:
            for container in lines.container_ids:
                merge_range = 0

                for container_line in container.line_ids:
                    merge_range += 1

                # Group by Container
                if merge_range > 1:
                    sheet.merge_range(row, 0, row + merge_range - 1, 0, number, formatHeaderDetailCenter)
                    sheet.merge_range(row, 1, row + merge_range - 1, 1, '1', formatHeaderDetailCenter)
                elif merge_range == 1:
                    sheet.write(row, 0, number, formatHeaderDetailCenter)
                    sheet.write(row, 1, '1', formatHeaderDetailCenter)

                # Details each Container
                for container_line in container.line_ids:
                    rpm_line = container_line.rpm_line_id

                    # Get Goods Type
                    goods_type = ''
                    if rpm_line.product_id.goods_type == "Blockboard":
                        goods_type = 'BB'
                    elif rpm_line.product_id.goods_type == "Plywood":
                        goods_type = 'PW'
                    elif rpm_line.product_id.goods_type == "LVL":
                        goods_type = 'LVL'

                    formula = '=' + 'M' + str(row+1) + ' + N' + str(row+1) + ' + O' + str(row+1) + ' + P' + str(row+1) + ' + Q' + str(row+1) + ' + R' + str(row+1)
                    sheet.write(row, 2, rpm_line.po_number, formatHeaderDetailCenter)
                    sheet.write(row, 3, rpm_line.partner_id.name, formatHeaderDetailCenter)
                    sheet.write(row, 4, goods_type, formatHeaderDetailCenter)            
                    sheet.write(row, 5, rpm_line.product_id.glue.name, formatHeaderDetailCenter)            
                    sheet.write(row, 6, rpm_line.product_id.grade.name, formatHeaderDetailCenter)
                    sheet.write(row, 7, rpm_line.product_id.tebal, formatHeaderDetailCenter)
                    sheet.write(row, 8, rpm_line.product_id.lebar, formatHeaderDetailCenter)
                    sheet.write(row, 9, rpm_line.product_id.panjang, formatHeaderDetailCenter)
                    sheet.write(row, 10, rpm_line.total_qty, formatHeaderDetailCenter)
                    sheet.write(row, 11, rpm_line.total_volume, formatHeaderDetailCenter)
                    sheet.write(row, 12, rpm_line.quantity_date1, formatHeaderDetailCenterNumber)
                    sheet.write(row, 13, rpm_line.quantity_date2, formatHeaderDetailCenterNumber)
                    sheet.write(row, 14, rpm_line.quantity_date3, formatHeaderDetailCenterNumber)
                    sheet.write(row, 15, rpm_line.quantity_date4, formatHeaderDetailCenterNumber)
                    sheet.write(row, 16, rpm_line.quantity_date5, formatHeaderDetailCenterNumber)
                    sheet.write(row, 17, rpm_line.quantity_date6, formatHeaderDetailCenterNumber)
                    sheet.write_formula(row, 18, formula, formatHeaderDetailCenterNumber)
                    row += 1

                number += 1