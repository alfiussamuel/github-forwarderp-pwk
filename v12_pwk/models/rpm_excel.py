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

        formatHeaderDetailLeft.set_margins(3)
        
        # Set Column Width
        sheet.set_column(0, 0, 3)
        sheet.set_column(1, 1, 10)
        sheet.set_column(2, 2, 18)
        sheet.set_column(3, 3, 15)
        sheet.set_column(4, 4, 10)
        sheet.set_column(5, 5, 10)
        sheet.set_column(6, 6, 4)
        sheet.set_column(7, 7, 4)
        sheet.set_column(8, 8, 4)
        sheet.set_column(9, 9, 8)
        sheet.set_column(10, 10, 8)
        sheet.set_column(11, 11, 8)
        sheet.set_column(12, 12, 8)
        sheet.set_column(13, 13, 8)
        sheet.set_column(14, 14, 5)
        sheet.set_column(15, 15, 5)
        sheet.set_column(16, 16, 12)
        sheet.set_column(17, 17, 10)
        sheet.set_column(18, 18, 35)
        
        # Data 1
        row = 5

        sheet.merge_range(row-3, 0, row-2, 18, 'RENCANA PRODUKSI MINGGUAN', formatHeaderCenter)

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
            rpm_line_obj = self.env['pwk.rpm.line'].browse(i['id'])
            total_bom = rpm_line_obj.total_bom
            total_tebal = rpm_line_obj.total_tebal
            merge_range = total_bom - 1

            sheet.merge_range(row, 0, row + merge_range, 0, number, formatHeaderDetailCenter)
            sheet.merge_range(row, 1, row + merge_range, 1, i['po_number'], formatHeaderDetailCenter)
            sheet.merge_range(row, 2, row + merge_range, 2, i['partner_id'], formatHeaderDetailCenter)
            sheet.merge_range(row, 3, row + merge_range, 3, i['product_id'], formatHeaderDetailCenter)            
            sheet.merge_range(row, 4, row + merge_range, 4, i['glue_id'], formatHeaderDetailCenter)            
            sheet.merge_range(row, 5, row + merge_range, 5, i['grade_id'], formatHeaderDetailCenter)
            sheet.merge_range(row, 6, row + merge_range, 6, i['tebal'], formatHeaderDetailCenter)
            sheet.merge_range(row, 7, row + merge_range, 7, i['lebar'], formatHeaderDetailCenter)
            sheet.merge_range(row, 8, row + merge_range, 8, i['panjang'], formatHeaderDetailCenter)
            sheet.merge_range(row, 9, row + merge_range, 9, i['total_qty'], formatHeaderDetailCenter)
            sheet.merge_range(row, 10, row + merge_range, 10, i['total_volume'], formatHeaderDetailCenter)
            sheet.merge_range(row, 16, row + merge_range, 16, rpm_line_obj.total_tebal, formatHeaderDetailCenter)
            sheet.merge_range(row, 17, row + merge_range, 17, rpm_line_obj.percent_tebal, formatHeaderDetailCenter)
            sheet.merge_range(row, 18, row + merge_range, 18, rpm_line_obj.notes, formatHeaderDetailLeft)

            if rpm_line_obj:
                if rpm_line_obj.is_selected_detail1 and rpm_line_obj.detail_ids_1:
                    detail_ids = rpm_line_obj.detail_ids_1
                elif rpm_line_obj.is_selected_detail2 and rpm_line_obj.detail_ids_2:
                    detail_ids = rpm_line_obj.detail_ids_2
                elif rpm_line_obj.is_selected_detail3 and rpm_line_obj.detail_ids_3:
                    detail_ids = rpm_line_obj.detail_ids_3
                elif rpm_line_obj.is_selected_detail4 and rpm_line_obj.detail_ids_4:
                    detail_ids = rpm_line_obj.detail_ids_4
                elif rpm_line_obj.is_selected_detail5 and rpm_line_obj.detail_ids_5:
                    detail_ids = rpm_line_obj.detail_ids_5

                if detail_ids:
                    for bom_line in detail_ids:
                        bom_label = ''
                        if bom_line.product_id.goods_type == 'Faceback':
                            bom_label = 'F/B ' + bom_line.product_id.jenis_kayu.name
                        elif bom_line.product_id.goods_type == 'Barecore':
                            bom_label = 'BC ' + bom_line.product_id.grade.name
                        else:
                            bom_label = bom_line.product_id.grade.name

                        sheet.write(row, 11, bom_label, formatHeaderDetailCenter)
                        sheet.write(row, 12, bom_line.product_id.tebal, formatHeaderDetailCenter)
                        sheet.write(row, 13, bom_line.ply, formatHeaderDetailCenter)
                        sheet.write(row, 14, bom_line.quantity, formatHeaderDetailCenter)
                        sheet.write(row, 15, bom_line.product_id.uom_id.name, formatHeaderDetailCenter)
                        row += 1
            else:
                row += 1

            number += 1