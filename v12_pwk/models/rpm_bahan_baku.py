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
        formatHeaderDetailCenterNumberOne = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True, 'num_format': '#,##0.0'})

        formatHeaderDetailLeft = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left', 'text_wrap': True})
        
        formatHeaderDetailRight = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'right', 'num_format': '#,##0'})
        formatHeaderDetailRightFour = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'right', 'num_format': '#,##0.0000'})
        formatHeaderDetailRightOne = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'right', 'num_format': '#,##0.0'})
        formatHeaderDetailRightBold = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'right', 'num_format': '#,##0', 'bold': True})
        formatHeaderDetailRightFourBold = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'right', 'num_format': '#,##0.0000', 'bold': True})

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
        formatHeaderDetailCenterNumberOne.set_border(1)
        formatHeaderDetailRight.set_border(1)
        formatHeaderDetailRightFour.set_border(1)
        formatHeaderDetailRightBold.set_border(1)
        formatHeaderDetailRightFourBold.set_border(1)

        formatHeaderTable.set_text_wrap()
        formatHeaderTableRight.set_text_wrap()
        formatHeaderDetailCenter.set_text_wrap()
        formatHeaderDetailRight.set_text_wrap()
        # formatHeaderDetailLeft.set_text_wrap()
        
        # Set Column Width
        sheet.set_column(0, 0, 10)
        sheet.set_column(1, 1, 10)
        sheet.set_column(2, 2, 6)
        sheet.set_column(3, 3, 6)
        sheet.set_column(4, 4, 6)
        sheet.set_column(5, 5, 10)
        sheet.set_column(6, 6, 12)
        sheet.set_column(7, 7, 14)
        sheet.set_column(8, 8, 14)
        sheet.set_column(9, 9, 14)
        sheet.set_column(10, 10, 14)
        sheet.set_column(11, 11, 14)
        sheet.set_column(12, 12, 14)
        sheet.set_column(13, 13, 50)
        
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
            veneer_ids = self.env['pwk.rpm.bahan.baku'].search([
                ('reference', '=', lines.id),
                ('goods_type', '=', 'Veneer')
            ])

            faceback_ids = self.env['pwk.rpm.bahan.baku'].search([
                ('reference', '=', lines.id),
                ('goods_type', '=', 'Faceback')
            ])

            mdf_ids = self.env['pwk.rpm.bahan.baku'].search([
                ('reference', '=', lines.id),
                ('goods_type', '=', 'MDF')
            ])

            barecore_ids = self.env['pwk.rpm.bahan.baku'].search([
                ('reference', '=', lines.id),
                ('goods_type', '=', 'Barecore')
            ])

            total_qty_stock_veneer = total_qty_veneer = total_volume_veneer = total_qty_needed_veneer = total_volume_needed_veneer = total_qty_spare_veneer = total_volume_spare_veneer = 0 
            total_qty_stock_faceback = total_qty_faceback = total_volume_faceback = total_qty_needed_faceback = total_volume_needed_faceback = total_qty_spare_faceback = total_volume_spare_faceback = 0 
            total_qty_stock_mdf = total_qty_mdf = total_volume_mdf = total_qty_needed_mdf = total_volume_needed_mdf = total_qty_spare_mdf = total_volume_spare_mdf = 0  
            total_qty_stock_barecore = total_qty_barecore = total_volume_barecore = total_qty_needed_barecore = total_volume_needed_barecore = total_qty_spare_barecore = total_volume_spare_barecore = 0

            if veneer_ids:
                for bahan_baku in veneer_ids:
                    sheet.write(row, 0, bahan_baku.product_id.jenis_kayu.name, formatHeaderDetailCenter)
                    sheet.write(row, 1, bahan_baku.product_id.goods_type, formatHeaderDetailCenter)
                    sheet.write(row, 2, bahan_baku.product_id.tebal, formatHeaderDetailCenterNumberOne)            
                    sheet.write(row, 3, bahan_baku.product_id.lebar, formatHeaderDetailCenter)            
                    sheet.write(row, 4, bahan_baku.product_id.panjang, formatHeaderDetailCenter)
                    sheet.write(row, 5, bahan_baku.product_id.grade.name, formatHeaderDetailCenter)
                    sheet.write(row, 6, bahan_baku.quantity_available, formatHeaderDetailRight)
                    sheet.write(row, 7, bahan_baku.quantity, formatHeaderDetailRight)
                    sheet.write(row, 8, bahan_baku.volume, formatHeaderDetailRightFour)
                    sheet.write(row, 9, bahan_baku.quantity_needed, formatHeaderDetailRight)
                    sheet.write(row, 10, bahan_baku.volume_needed, formatHeaderDetailRightFour)
                    sheet.write(row, 11, bahan_baku.quantity_spare, formatHeaderDetailRight)
                    sheet.write(row, 12, bahan_baku.volume_spare, formatHeaderDetailRightFour)
                    sheet.write(row, 13, (bahan_baku.notes or ''), formatHeaderDetailLeft)
                    row += 1

                    total_qty_stock_veneer += bahan_baku.quantity_available
                    total_qty_veneer += bahan_baku.quantity
                    total_volume_veneer += bahan_baku.volume
                    total_qty_needed_veneer += bahan_baku.quantity_needed
                    total_volume_needed_veneer += bahan_baku.volume_needed
                    total_qty_spare_veneer += bahan_baku.quantity_spare
                    total_volume_spare_veneer += bahan_baku.volume_spare

                sheet.merge_range(row, 0, row, 5, 'TOTAL ', formatHeaderDetailRightBold)
                sheet.write(row, 6, total_qty_stock_veneer, formatHeaderDetailRightBold)
                sheet.write(row, 7, total_qty_veneer, formatHeaderDetailRightBold)
                sheet.write(row, 8, total_volume_veneer, formatHeaderDetailRightFourBold)
                sheet.write(row, 9, total_qty_needed_veneer, formatHeaderDetailRightBold)
                sheet.write(row, 10, total_volume_needed_veneer, formatHeaderDetailRightFourBold)
                sheet.write(row, 11, total_qty_spare_veneer, formatHeaderDetailRightBold)
                sheet.write(row, 12, total_volume_spare_veneer, formatHeaderDetailRightFourBold)
                sheet.write(row, 13, '', formatHeaderDetailRightFourBold)

            if faceback_ids:
                row += 1
                for bahan_baku in faceback_ids:
                    sheet.write(row, 0, bahan_baku.product_id.jenis_kayu.name, formatHeaderDetailCenter)
                    sheet.write(row, 1, bahan_baku.product_id.goods_type, formatHeaderDetailCenter)
                    sheet.write(row, 2, bahan_baku.product_id.tebal, formatHeaderDetailCenterNumberOne)            
                    sheet.write(row, 3, bahan_baku.product_id.lebar, formatHeaderDetailCenter)            
                    sheet.write(row, 4, bahan_baku.product_id.panjang, formatHeaderDetailCenter)
                    sheet.write(row, 5, bahan_baku.product_id.grade.name, formatHeaderDetailCenter)
                    sheet.write(row, 6, bahan_baku.quantity_available, formatHeaderDetailRight)
                    sheet.write(row, 7, bahan_baku.quantity, formatHeaderDetailRight)
                    sheet.write(row, 8, bahan_baku.volume, formatHeaderDetailRightFour)
                    sheet.write(row, 9, bahan_baku.quantity_needed, formatHeaderDetailRight)
                    sheet.write(row, 10, bahan_baku.volume_needed, formatHeaderDetailRightFour)
                    sheet.write(row, 11, bahan_baku.quantity_spare, formatHeaderDetailRight)
                    sheet.write(row, 12, bahan_baku.volume_spare, formatHeaderDetailRightFour)
                    sheet.write(row, 13, (bahan_baku.notes or ''), formatHeaderDetailLeft)
                    row += 1  

                    total_qty_stock_faceback += bahan_baku.quantity_available
                    total_qty_faceback += bahan_baku.quantity
                    total_volume_faceback += bahan_baku.volume
                    total_qty_needed_faceback += bahan_baku.quantity_needed
                    total_volume_needed_faceback += bahan_baku.volume_needed
                    total_qty_spare_faceback += bahan_baku.quantity_spare
                    total_volume_spare_faceback += bahan_baku.volume_spare

                sheet.merge_range(row, 0, row, 5, 'TOTAL ', formatHeaderDetailRightBold)
                sheet.write(row, 6, total_qty_stock_faceback, formatHeaderDetailRightBold)
                sheet.write(row, 7, total_qty_faceback, formatHeaderDetailRightBold)
                sheet.write(row, 8, total_volume_faceback, formatHeaderDetailRightFourBold)
                sheet.write(row, 9, total_qty_needed_faceback, formatHeaderDetailRightBold)
                sheet.write(row, 10, total_volume_needed_faceback, formatHeaderDetailRightFourBold)
                sheet.write(row, 11, total_qty_spare_faceback, formatHeaderDetailRightBold)
                sheet.write(row, 12, total_volume_spare_faceback, formatHeaderDetailRightFourBold)
                sheet.write(row, 13, '', formatHeaderDetailRightFourBold)

            if mdf_ids:
                row += 1
                for bahan_baku in mdf_ids:
                    sheet.write(row, 0, bahan_baku.product_id.jenis_kayu.name, formatHeaderDetailCenter)
                    sheet.write(row, 1, bahan_baku.product_id.goods_type, formatHeaderDetailCenter)
                    sheet.write(row, 2, bahan_baku.product_id.tebal, formatHeaderDetailCenterNumberOne)            
                    sheet.write(row, 3, bahan_baku.product_id.lebar, formatHeaderDetailCenter)            
                    sheet.write(row, 4, bahan_baku.product_id.panjang, formatHeaderDetailCenter)
                    sheet.write(row, 5, bahan_baku.product_id.grade.name, formatHeaderDetailCenter)
                    sheet.write(row, 6, bahan_baku.quantity_available, formatHeaderDetailRight)
                    sheet.write(row, 7, bahan_baku.quantity, formatHeaderDetailRight)
                    sheet.write(row, 8, bahan_baku.volume, formatHeaderDetailRightFour)
                    sheet.write(row, 9, bahan_baku.quantity_needed, formatHeaderDetailRight)
                    sheet.write(row, 10, bahan_baku.volume_needed, formatHeaderDetailRightFour)
                    sheet.write(row, 11, bahan_baku.quantity_spare, formatHeaderDetailRight)
                    sheet.write(row, 12, bahan_baku.volume_spare, formatHeaderDetailRightFour)
                    sheet.write(row, 13, (bahan_baku.notes or ''), formatHeaderDetailLeft)
                    row += 1  

                    total_qty_stock_mdf += bahan_baku.quantity_available
                    total_qty_mdf += bahan_baku.quantity
                    total_volume_mdf += bahan_baku.volume
                    total_qty_needed_mdf += bahan_baku.quantity_needed
                    total_volume_needed_mdf += bahan_baku.volume_needed
                    total_qty_spare_mdf += bahan_baku.quantity_spare
                    total_volume_spare_mdf += bahan_baku.volume_spare

                sheet.merge_range(row, 0, row, 5, 'TOTAL ', formatHeaderDetailRightBold)
                sheet.write(row, 6, total_qty_stock_mdf, formatHeaderDetailRightBold)
                sheet.write(row, 7, total_qty_mdf, formatHeaderDetailRightBold)
                sheet.write(row, 8, total_volume_mdf, formatHeaderDetailRightFourBold)
                sheet.write(row, 9, total_qty_needed_mdf, formatHeaderDetailRightBold)
                sheet.write(row, 10, total_volume_needed_mdf, formatHeaderDetailRightFourBold)
                sheet.write(row, 11, total_qty_spare_mdf, formatHeaderDetailRightBold)
                sheet.write(row, 12, total_volume_spare_mdf, formatHeaderDetailRightFourBold)
                sheet.write(row, 13, '', formatHeaderDetailRightFourBold)

            if barecore_ids:
                row += 1
                for bahan_baku in barecore_ids:
                    sheet.write(row, 0, bahan_baku.product_id.jenis_kayu.name, formatHeaderDetailCenter)
                    sheet.write(row, 1, bahan_baku.product_id.goods_type, formatHeaderDetailCenter)
                    sheet.write(row, 2, bahan_baku.product_id.tebal, formatHeaderDetailCenterNumberOne)            
                    sheet.write(row, 3, bahan_baku.product_id.lebar, formatHeaderDetailCenter)            
                    sheet.write(row, 4, bahan_baku.product_id.panjang, formatHeaderDetailCenter)
                    sheet.write(row, 5, bahan_baku.product_id.grade.name, formatHeaderDetailCenter)
                    sheet.write(row, 6, bahan_baku.quantity_available, formatHeaderDetailRight)
                    sheet.write(row, 7, bahan_baku.quantity, formatHeaderDetailRight)
                    sheet.write(row, 8, bahan_baku.volume, formatHeaderDetailRightFour)
                    sheet.write(row, 9, bahan_baku.quantity_needed, formatHeaderDetailRight)
                    sheet.write(row, 10, bahan_baku.volume_needed, formatHeaderDetailRightFour)
                    sheet.write(row, 11, bahan_baku.quantity_spare, formatHeaderDetailRight)
                    sheet.write(row, 12, bahan_baku.volume_spare, formatHeaderDetailRightFour)
                    sheet.write(row, 13, (bahan_baku.notes or ''), formatHeaderDetailLeft)
                    row += 1  

                    total_qty_stock_barecore += bahan_baku.quantity_available
                    total_qty_barecore += bahan_baku.quantity
                    total_volume_barecore += bahan_baku.volume
                    total_qty_needed_barecore += bahan_baku.quantity_needed
                    total_volume_needed_barecore += bahan_baku.volume_needed
                    total_qty_spare_barecore += bahan_baku.quantity_spare
                    total_volume_spare_barecore += bahan_baku.volume_spare

                sheet.merge_range(row, 0, row, 5, 'TOTAL ', formatHeaderDetailRightBold)
                sheet.write(row, 6, total_qty_stock_barecore, formatHeaderDetailRightBold)
                sheet.write(row, 7, total_qty_barecore, formatHeaderDetailRightBold)
                sheet.write(row, 8, total_volume_barecore, formatHeaderDetailRightFourBold)
                sheet.write(row, 9, total_qty_needed_barecore, formatHeaderDetailRightBold)
                sheet.write(row, 10, total_volume_needed_barecore, formatHeaderDetailRightFourBold)
                sheet.write(row, 11, total_qty_spare_barecore, formatHeaderDetailRightBold)
                sheet.write(row, 12, total_volume_spare_barecore, formatHeaderDetailRightFourBold)
                sheet.write(row, 13, '', formatHeaderDetailRightFourBold)