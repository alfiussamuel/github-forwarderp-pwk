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
        sheet.set_column(0, 0, 3)
        sheet.set_column(1, 1, 5)
        sheet.set_column(2, 2, 8)
        sheet.set_column(3, 3, 10)
        sheet.set_column(4, 4, 7)
        sheet.set_column(5, 5, 10)
        sheet.set_column(6, 6, 7)
        sheet.set_column(7, 7, 6)
        sheet.set_column(8, 8, 6)
        sheet.set_column(9, 9, 6)
        sheet.set_column(10, 10, 8)
        sheet.set_column(11, 11, 8)
        sheet.set_column(12, 12, 12)
        sheet.set_column(13, 13, 8)
        sheet.set_column(14, 14, 8)
        sheet.set_column(15, 15, 5)
        sheet.set_column(16, 16, 5)
        sheet.set_column(17, 17, 10)
        sheet.set_column(18, 18, 10)
        sheet.set_column(19, 19, 45)

        # Set default Row height
        sheet.set_default_row(21)
        
        # Data 1
        row = 5

        sheet.merge_range(row-3, 0, row-2, 18, 'RENCANA PRODUKSI MINGGUAN', formatHeaderCenter)

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
        sheet.merge_range(row, 12, row, 14, 'Bahan Baku', formatHeaderTable)
        sheet.merge_range(row, 15, row+1, 16, 'Kebutuhan', formatHeaderTable)
        sheet.merge_range(row, 17, row+1, 17, 'Total BOM', formatHeaderTable)
        sheet.write(row, 18, 'RC', formatHeaderTable)
        sheet.merge_range(row, 19, row+1, 19, 'Spesifikasi Product', formatHeaderTable)

        # Merge 3 and 4
        sheet.write(row+1, 7, 'T', formatHeaderTable)
        sheet.write(row+1, 8, 'L', formatHeaderTable)
        sheet.write(row+1, 9, 'P', formatHeaderTable)
        sheet.write(row+1, 10, 'Pcs', formatHeaderTable)
        sheet.write(row+1, 11, 'M3', formatHeaderTable)
        sheet.merge_range(row+1, 12, row+1, 13, 'BOM', formatHeaderTable)
        sheet.write(row+1, 14, 'Ply', formatHeaderTable)
        sheet.write(row+1, 18, 'Barang Jadi', formatHeaderTable)
        
        row = 7
        number = 1        
        
        if lines.container_ids:
            for container in lines.container_ids:
                merge_range = 0

                for container_line in container.line_ids:
                    merge_range += container_line.rpm_line_id.total_bom

                # Group by Container
                sheet.merge_range(row, 0, row + merge_range - 1, 0, number, formatHeaderDetailCenter)
                sheet.merge_range(row, 1, row + merge_range - 1, 1, '1', formatHeaderDetailCenter)

                # Details each Container
                for container_line in container.line_ids:
                    rpm_line = container_line.rpm_line_id
                    merge_range_bom = int(rpm_line.total_bom - 1)

                    # Get Goods Type
                    goods_type = ''
                    if rpm_line.product_id.goods_type == "Blockboard":
                        goods_type = 'BB'
                    elif rpm_line.product_id.goods_type == "Plywood":
                        goods_type = 'PW'
                    elif rpm_line.product_id.goods_type == "LVL":
                        goods_type = 'LVL'

                    sheet.merge_range(row, 2, row + merge_range_bom, 2, rpm_line.po_number, formatHeaderDetailCenter)
                    sheet.merge_range(row, 3, row + merge_range_bom, 3, rpm_line.partner_id.name, formatHeaderDetailCenter)
                    sheet.merge_range(row, 4, row + merge_range_bom, 4, goods_type, formatHeaderDetailCenter)            
                    sheet.merge_range(row, 5, row + merge_range_bom, 5, rpm_line.product_id.glue.name, formatHeaderDetailCenter)            
                    sheet.merge_range(row, 6, row + merge_range_bom, 6, rpm_line.product_id.grade.name, formatHeaderDetailCenter)
                    sheet.merge_range(row, 7, row + merge_range_bom, 7, rpm_line.product_id.tebal, formatHeaderDetailCenter)
                    sheet.merge_range(row, 8, row + merge_range_bom, 8, rpm_line.product_id.lebar, formatHeaderDetailCenter)
                    sheet.merge_range(row, 9, row + merge_range_bom, 9, rpm_line.product_id.panjang, formatHeaderDetailCenter)
                    sheet.merge_range(row, 10, row + merge_range_bom, 10, rpm_line.total_qty, formatHeaderDetailCenter)
                    sheet.merge_range(row, 11, row + merge_range_bom, 11, rpm_line.total_volume, formatHeaderDetailCenter)
                    sheet.merge_range(row, 17, row + merge_range_bom, 17, rpm_line.total_tebal, formatHeaderDetailCenter)
                    sheet.merge_range(row, 18, row + merge_range_bom, 18, rpm_line.percent_tebal, formatHeaderDetailCenter)
                    sheet.merge_range(row, 19, row + merge_range_bom, 19, (rpm_line.notes or ''), formatHeaderDetailLeft)

                    detail_ids = ''
                    if rpm_line.is_selected_detail1 and rpm_line.detail_ids_1:
                        detail_ids = rpm_line.detail_ids_1
                    elif rpm_line.is_selected_detail2 and rpm_line.detail_ids_2:
                        detail_ids = rpm_line.detail_ids_2
                    elif rpm_line.is_selected_detail3 and rpm_line.detail_ids_3:
                        detail_ids = rpm_line.detail_ids_3
                    elif rpm_line.is_selected_detail4 and rpm_line.detail_ids_4:
                        detail_ids = rpm_line.detail_ids_4
                    elif rpm_line.is_selected_detail5 and rpm_line.detail_ids_5:
                        detail_ids = rpm_line.detail_ids_5

                    if detail_ids:
                        for bom_line in detail_ids:
                            bom_label = ''
                            if bom_line.product_id.goods_type == 'Faceback':
                                bom_label = 'F/B ' + (bom_line.product_id.jenis_kayu.code or '')
                            elif bom_line.product_id.goods_type == 'Barecore':
                                bom_label = 'BC ' + bom_line.product_id.grade.name
                            else:
                                bom_label = bom_line.product_id.grade.name + ' ' + (bom_line.product_id.jenis_kayu.code or '')

                            if bom_line.product_id.goods_type == 'Faceback':
                                formatHeaderDetailCenterColor = workbook.add_format({'font_size': 9, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'bg_color':bom_line.product_id.jenis_kayu.color})
                                sheet.write(row, 12, bom_label, formatHeaderDetailCenterColor)
                            else:
                                sheet.write(row, 12, bom_label, formatHeaderDetailCenter)
                            sheet.write(row, 13, bom_line.product_id.tebal, formatHeaderDetailCenter)
                            sheet.write(row, 14, bom_line.ply, formatHeaderDetailCenter)
                            sheet.write(row, 15, bom_line.quantity, formatHeaderDetailCenter)
                            sheet.write(row, 16, bom_line.product_id.uom_id.name, formatHeaderDetailCenter)
                            row += 1

                number += 1

        row += 1
        sheet.write(row, 3, 'Hari Kerja', formatHeaderDetailLeft)
        sheet.write(row + 1, 3, 'Total Produksi', formatHeaderDetailLeft)
        sheet.write(row + 2, 3, 'Blockboard', formatHeaderDetailLeft)
        sheet.write(row + 3, 3, 'Plywood', formatHeaderDetailLeft)
        sheet.write(row + 4, 3, 'LVL', formatHeaderDetailLeft)
        sheet.write(row + 5, 3, 'Target / Hari', formatHeaderDetailLeft)

        sheet.write(row, 4, ':', formatHeaderDetailCenter)
        sheet.write(row + 1, 4, ':', formatHeaderDetailCenter)
        sheet.write(row + 2, 4, ':', formatHeaderDetailCenter)
        sheet.write(row + 3, 4, ':', formatHeaderDetailCenter)
        sheet.write(row + 4, 4, ':', formatHeaderDetailCenter)
        sheet.write(row + 5, 4, ':', formatHeaderDetailCenter)

        sheet.write(row, 5, lines.working_days, formatHeaderDetailCenter)
        sheet.write(row + 1, 5, lines.total_produksi, formatHeaderDetailCenter)
        sheet.write(row + 2, 5, lines.total_blockboard, formatHeaderDetailCenter)
        sheet.write(row + 3, 5, lines.total_plywood, formatHeaderDetailCenter)
        sheet.write(row + 4, 5, lines.total_lvl, formatHeaderDetailCenter)
        sheet.write(row + 5, 5, lines.target_per_hari, formatHeaderDetailCenter)

        sheet.write(row + 2, 6, lines.total_blockboard_percent, formatHeaderDetailCenter)
        sheet.write(row + 3, 6, lines.total_plywood_percent, formatHeaderDetailCenter)
        sheet.write(row + 4, 6, lines.total_lvl_percent, formatHeaderDetailCenter)