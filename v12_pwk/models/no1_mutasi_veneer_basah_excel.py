# -*- coding: utf-8 -*-

import datetime
from datetime import datetime
import pytz
from odoo import models


class MutasiVeneerBasahReportXls(models.AbstractModel):
    _name = 'report.v12_pwk.mutasi_veneer_basah_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_data(self, data):
        print('data ', data)
        print('self', self)
        lines = []

        vals = {
                'name' : 'add',
                }

        lines.append(vals)
        
        return lines

    def generate_xlsx_report(self, workbook, data, lines):        
        get_data = self.get_data
        alamat = ' Jl. Raya Krangan - Pringsurat, Karanglo, Kupen, Kec. Pringsurat, Kabupaten Temanggung, Jawa Tengah 56272'

        sheet = workbook.add_worksheet('Sheet 1')
        format0 = workbook.add_format({'font_size': 20, 'align': 'center', 'bold': True})
        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        formatHeaderCompany = workbook.add_format({'font_size': 12, 'align': 'left', 'bold': True})
        formatHeader = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left', 'bold': False, 'text_wrap': True})
        formatHeaderCenter = workbook.add_format({'font_size': 14, 'valign':'vcenter', 'align': 'center', 'bold': True, 'text_wrap': True})
        formatHeaderRight = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left', 'num_format': '#,##0'})
        formatHeaderTable = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'bold': True, 'bg_color':'#4ead2f', 'color':'white', 'text_wrap': True})
        formatHeaderTableRight = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'right', 'bold': True, 'bg_color':'#3eaec2', 'text_wrap': True, 'num_format': '#,##0'})
        formatHeaderDetailCenter = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'centre', 'text_wrap': True})
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
        sheet.set_column(2, 2, 5)
        sheet.set_column(3, 3, 2)
        sheet.set_column(4, 4, 5)
        sheet.set_column(5, 5, 2)
        sheet.set_column(6, 6, 5)
        sheet.set_column(7, 7, 15)
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
        sheet.set_column(20, 20, 10)
        sheet.set_column(21, 21, 10)
        sheet.set_column(22, 22, 10)
        sheet.set_column(23, 23, 10)

        # sheet.set_row(8, 25)
        # sheet.set_row(9, 30)

        # Header        
        sheet.merge_range(2, 0, 2, 16, 'LAPORAN MUTASI VENEER BASAH - STACKING', formatHeaderCenter)
        sheet.merge_range(3, 0, 3, 16, lines.date.strftime("%d-%m-%Y"), formatHeaderCenter)

        # merge 1 - 4 
        sheet.merge_range(5, 0, 8, 0, 'NO', formatHeaderTable)
        sheet.merge_range(5, 1, 8, 1, 'JENIS KAYU', formatHeaderTable)
        sheet.merge_range(5, 2, 6, 6, 'UKURAN', formatHeaderTable)
        sheet.merge_range(5, 7, 8, 7, 'GRADE', formatHeaderTable)
        sheet.merge_range(5, 8, 7, 9, 'STOK AWAL', formatHeaderTable)
        sheet.merge_range(5, 10, 5, 17, 'MASUK', formatHeaderTable)
        sheet.merge_range(5, 18, 5, 25, 'KELUAR', formatHeaderTable)
        sheet.merge_range(5, 26, 7, 27, 'STOK AKHIR', formatHeaderTable)

        # Merge 3 and 4
        sheet.merge_range(7, 2, 8, 2, 'T', formatHeaderTable)
        sheet.merge_range(7, 3, 8, 3, '', formatHeaderTable)
        sheet.merge_range(7, 4, 8, 4, 'L', formatHeaderTable)
        sheet.merge_range(7, 5, 8, 5, '', formatHeaderTable)
        sheet.merge_range(7, 6, 8, 6, 'P', formatHeaderTable)
        
        # Row 2
        sheet.merge_range(6, 10, 6, 13, 'SUPPLIER', formatHeaderTable)
        sheet.merge_range(6, 14, 6, 17, 'ROTARY', formatHeaderTable)
        sheet.merge_range(6, 18, 6, 21, 'STACKING', formatHeaderTable)
        sheet.merge_range(6, 22, 6, 25, 'ROLERDRYER', formatHeaderTable)

        # Row 3
        sheet.merge_range(7, 10, 7, 11, 'HARI INI', formatHeaderTable)
        sheet.merge_range(7, 12, 7, 13, 'AKUMULASI', formatHeaderTable)

        sheet.merge_range(7, 14, 7, 15, 'HARI INI', formatHeaderTable)
        sheet.merge_range(7, 16, 7, 17, 'AKUMULASI', formatHeaderTable)

        sheet.merge_range(7, 18, 7, 19, 'HARI INI', formatHeaderTable)
        sheet.merge_range(7, 20, 7, 21, 'AKUMULASI', formatHeaderTable)

        sheet.merge_range(7, 22, 7, 23, 'HARI INI', formatHeaderTable)
        sheet.merge_range(7, 24, 7, 25, 'AKUMULASI', formatHeaderTable)

        # Row 4
        sheet.write(8, 8, 'PCS', formatHeaderTable)
        sheet.write(8, 9, 'M3', formatHeaderTable)
        sheet.write(8, 10, 'PCS', formatHeaderTable)
        sheet.write(8, 11, 'M3', formatHeaderTable)
        sheet.write(8, 12, 'PCS', formatHeaderTable)
        sheet.write(8, 13, 'M3', formatHeaderTable)
        sheet.write(8, 14, 'PCS', formatHeaderTable)
        sheet.write(8, 15, 'M3', formatHeaderTable)
        sheet.write(8, 16, 'PCS', formatHeaderTable)
        sheet.write(8, 17, 'M3', formatHeaderTable)
        sheet.write(8, 18, 'PCS', formatHeaderTable)
        sheet.write(8, 19, 'M3', formatHeaderTable)
        sheet.write(8, 20, 'PCS', formatHeaderTable)
        sheet.write(8, 21, 'M3', formatHeaderTable)
        sheet.write(8, 22, 'PCS', formatHeaderTable)
        sheet.write(8, 23, 'M3', formatHeaderTable)
        sheet.write(8, 24, 'PCS', formatHeaderTable)
        sheet.write(8, 25, 'M3', formatHeaderTable)

        row = 9
        number = 1
        for i in get_data:         
            # sheet.write(row, 0, number, formatHeaderDetailCenter)
            # sheet.write(row, 1, i['jenis_kayu'], formatHeaderDetailCenter)            
            # sheet.write(row, 2, i['tebal'], formatHeaderDetailCenter)
            # sheet.write(row, 3, '', formatHeaderDetailCenter)
            # sheet.write(row, 4, i['lebar'], formatHeaderDetailCenter)
            # sheet.write(row, 5, '', formatHeaderDetailCenter)
            # sheet.write(row, 6, i['panjang'], formatHeaderDetailCenter)

            # sheet.write(row, 7, i['grade'], formatHeaderDetailCenterNumberFour)
            # sheet.write(row, 8, i['awal_pcs'], formatHeaderDetailCenterNumber)
            # sheet.write(row, 9, i['awal_vol'], formatHeaderDetailCenterNumber)

            # sheet.write(row, 10, i['masuk_supplier_pcs'], formatHeaderDetailCenterNumber)
            # sheet.write(row, 11, i['masuk_supplier_vol'], formatHeaderDetailCenter)
            # sheet.write(row, 12, i['masuk_supplier_acc_pcs'], formatHeaderDetailCenter)
            # sheet.write(row, 13, i['masuk_supplier_acc_vol'], formatHeaderDetailCenter)

            # sheet.write(row, 14, i['masuk_rotary_pcs'], formatHeaderDetailCenterNumber)
            # sheet.write(row, 15, i['masuk_rotary_vol'], formatHeaderDetailCenterNumber)
            # sheet.write(row, 14, i['masuk_rotary_acc_pcs'], formatHeaderDetailCenterNumber)
            # sheet.write(row, 15, i['masuk_rotary_acc_vol'], formatHeaderDetailCenterNumber)


            # sheet.write(row, 16, i['keluar_stacking_pcs'], formatHeaderDetailCenterNumber)
            # sheet.write(row, 16, i['keluar_stacking_vol'], formatHeaderDetailCenterNumber)
            # sheet.write(row, 16, i['keluar_stacking_acc_pcs'], formatHeaderDetailCenterNumber)
            # sheet.write(row, 16, i['keluar_stacking_acc_vol'], formatHeaderDetailCenterNumber)

            # sheet.write(row, 16, i['keluar_roler_pcs'], formatHeaderDetailCenterNumber)
            # sheet.write(row, 16, i['keluar_roler_vol'], formatHeaderDetailCenterNumber)
            # sheet.write(row, 16, i['keluar_roler_acc_pcs'], formatHeaderDetailCenterNumber)
            # sheet.write(row, 16, i['keluar_roler_acc_vol'], formatHeaderDetailCenterNumber)

            # sheet.write(row, 16, i['akhir_pcs'], formatHeaderDetailCenterNumber)
            # sheet.write(row, 16, i['akhir_vol'], formatHeaderDetailCenterNumber)
            
            row += 1
            number += 1