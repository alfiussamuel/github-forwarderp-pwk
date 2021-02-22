# -*- coding: utf-8 -*-

import datetime
from datetime import datetime
import pytz
from odoo import models


class RpmReportXls(models.AbstractModel):
    _name = 'report.v12_pwk.rpm_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_data(self, data):        
        lines = []
        if data.line_ids:
            for line in data.line_ids:
                vals = {
                    'id': line.id,
                    'partner_id': line.partner_id.name,
                    'po_number': line.po_number,
                    'product_id': line.product_id.name,
                    'glue_id': line.glue_id.name,
                    'grade_id': line.grade_id.name,
                    'tebal': line.thick,
                    'lebar': line.width,
                    'panjang': line.length,
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
        formatHeaderDetailCenter = workbook.add_format({'font_size': 9, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True})
        formatHeaderDetailCenterNumber = workbook.add_format({'font_size': 9, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': '#,##0'})
        formatHeaderDetailCenterNumberFour = workbook.add_format({'font_size': 9, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': '#,##4'})
        formatHeaderDetailLeft = workbook.add_format({'font_size': 9, 'valign':'vcenter', 'align': 'left'})
        formatHeaderDetailRight = workbook.add_format({'font_size': 9, 'valign':'vcenter', 'align': 'right', 'num_format': '#,##0'})
        formatHeaderDetailRightFour = workbook.add_format({'font_size': 9, 'valign':'vcenter', 'align': 'right', 'num_format': '#,##0.0000'})
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
        formatHeaderDetailLeft.set_border(1)

        formatHeaderTable.set_text_wrap()
        formatHeaderTableRight.set_text_wrap()
        formatHeaderDetailCenter.set_text_wrap()
        formatHeaderDetailRight.set_text_wrap()
        formatHeaderDetailLeft.set_text_wrap()
        
        # Set Column Width
        sheet.set_column(0, 0, 3)
        sheet.set_column(1, 1, 10)
        sheet.set_column(2, 2, 15)
        sheet.set_column(3, 3, 38)
        sheet.set_column(4, 4, 10)
        sheet.set_column(5, 5, 10)
        sheet.set_column(6, 6, 4)
        sheet.set_column(7, 7, 4)
        sheet.set_column(8, 8, 4)
        sheet.set_column(9, 9, 10)
        sheet.set_column(10, 10, 10)
        sheet.set_column(11, 11, 7)
        sheet.set_column(12, 12, 7)
        sheet.set_column(13, 13, 7)
        sheet.set_column(14, 14, 5)
        sheet.set_column(15, 15, 5)
        sheet.set_column(16, 16, 12)
        sheet.set_column(17, 17, 10)
        sheet.set_column(18, 18, 20)
        
        # Data 1
        row = 5

        sheet.merge_range(row-3, 0, row-3, 15, 'RENCANA PRODUKSI MINGGUAN', formatHeaderCenter)

        # merge 1 - 4 
        sheet.merge_range(row, 0, row+1, 0, 'No', formatHeaderTable)
        sheet.merge_range(row, 1, row+1, 1, 'No. SO', formatHeaderTable)
        sheet.merge_range(row, 2, row+1, 2, 'Buyer', formatHeaderTable)
        sheet.merge_range(row, 3, row+1, 3, 'Product', formatHeaderTable)
        sheet.merge_range(row, 4, row+1, 4, 'Glue Type', formatHeaderTable)
        sheet.merge_range(row, 5, row+1, 5, 'Grade', formatHeaderTable)
        sheet.merge_range(row, 6, row, 8, 'Size (mm)', formatHeaderTable)
        sheet.merge_range(row, 9, row, 10, 'Order', formatHeaderTable)
        sheet.merge_range(row, 11, row, 13, 'Bahan Baku', formatHeaderTable)
        sheet.merge_range(row, 14, row+1, 15, 'Kebutuhan', formatHeaderTable)
        sheet.merge_range(row, 16, row+1, 16, 'Total BOM', formatHeaderTable)
        sheet.write(row, 17, 'RC', formatHeaderTable)
        sheet.merge_range(row, 18, row+1, 18, 'Spesifikasi Product', formatHeaderTable)

        # Merge 3 and 4
        sheet.write(row+1, 6, 'T', formatHeaderTable)
        sheet.write(row+1, 7, 'L', formatHeaderTable)
        sheet.write(row+1, 8, 'P', formatHeaderTable)
        sheet.write(row+1, 9, 'Pcs', formatHeaderTable)
        sheet.write(row+1, 10, 'M3', formatHeaderTable)
        sheet.merge_range(row+1, 11, row+1, 12, 'BOM', formatHeaderTable)
        sheet.write(row+1, 13, 'Ply', formatHeaderTable)
        sheet.write(row+1, 17, 'Barang Jadi', formatHeaderTable)
        
        row = 7
        number = 1        
        for i in get_data:
            sheet.write(row, 0, number, formatHeaderDetailCenter)
            sheet.write(row, 1, i['po_number'], formatHeaderDetailCenter)
            sheet.write(row, 2, i['partner_id'], formatHeaderDetailCenter)
            sheet.write(row, 3, i['product_id'], formatHeaderDetailCenter)            
            sheet.write(row, 4, i['glue_id'], formatHeaderDetailCenter)            
            sheet.write(row, 5, i['grade_id'], formatHeaderDetailCenter)
            sheet.write(row, 6, i['tebal'], formatHeaderDetailCenter)
            sheet.write(row, 7, i['lebar'], formatHeaderDetailCenter)
            sheet.write(row, 8, i['panjang'], formatHeaderDetailCenter)

            rpm_line_obj = self.env['pwk.rpm.line'].browse(i['id'])
            if rpm_line_obj:
                if rpm_line_obj.is_selected_detail1 and rpm_line_obj.detail_ids_1:
                    for bom_line in rpm_line_obj.detail_ids_1:
                        sheet.write(row, 11, bom_line.product_id.grade_id.name, formatHeaderDetailCenter)
                        sheet.write(row, 12, bom_line.product_id.tebal, formatHeaderDetailCenter)
                        sheet.write(row, 13, bom_line.ply, formatHeaderDetailCenter)
                        row += 1
            else:
                row += 1

            number += 1