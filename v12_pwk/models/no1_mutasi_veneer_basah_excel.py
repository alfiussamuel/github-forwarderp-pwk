# -*- coding: utf-8 -*-

import datetime
from datetime import datetime
import pytz
from odoo import models


class MutasiVeneerBasahReportXls(models.AbstractModel):
    _name = 'report.v12_pwk.mutasi_veneer_basah_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_data(self, data):        
        lines = []
        if data.stacking_ids:
            for line in data.stacking_ids:
                vals = {
                        'jenis_kayu' : line.product_id.jenis_kayu_id.name,
                        'tebal': line.tebal,
                        'lebar': line.lebar,
                        'panjang': line.panjang,
                        'grade': line.grade.name,
                        'awal_pcs': line.stock_awal_pcs,
                        'awal_vol': line.stock_awal_vol,
                        'masuk_supplier_pcs': line.stock_masuk_supplier_pcs,
                        'masuk_supplier_vol': line.stock_masuk_supplier_vol,
                        'masuk_supplier_acc_pcs': line.acc_stock_masuk_supplier_pcs,
                        'masuk_supplier_acc_vol': line.acc_stock_masuk_supplier_vol,
                        'masuk_rotary_pcs': line.stock_masuk_rotary_pcs,
                        'masuk_rotary_vol': line.stock_masuk_rotary_vol,
                        'masuk_rotary_acc_pcs': line.acc_stock_masuk_rotary_pcs,
                        'masuk_rotary_acc_vol': line.acc_stock_masuk_rotary_vol,
                        'keluar_stacking_pcs': line.stock_keluar_stacking_pcs,
                        'keluar_stacking_vol': line.stock_keluar_stacking_vol,
                        'keluar_stacking_acc_pcs': line.acc_stock_keluar_stacking_pcs,
                        'keluar_stacking_acc_vol': line.acc_stock_keluar_stacking_vol,
                        'keluar_roler_pcs': line.stock_keluar_roler_pcs,
                        'keluar_roler_vol': line.stock_keluar_roler_vol,
                        'keluar_roler_acc_pcs': line.acc_stock_keluar_roler_pcs,
                        'keluar_roler_acc_vol': line.acc_stock_keluar_roler_vol,
                        'akhir_pcs': line.stock_akhir_pcs,
                        'akhir_vol': line.stock_akhir_vol,
                        }

                lines.append(vals)

        return lines

    def get_data2(self, data):        
        lines = []
        if data.kd_ids:
            for line in data.kd_ids:
                vals = {
                        'jenis_kayu' : line.product_id.jenis_kayu_id.name,
                        'tebal': line.tebal,
                        'lebar': line.lebar,
                        'panjang': line.panjang,
                        'grade': line.grade.name,
                        'awal_pcs': line.stock_awal_pcs,
                        'awal_vol': line.stock_awal_vol,
                        'masuk_pcs': line.stock_masuk_pcs,
                        'masuk_vol': line.stock_masuk_vol,
                        'masuk_acc_pcs': line.acc_stock_masuk_pcs,
                        'masuk_acc_vol': line.acc_stock_masuk_vol,
                        'keluar_pcs': line.stock_keluar_pcs,
                        'keluar_vol': line.stock_keluar_vol,
                        'keluar_acc_pcs': line.acc_stock_keluar_pcs,
                        'keluar_acc_vol': line.acc_stock_keluar_vol,
                        'akhir_pcs': line.stock_akhir_pcs,
                        'akhir_vol': line.stock_akhir_vol,
                        }

                lines.append(vals)

        return lines

    def get_data3(self, data):        
        lines = []
        if data.kd_re_ids:
            for line in data.kd_re_ids:
                vals = {
                        'jenis_kayu' : line.product_id.jenis_kayu_id.name,
                        'tebal': line.tebal,
                        'lebar': line.lebar,
                        'panjang': line.panjang,
                        'grade': line.grade.name,
                        'awal_pcs': line.stock_awal_pcs,
                        'awal_vol': line.stock_awal_vol,
                        'masuk_pcs': line.stock_masuk_pcs,
                        'masuk_vol': line.stock_masuk_vol,
                        'masuk_acc_pcs': line.acc_stock_masuk_pcs,
                        'masuk_acc_vol': line.acc_stock_masuk_vol,
                        'keluar_pcs': line.stock_keluar_pcs,
                        'keluar_vol': line.stock_keluar_vol,
                        'keluar_acc_pcs': line.acc_stock_keluar_pcs,
                        'keluar_acc_vol': line.acc_stock_keluar_vol,
                        'akhir_pcs': line.stock_akhir_pcs,
                        'akhir_vol': line.stock_akhir_vol,
                        }

                lines.append(vals)

        return lines

    def generate_xlsx_report(self, workbook, data, lines):        
        get_data = self.get_data(lines)
        get_data2 = self.get_data2(lines)
        get_data3 = self.get_data3(lines)
        alamat = ' Jl. Raya Krangan - Pringsurat, Karanglo, Kupen, Kec. Pringsurat, Kabupaten Temanggung, Jawa Tengah 56272'

        sheet = workbook.add_worksheet('Sheet 1')
        format0 = workbook.add_format({'font_size': 20, 'align': 'center', 'bold': True})
        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        formatHeaderCompany = workbook.add_format({'font_size': 12, 'align': 'left', 'bold': True})
        formatHeader = workbook.add_format({'font_size': 10, 'valign':'vcenter', 'align': 'left', 'bold': False, 'text_wrap': True})
        formatHeaderCenter = workbook.add_format({'font_size': 14, 'valign':'vcenter', 'align': 'center', 'bold': True, 'text_wrap': True})
        formatHeaderLeft = workbook.add_format({'font_size': 14, 'valign':'vcenter', 'align': 'left', 'bold': True, 'text_wrap': True})
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
        formatHeaderDetailLeft.set_border(1)
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
        sheet.set_column(7, 7, 10)
        sheet.set_column(8, 8, 5)
        sheet.set_column(9, 9, 5)
        sheet.set_column(10, 10, 8)
        sheet.set_column(11, 11, 8)
        sheet.set_column(12, 12, 8)
        sheet.set_column(13, 13, 8)
        sheet.set_column(14, 14, 8)
        sheet.set_column(15, 15, 8)
        sheet.set_column(16, 16, 8)
        sheet.set_column(17, 17, 8)
        sheet.set_column(18, 18, 8)
        sheet.set_column(19, 19, 8)
        sheet.set_column(20, 20, 8)
        sheet.set_column(21, 21, 8)
        sheet.set_column(22, 22, 8)
        sheet.set_column(23, 23, 8)

        # Data 1
        row = 5

        sheet.merge_range(row-3, 0, row-3, 27, 'LAPORAN MUTASI VENEER BASAH - STACKING', formatHeaderCenter)
        sheet.merge_range(row-2, 0, row-2, 27, lines.date.strftime("%d-%m-%Y"), formatHeaderCenter)

        # merge 1 - 4 
        sheet.merge_range(row, 0, row+3, 0, 'NO', formatHeaderTable)
        sheet.merge_range(row, 1, row+3, 1, 'JENIS KAYU', formatHeaderTable)
        sheet.merge_range(row, 2, row+1, 6, 'UKURAN', formatHeaderTable)
        sheet.merge_range(row, 7, row+3, 7, 'GRADE', formatHeaderTable)
        sheet.merge_range(row, 8, row+2, 9, 'STOK AWAL', formatHeaderTable)
        sheet.merge_range(row, 10, row, 17, 'MASUK', formatHeaderTable)
        sheet.merge_range(row, 18, row, 25, 'KELUAR', formatHeaderTable)
        sheet.merge_range(row, 26, row+2, 27, 'STOK AKHIR', formatHeaderTable)

        # Merge 3 and 4
        sheet.merge_range(row+2, 2, row+3, 2, 'T', formatHeaderTable)
        sheet.merge_range(row+2, 3, row+3, 3, '', formatHeaderTable)
        sheet.merge_range(row+2, 4, row+3, 4, 'L', formatHeaderTable)
        sheet.merge_range(row+2, 5, row+3, 5, '', formatHeaderTable)
        sheet.merge_range(row+2, 6, row+3, 6, 'P', formatHeaderTable)
        
        # Row 2
        sheet.merge_range(row+1, 10, row+1, 13, 'SUPPLIER', formatHeaderTable)
        sheet.merge_range(row+1, 14, row+1, 17, 'ROTARY', formatHeaderTable)
        sheet.merge_range(row+1, 18, row+1, 21, 'STACKING', formatHeaderTable)
        sheet.merge_range(row+1, 22, row+1, 25, 'ROLERDRYER', formatHeaderTable)

        # Row 3
        sheet.merge_range(row+2, 10, row+2, 11, 'HARI INI', formatHeaderTable)
        sheet.merge_range(row+2, 12, row+2, 13, 'AKUMULASI', formatHeaderTable)

        sheet.merge_range(row+2, 14, row+2, 15, 'HARI INI', formatHeaderTable)
        sheet.merge_range(row+2, 16, row+2, 17, 'AKUMULASI', formatHeaderTable)

        sheet.merge_range(row+2, 18, row+2, 19, 'HARI INI', formatHeaderTable)
        sheet.merge_range(row+2, 20, row+2, 21, 'AKUMULASI', formatHeaderTable)

        sheet.merge_range(row+2, 22, row+2, 23, 'HARI INI', formatHeaderTable)
        sheet.merge_range(row+2, 24, row+2, 25, 'AKUMULASI', formatHeaderTable)

        # Row 4
        sheet.write(row+3, 8, 'PCS', formatHeaderTable)
        sheet.write(row+3, 9, 'M3', formatHeaderTable)
        sheet.write(row+3, 10, 'PCS', formatHeaderTable)
        sheet.write(row+3, 11, 'M3', formatHeaderTable)
        sheet.write(row+3, 12, 'PCS', formatHeaderTable)
        sheet.write(row+3, 13, 'M3', formatHeaderTable)
        sheet.write(row+3, 14, 'PCS', formatHeaderTable)
        sheet.write(row+3, 15, 'M3', formatHeaderTable)
        sheet.write(row+3, 16, 'PCS', formatHeaderTable)
        sheet.write(row+3, 17, 'M3', formatHeaderTable)
        sheet.write(row+3, 18, 'PCS', formatHeaderTable)
        sheet.write(row+3, 19, 'M3', formatHeaderTable)
        sheet.write(row+3, 20, 'PCS', formatHeaderTable)
        sheet.write(row+3, 21, 'M3', formatHeaderTable)
        sheet.write(row+3, 22, 'PCS', formatHeaderTable)
        sheet.write(row+3, 23, 'M3', formatHeaderTable)
        sheet.write(row+3, 24, 'PCS', formatHeaderTable)
        sheet.write(row+3, 25, 'M3', formatHeaderTable)
        sheet.write(row+3, 26, 'PCS', formatHeaderTable)
        sheet.write(row+3, 27, 'M3', formatHeaderTable)

        row = 9
        number = 1
        for i in get_data:         
            sheet.write(row, 0, number, formatHeaderDetailCenter)
            sheet.write(row, 1, i['jenis_kayu'], formatHeaderDetailCenter)            
            sheet.write(row, 2, i['tebal'], formatHeaderDetailCenter)
            sheet.write(row, 3, '', formatHeaderDetailCenter)
            sheet.write(row, 4, i['lebar'], formatHeaderDetailCenter)
            sheet.write(row, 5, '', formatHeaderDetailCenter)
            sheet.write(row, 6, i['panjang'], formatHeaderDetailCenter)

            sheet.write(row, 7, i['grade'], formatHeaderDetailCenterNumberFour)
            sheet.write(row, 8, i['awal_pcs'], formatHeaderDetailCenterNumber)
            sheet.write(row, 9, i['awal_vol'], formatHeaderDetailCenterNumber)

            sheet.write(row, 10, i['masuk_supplier_pcs'], formatHeaderDetailCenterNumber)
            sheet.write(row, 11, i['masuk_supplier_vol'], formatHeaderDetailCenter)
            sheet.write(row, 12, i['masuk_supplier_acc_pcs'], formatHeaderDetailCenter)
            sheet.write(row, 13, i['masuk_supplier_acc_vol'], formatHeaderDetailCenter)

            sheet.write(row, 14, i['masuk_rotary_pcs'], formatHeaderDetailCenterNumber)
            sheet.write(row, 15, i['masuk_rotary_vol'], formatHeaderDetailCenterNumber)
            sheet.write(row, 16, i['masuk_rotary_acc_pcs'], formatHeaderDetailCenterNumber)
            sheet.write(row, 17, i['masuk_rotary_acc_vol'], formatHeaderDetailCenterNumber)


            sheet.write(row, 18, i['keluar_stacking_pcs'], formatHeaderDetailCenterNumber)
            sheet.write(row, 19, i['keluar_stacking_vol'], formatHeaderDetailCenterNumber)
            sheet.write(row, 20, i['keluar_stacking_acc_pcs'], formatHeaderDetailCenterNumber)
            sheet.write(row, 21, i['keluar_stacking_acc_vol'], formatHeaderDetailCenterNumber)

            sheet.write(row, 22, i['keluar_roler_pcs'], formatHeaderDetailCenterNumber)
            sheet.write(row, 23, i['keluar_roler_vol'], formatHeaderDetailCenterNumber)
            sheet.write(row, 24, i['keluar_roler_acc_pcs'], formatHeaderDetailCenterNumber)
            sheet.write(row, 25, i['keluar_roler_acc_vol'], formatHeaderDetailCenterNumber)

            sheet.write(row, 26, i['akhir_pcs'], formatHeaderDetailCenterNumber)
            sheet.write(row, 27, i['akhir_vol'], formatHeaderDetailCenterNumber)
            
            row += 1
            number += 1


        # Data 2
        row += 5
        number = 1

        sheet.merge_range(row-3, 0, row-3, 27, 'LAPORAN MUTASI VENEER BASAH - IN KD', formatHeaderCenter)
        sheet.merge_range(row-2, 0, row-2, 27, lines.date.strftime("%d-%m-%Y"), formatHeaderCenter)

        sheet.merge_range(row, 0, row+3, 0, 'NO', formatHeaderTable)
        sheet.merge_range(row, 1, row+3, 1, 'JENIS KAYU', formatHeaderTable)
        sheet.merge_range(row, 2, row+1, 6, 'UKURAN', formatHeaderTable)
        sheet.merge_range(row, 7, row+3, 7, 'GRADE', formatHeaderTable)
        sheet.merge_range(row, 8, row+2, 9, 'STOK AWAL', formatHeaderTable)
        sheet.merge_range(row, 10, row, 13, 'MASUK', formatHeaderTable)
        sheet.merge_range(row, 14, row, 17, 'KELUAR', formatHeaderTable)
        sheet.merge_range(row, 18, row+2, 19, 'STOK AKHIR', formatHeaderTable)

        # Merge 3 and 4
        sheet.merge_range(row+2, 2, row+3, 2, 'T', formatHeaderTable)
        sheet.merge_range(row+2, 3, row+3, 3, '', formatHeaderTable)
        sheet.merge_range(row+2, 4, row+3, 4, 'L', formatHeaderTable)
        sheet.merge_range(row+2, 5, row+3, 5, '', formatHeaderTable)
        sheet.merge_range(row+2, 6, row+3, 6, 'P', formatHeaderTable)
        
        # Row 2
        sheet.merge_range(row+1, 10, row+1, 13, 'SUPPLIER', formatHeaderTable)                
        sheet.merge_range(row+1, 14, row+1, 17, 'ROLERDRYER', formatHeaderTable)

        # Row 3
        sheet.merge_range(row+2, 10, row+2, 11, 'HARI INI', formatHeaderTable)
        sheet.merge_range(row+2, 12, row+2, 13, 'AKUMULASI', formatHeaderTable)

        sheet.merge_range(row+2, 14, row+2, 15, 'HARI INI', formatHeaderTable)
        sheet.merge_range(row+2, 16, row+2, 17, 'AKUMULASI', formatHeaderTable)
        

        # Row 4
        sheet.write(row+3, 8, 'PCS', formatHeaderTable)
        sheet.write(row+3, 9, 'M3', formatHeaderTable)
        sheet.write(row+3, 10, 'PCS', formatHeaderTable)
        sheet.write(row+3, 11, 'M3', formatHeaderTable)
        sheet.write(row+3, 12, 'PCS', formatHeaderTable)
        sheet.write(row+3, 13, 'M3', formatHeaderTable)
        sheet.write(row+3, 14, 'PCS', formatHeaderTable)
        sheet.write(row+3, 15, 'M3', formatHeaderTable)
        sheet.write(row+3, 16, 'PCS', formatHeaderTable)
        sheet.write(row+3, 17, 'M3', formatHeaderTable)
        sheet.write(row+3, 18, 'PCS', formatHeaderTable)
        sheet.write(row+3, 19, 'M3', formatHeaderTable)

        row += 4

        for i in get_data2:
            sheet.write(row, 0, number, formatHeaderDetailCenter)
            sheet.write(row, 1, i['jenis_kayu'], formatHeaderDetailCenter)            
            sheet.write(row, 2, i['tebal'], formatHeaderDetailCenter)
            sheet.write(row, 3, '', formatHeaderDetailCenter)
            sheet.write(row, 4, i['lebar'], formatHeaderDetailCenter)
            sheet.write(row, 5, '', formatHeaderDetailCenter)
            sheet.write(row, 6, i['panjang'], formatHeaderDetailCenter)

            sheet.write(row, 7, i['grade'], formatHeaderDetailCenterNumberFour)
            sheet.write(row, 8, i['awal_pcs'], formatHeaderDetailCenterNumber)
            sheet.write(row, 9, i['awal_vol'], formatHeaderDetailCenterNumber)

            sheet.write(row, 10, i['masuk_pcs'], formatHeaderDetailCenterNumber)
            sheet.write(row, 11, i['masuk_vol'], formatHeaderDetailCenter)
            sheet.write(row, 12, i['masuk_acc_pcs'], formatHeaderDetailCenter)
            sheet.write(row, 13, i['masuk_acc_vol'], formatHeaderDetailCenter)

            sheet.write(row, 14, i['keluar_pcs'], formatHeaderDetailCenterNumber)
            sheet.write(row, 15, i['keluar_vol'], formatHeaderDetailCenterNumber)
            sheet.write(row, 16, i['keluar_acc_pcs'], formatHeaderDetailCenterNumber)
            sheet.write(row, 17, i['keluar_acc_vol'], formatHeaderDetailCenterNumber)

            sheet.write(row, 18, i['akhir_pcs'], formatHeaderDetailCenterNumber)
            sheet.write(row, 19, i['akhir_vol'], formatHeaderDetailCenterNumber)
            
            row += 1
            number += 1


        # Data 3
        if get_data3:
            row += 5
            number = 1

            sheet.merge_range(row-3, 0, row-3, 27, 'LAPORAN MUTASI VENEER BASAH - RE-IN KD', formatHeaderCenter)
            sheet.merge_range(row-2, 0, row-2, 27, lines.date.strftime("%d-%m-%Y"), formatHeaderCenter)

            sheet.merge_range(row, 0, row+3, 0, 'NO', formatHeaderTable)
            sheet.merge_range(row, 1, row+3, 1, 'JENIS KAYU', formatHeaderTable)
            sheet.merge_range(row, 2, row+1, 6, 'UKURAN', formatHeaderTable)
            sheet.merge_range(row, 7, row+3, 7, 'GRADE', formatHeaderTable)
            sheet.merge_range(row, 8, row+2, 9, 'STOK AWAL', formatHeaderTable)
            sheet.merge_range(row, 10, row, 13, 'MASUK', formatHeaderTable)
            sheet.merge_range(row, 14, row, 17, 'KELUAR', formatHeaderTable)
            sheet.merge_range(row, 18, row+2, 19, 'STOK AKHIR', formatHeaderTable)

            # Merge 3 and 4
            sheet.merge_range(row+2, 2, row+3, 2, 'T', formatHeaderTable)
            sheet.merge_range(row+2, 3, row+3, 3, '', formatHeaderTable)
            sheet.merge_range(row+2, 4, row+3, 4, 'L', formatHeaderTable)
            sheet.merge_range(row+2, 5, row+3, 5, '', formatHeaderTable)
            sheet.merge_range(row+2, 6, row+3, 6, 'P', formatHeaderTable)
            
            # Row 2
            sheet.merge_range(row+1, 10, row+1, 13, 'SUPPLIER', formatHeaderTable)                
            sheet.merge_range(row+1, 14, row+1, 17, 'ROLERDRYER', formatHeaderTable)

            # Row 3
            sheet.merge_range(row+2, 10, row+2, 11, 'HARI INI', formatHeaderTable)
            sheet.merge_range(row+2, 12, row+2, 13, 'AKUMULASI', formatHeaderTable)

            sheet.merge_range(row+2, 14, row+2, 15, 'HARI INI', formatHeaderTable)
            sheet.merge_range(row+2, 16, row+2, 17, 'AKUMULASI', formatHeaderTable)
            

            # Row 4
            sheet.write(row+3, 8, 'PCS', formatHeaderTable)
            sheet.write(row+3, 9, 'M3', formatHeaderTable)
            sheet.write(row+3, 10, 'PCS', formatHeaderTable)
            sheet.write(row+3, 11, 'M3', formatHeaderTable)
            sheet.write(row+3, 12, 'PCS', formatHeaderTable)
            sheet.write(row+3, 13, 'M3', formatHeaderTable)
            sheet.write(row+3, 14, 'PCS', formatHeaderTable)
            sheet.write(row+3, 15, 'M3', formatHeaderTable)
            sheet.write(row+3, 16, 'PCS', formatHeaderTable)
            sheet.write(row+3, 17, 'M3', formatHeaderTable)
            sheet.write(row+3, 18, 'PCS', formatHeaderTable)
            sheet.write(row+3, 19, 'M3', formatHeaderTable)

            row += 4

            for i in get_data3:
                sheet.write(row, 0, number, formatHeaderDetailCenter)
                sheet.write(row, 1, i['jenis_kayu'], formatHeaderDetailCenter)            
                sheet.write(row, 2, i['tebal'], formatHeaderDetailCenter)
                sheet.write(row, 3, '', formatHeaderDetailCenter)
                sheet.write(row, 4, i['lebar'], formatHeaderDetailCenter)
                sheet.write(row, 5, '', formatHeaderDetailCenter)
                sheet.write(row, 6, i['panjang'], formatHeaderDetailCenter)

                sheet.write(row, 7, i['grade'], formatHeaderDetailCenterNumberFour)
                sheet.write(row, 8, i['awal_pcs'], formatHeaderDetailCenterNumber)
                sheet.write(row, 9, i['awal_vol'], formatHeaderDetailCenterNumber)

                sheet.write(row, 10, i['masuk_pcs'], formatHeaderDetailCenterNumber)
                sheet.write(row, 11, i['masuk_vol'], formatHeaderDetailCenter)
                sheet.write(row, 12, i['masuk_acc_pcs'], formatHeaderDetailCenter)
                sheet.write(row, 13, i['masuk_acc_vol'], formatHeaderDetailCenter)

                sheet.write(row, 14, i['keluar_pcs'], formatHeaderDetailCenterNumber)
                sheet.write(row, 15, i['keluar_vol'], formatHeaderDetailCenterNumber)
                sheet.write(row, 16, i['keluar_acc_pcs'], formatHeaderDetailCenterNumber)
                sheet.write(row, 17, i['keluar_acc_vol'], formatHeaderDetailCenterNumber)

                sheet.write(row, 18, i['akhir_pcs'], formatHeaderDetailCenterNumber)
                sheet.write(row, 19, i['akhir_vol'], formatHeaderDetailCenterNumber)
                
                row += 1
                number += 1