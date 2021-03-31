# -*- coding: utf-8 -*-

import datetime
from datetime import datetime
import pytz
from odoo import models


class RpbReportXls(models.AbstractModel):
    _name = 'report.v12_pwk.rpb_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_data(self, data):        
        lines = []
        if data.line_ids:
            for line in data.line_ids:
                vals = {
                    'partner': line.sale_line_id.order_id.partner_id.name,
                    'goods_type': line.product_id.goods_type,
                    'jenis_kayu': line.product_id.jenis_kayu.name,
                    'order': line.sale_line_id.order_id.po_number,
                    'tebal': line.thick,
                    'lebar': line.width,
                    'panjang': line.length,
                    'glue': line.glue_id.name,
                    'grade': line.grade_id.name,
                    'container': line.container_id.name,
                    'container_qty': line.container_qty,
                    'container_vol': line.container_vol,                    
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
        formatHeaderRight = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'right', 'num_format': '#,##0', 'bold': True, 'bg_color':'#4ead2f', 'color':'white'})
        formatHeaderRightFour = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'right', 'num_format': '#,##0', 'bold': True, 'bg_color':'#4ead2f', 'color':'white', 'num_format': '#,##4'})
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
        
        formatHeaderRight.set_border(1)
        formatHeaderRightFour.set_border(1)
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
        sheet.set_column(1, 1, 22)
        sheet.set_column(2, 2, 10)
        sheet.set_column(3, 3, 8)
        sheet.set_column(4, 4, 10)
        sheet.set_column(5, 5, 4)
        sheet.set_column(6, 6, 1)
        sheet.set_column(7, 7, 4)
        sheet.set_column(8, 8, 1)
        sheet.set_column(9, 9, 4)
        sheet.set_column(10, 10, 10)
        sheet.set_column(11, 11, 7)
        sheet.set_column(12, 12, 7)
        sheet.set_column(13, 13, 8)
        sheet.set_column(14, 14, 8)
        sheet.set_column(15, 15, 8)
        sheet.set_column(16, 16, 8)

        # Data 1
        row = 5

        sheet.merge_range(row-3, 0, row-3, 15, 'RENCANA PRODUKSI (' + lines.name + ')', formatHeaderCenter)
        sheet.merge_range(row-2, 0, row-2, 15, 'TARGET : ' + str(lines.target) + ' M3', formatHeaderCenterNumber)

        # merge 1 - 4 
        sheet.merge_range(row, 0, row+1, 0, 'No', formatHeaderTable)
        sheet.merge_range(row, 1, row+1, 1, 'Buyer', formatHeaderTable)
        sheet.merge_range(row, 2, row+1, 2, 'Product', formatHeaderTable)
        sheet.merge_range(row, 3, row+1, 3, 'F/B', formatHeaderTable)
        sheet.merge_range(row, 4, row+1, 4, 'PO No.', formatHeaderTable)
        sheet.merge_range(row, 5, row, 9, 'Size (mm)', formatHeaderTable)
        sheet.merge_range(row, 10, row+1, 10, 'Glue Type', formatHeaderTable)
        sheet.merge_range(row, 11, row+1, 11, 'Grade', formatHeaderTable)
        sheet.merge_range(row, 12, row+1, 12, 'CONT', formatHeaderTable)
        sheet.merge_range(row, 13, row, 14, 'Isi Per Cont (m3)', formatHeaderTable)
        sheet.merge_range(row, 15, row, 16, 'Total Volume (m3)', formatHeaderTable)

        # Merge 3 and 4
        sheet.write(row+1, 5, 'T', formatHeaderTable)
        sheet.write(row+1, 6, '', formatHeaderTable)
        sheet.write(row+1, 7, 'L', formatHeaderTable)
        sheet.write(row+1, 8, '', formatHeaderTable)
        sheet.write(row+1, 9, 'P', formatHeaderTable)
        sheet.write(row+1, 13, 'Pcs', formatHeaderTable)
        sheet.write(row+1, 14, 'M3', formatHeaderTable)
        sheet.write(row+1, 15, 'PCS', formatHeaderTable)
        sheet.write(row+1, 16, 'M3', formatHeaderTable)        

        row = 7
        number = 1
        merge_range = 1
        previous_container = 1
        grand_total_container_qty = 0
        grand_total_container_vol = 0

        for goods in lines.group_ids:
            total_container_qty = 0
            total_container_vol = 0

            for container in goods.line_ids:
                total = 0

                for i in get_data:
                    if i['container'] == container['container']:
                        sheet.write(row, 0, number, formatHeaderDetailCenter)
                        sheet.write(row, 1, i['partner'], formatHeaderDetailCenter)
                        sheet.write(row, 2, i['goods_type'], formatHeaderDetailCenter)
                        sheet.write(row, 3, i['jenis_kayu'], formatHeaderDetailCenter)            
                        sheet.write(row, 4, i['order'], formatHeaderDetailCenter)            
                        sheet.write(row, 5, i['tebal'], formatHeaderDetailCenter)
                        sheet.write(row, 6, '', formatHeaderDetailCenter)
                        sheet.write(row, 7, i['lebar'], formatHeaderDetailCenter)
                        sheet.write(row, 8, '', formatHeaderDetailCenter)
                        sheet.write(row, 9, i['panjang'], formatHeaderDetailCenter)
                        sheet.write(row, 10, i['glue'], formatHeaderDetailCenter)
                        sheet.write(row, 11, i['grade'], formatHeaderDetailCenter)
                        
                        sheet.write(row, 13, i['container_qty'], formatHeaderDetailRight)
                        sheet.write(row, 14, i['container_vol'], formatHeaderDetailRightFour)
                        sheet.write(row, 15, i['container_qty'], formatHeaderDetailRight)
                        sheet.write(row, 16, i['container_vol'], formatHeaderDetailRightFour)

                        total += 1
                        row += 1
                        number += 1
                        total_container_qty += i['container_qty']
                        total_container_vol += i['container_vol']
                        grand_total_container_qty += i['container_qty']
                        grand_total_container_vol += i['container_vol']

                if total == 1:
                    sheet.write(row - 1, 12, 1, formatHeaderDetailCenterNumber)
                elif total > 1:
                    sheet.merge_range(row - total, 12, row - 1, 12, 1, formatHeaderDetailCenterNumber)

            sheet.merge_range(row, 0, row, 12, "TOTAL " + goods.goods_type , formatHeaderRight)
            sheet.write(row, 13, total_container_qty, formatHeaderRight)
            sheet.write(row, 14, total_container_vol, formatHeaderRightFour)
            sheet.write(row, 15, total_container_qty, formatHeaderRight)
            sheet.write(row, 16, total_container_vol, formatHeaderRightFour)
            row += 1

        sheet.merge_range(row, 0, row, 12, "GRAND TOTAL" , formatHeaderRight)
        sheet.write(row, 13, grand_total_container_qty, formatHeaderRight)
        sheet.write(row, 14, grand_total_container_vol, formatHeaderRightFour)
        sheet.write(row, 15, grand_total_container_qty, formatHeaderRight)
        sheet.write(row, 16, grand_total_container_vol, formatHeaderRightFour)