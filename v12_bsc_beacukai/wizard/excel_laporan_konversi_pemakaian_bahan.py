# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
from cStringIO import StringIO
import base64
import xlsxwriter
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning
import logging

_logger = logging.getLogger(__name__)


# class ReportBahanbaku(models.AbstractModel):
#     _name = 'report.v10_bsc_beacukai.report_bahanbaku'

    # @api.model
    # def render_html(self, docids, data=None):
    #     self.model = self.env.context.get('active_model')
    #     docs = self.env[self.model].browse(self.env.context.get('active_id'))
    #     bc_type = self.env['ir.config_parameter'].sudo().get_param('bc_type')
    #     docs.bc_type = ""
    #     if bc_type == 0 :
    #         docs.bc_type = "Kawasan Berikat"
    #     else :
    #         docs.bc_type = "Gudang Berikat"
    #     sales_records = []

    #     location_id = int(self.env['ir.config_parameter'].sudo().get_param('location_bahanbakupenolong'))

    #     move_line_ids = self.env['stock.move'].search([
    #         ('date', '<=', docs.date_to),
    #         ('state','=','done'),
    #         '|', ('location_id','=',location_id), ('location_dest_id','=',location_id)
    #         ])

    #     data_product = []
    #     for product in move_line_ids.mapped('product_id'):
    #         data_product.append(product)

    #     docargs = {
    #         'doc_ids': self.ids,
    #         'doc_model': self.model,
    #         'docs': docs,
    #         'time': time,
    #         'product' : data_product,
    #         'header': self.env['beacukai.apiu'].search([],limit=1)
    #     }
    #     return self.env['report'].render('v10_bsc_beacukai.report_bahanbaku', docargs)


class ExcelLaporanKonversPemakaianBahan(models.TransientModel):
    _name = 'excel.laporan.konversi.pemakaian.bahan'

    # @api.multi
    # def open_table(self):
    #     self.ensure_one()
    #     ctx = dict(
    #         self._context,
    #         date_to=self.date_to,
    #         date_from=self.date_from,
    #         group_by="product_id")

    #     action = self.env['ir.model.data'].xmlid_to_object('v10_bsc_beacukai.action_laporan_mutasi')
    #action = self.env['ir.model.data'].xmlid_to_object('v10_bsc_beacukai.action_laporan_mutasi_bahan_baku')
    # if not action:
    #     action = {
    #         'view_type': 'form',
    #         'view_mode': 'tree,graph,pivot',
    #         'res_model': 'laporan.mutasi',
    #         'type': 'ir.actions.act_window',
    #     }
    # else:
    #     action = action[0].read()[0]

    # action = {
    #         'view_type': 'form',
    #         'view_mode': 'tree,graph,pivot',
    #         'res_model': 'beacukai.outgoing.line',
    #         'type': 'ir.actions.act_window',
    #     }

    # action['domain'] = "[('report_name','=','" + "Name" + "')]"
    # action['name'] = _('Laporan Mutasi Per ' + str(self.date_from) + ' - ' + str(self.date_to))
    # action['context'] = ctx
    # return action

    # loc = self.env['ir.config_parameter'].sudo().get_param('location_bahanbakupenolong')
    # location_id = self.env['stock.location'].browse(loc)

    # action['domain'] = "[('date', '>=', '" + self.date_from + "'),('date', '<=', '" + self.date_to + "'),'|',('location_id', '=', " + loc + "),('location_dest_id', '=', " + loc + ")]"
    # action['name'] = _('Laporan Pertanggungjawaban Bahan Baku')
    # action['context'] = ctx
    # return action

    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date', default=fields.Date.today())
    state_position = fields.Selection(
        [('choose', 'choose'), ('get', 'get')], default='choose')
    #location_id = fields.Many2one('stock.location', string="Location", domain="[('usage','=','internal')]")
    location_id = fields.Many2one('stock.location', 'Location')
    data = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    contract_number = fields.Char('Nomor Kontrak')
    subcontract_company_npwp = fields.Char('NPWP Subkontrak')
    subcontract_company_name = fields.Char('Nama Perusahaan Subkontrak')
    subcontract_company_address = fields.Text('Alamat Perusahaan Subkontrak')

    @api.multi
    def generate_report(self):
        filename = 'Laporan Konversi Pemakaian Bahan.xlsx'

        fp = StringIO()
        workbook = xlsxwriter.Workbook(fp)
        #################################################################################
        center_title = workbook.add_format(
            {'bold': 1, 'valign': 'vcenter', 'align': 'center'})
        center_title.set_font_size('13')
        center_title.set_bg_color('#eff0f2')
        center_title.set_border()
        #################################################################################
        left_title = workbook.add_format(
            {'bold': 1, 'valign': 'vcenter', 'align': 'left'})
        left_title.set_font_size('12')
        left_title.set_bg_color('#eff0f2')
        left_title.set_border()
        #################################################################################
        bold_font = workbook.add_format(
            {'bold': 1, 'valign': 'vcenter', 'align': 'left'})
        bold_font.set_text_wrap()
        #################################################################################
        header_table = workbook.add_format(
            {'bold': 1, 'valign': 'vcenter', 'align': 'center'})
        header_table.set_text_wrap()
        header_table.set_bg_color('#eff0f2')
        header_table.set_border()
        #################################################################################
        footer_table = workbook.add_format(
            {'bold': 1, 'valign': 'vcenter', 'align': 'right'})
        footer_table.set_text_wrap()
        footer_table.set_border()
        #################################################################################
        set_right = workbook.add_format(
            {'valign': 'vcenter', 'align': 'right'})
        set_right.set_text_wrap()
        set_right.set_border()
        #################################################################################
        set_center = workbook.add_format(
            {'valign': 'vcenter', 'align': 'center'})
        set_center.set_text_wrap()
        set_center.set_border()
        #################################################################################
        set_border = workbook.add_format(
            {'valign': 'vcenter', 'align': 'left'})
        set_border.set_text_wrap()
        set_border.set_border()

        product_ids = self.env['product.product'].search([
            ('active', '=', True)
        ])

        worksheet1 = workbook.add_worksheet('All Account')
        worksheet1.set_column('A:A', 10)
        worksheet1.set_column('B:B', 5)
        worksheet1.set_column('C:C', 20)
        worksheet1.set_column('D:D', 5)
        worksheet1.set_column('E:E', 20)
        worksheet1.set_column('F:F', 10)
        worksheet1.set_column('G:G', 10)
        worksheet1.set_column('H:H', 5)
        worksheet1.set_column('I:I', 20)
        worksheet1.set_column('J:J', 5)
        worksheet1.set_column('K:K', 20)
        worksheet1.set_column('L:L', 10)
        worksheet1.set_column('M:M', 10)
        worksheet1.set_column('N:N', 10)
        worksheet1.set_column('O:O', 8)
        worksheet1.set_column('P:P', 8)
        worksheet1.set_column('Q:Q', 8)
        worksheet1.set_column('R:R', 8)
        worksheet1.set_column('S:S', 8)
        worksheet1.set_column('T:T', 8)
        # worksheet1.set_row(1, 20)
        # worksheet1.set_row(2, 20)
        # worksheet1.set_row(3, 20)
        # worksheet1.set_row(6, 30)

        # print self.env.user.company_id.name

        # bc_type = self.env['ir.config_parameter'].sudo().get_param('bc_type')
        # kbgb = ""
        # if bc_type==0:
        #     kbgb = "Kawasan Berikat"
        # else:
        #     kbgb = "Gudang Berikat"
        loc = self.env['ir.config_parameter'].sudo().get_param('location_bahanbakupenolong')
        location_id = self.env['stock.location'].browse(loc)

        # move_line_ids = self.env['stock.move'].search([
        #     ('date', '<=', self.date_to),
        #     ('state', '=', 'done'),
        #     ('bom_line_id', '!=', 0),
        #     '|', ('location_id', '=',
        #           location_id.id), ('location_dest_id', '=', location_id.id)
        # ])
        # move_line_ids = self.env['stock.move'].search([
        #     ('date', '<=', self.date_to),
        #     ('state', '=', 'done'),
        #     ('bom_line_id', '!=', False)
        # ])
        move_line_ids = self.env['stock.move'].search([
            ('date', '<=', self.date_to),
            ('state', '=', 'done'),
            ('production_id', '!=', False)
        ])
        # print("==========================move_line_ids : ",move_line_ids)
        worksheet1.merge_range(
            'A2:L2', 'Laporan Konversi Pemakaian Bahan (Subkontrak)', left_title)
        worksheet1.merge_range('A3:B3', 'Nomor Kontrak', left_title)
        worksheet1.merge_range(
            'C3:L3', self.contract_number, left_title)
        worksheet1.merge_range('A4:B4', 'Tanggal ', left_title)
        worksheet1. merge_range('C4:L4', datetime.strptime(self.date_from, '%Y-%m-%d').strftime(
            '%d - %m - %Y') + ' s.d ' + datetime.strptime(self.date_to, '%Y-%m-%d').strftime('%d - %m - %Y'), left_title)

        worksheet1.merge_range(
            'A6:C6', 'DATA PENGUSAHA TPB ', left_title)
        worksheet1.merge_range('A7:C7', 'A. NPWP ', left_title)
        worksheet1.merge_range(
            'D7:F7', self.env.user.company_id.company_npwp, left_title)
        worksheet1.merge_range('A8:C8', 'B. NAMA TPB ', left_title)
        worksheet1.merge_range(
            'D8:F8', self.env.user.company_id.name, left_title)
        worksheet1.merge_range(
            'A9:C9', 'C. NOMOR SURAT IZIN TPB ', left_title)
        worksheet1.merge_range(
            'D9:F9', self.env.user.company_id.company_permission_no, left_title)
        worksheet1.merge_range(
            'A10:C10', 'D. TANGGAL SURAT IZIN TPB ', left_title)
        worksheet1.merge_range(
            'D10:F10', self.env.user.company_id.company_permission_date, left_title)
        
        worksheet1.merge_range(
            'H6:J6', 'DATA PENERIMA SUBKONTRAK ', left_title)
        worksheet1.merge_range('H7:J7', 'A. NPWP ', left_title)
        worksheet1.merge_range(
            'K7:M7', self.subcontract_company_npwp, left_title)
        worksheet1.merge_range(
            'H8:J8', 'B. NAMA PERUSAHAAN ', left_title)
        worksheet1.merge_range(
            'K8:M8', self.subcontract_company_name, left_title)
        worksheet1.merge_range('H9:J9', 'C. ALAMAT ', left_title)
        worksheet1.merge_range(
            'K9:M9', self.subcontract_company_address, left_title)

        row = 12
        row1 = 13
        worksheet1.merge_range('A12:A13', 'NOMOR KONVERSI', header_table)
        worksheet1.write(row1, 0, '1a', header_table)
        worksheet1.write(row, 1, 'NO.', header_table)
        worksheet1.write(row1, 1, '1b', header_table)
        worksheet1.merge_range('B12:G12', 'DATA BARANG JADI', header_table)
        worksheet1.write(row, 2, 'KODE BARANG JADI', header_table)
        worksheet1.write(row1, 2, '1c', header_table)
        worksheet1.write(row, 3, 'HS', header_table)
        worksheet1.write(row1, 3, '1d', header_table)
        worksheet1.write(row, 4, 'URAIAN BARANG', header_table)
        worksheet1.write(row1, 4, '1e', header_table)
        worksheet1.write(row, 5, 'JUMLAH', header_table)
        worksheet1.write(row1, 5, '1f', header_table)
        worksheet1.write(row, 6, 'SATUAN', header_table)
        worksheet1.write(row1, 6, '1g', header_table)
        worksheet1.merge_range('H12:N12', 'KONVERSI', header_table)
        worksheet1.write(row, 7, 'NO.', header_table)
        worksheet1.write(row1, 7, '2a.', header_table)
        worksheet1.write(row, 8, 'KODE BARANG BAKU', header_table)
        worksheet1.write(row1, 8, '2b', header_table)
        worksheet1.write(row, 9, 'HS', header_table)
        worksheet1.write(row1, 9, '2c', header_table)
        worksheet1.write(row, 10, 'URAIAN BARANG', header_table)
        worksheet1.write(row1, 10, '2d', header_table)
        worksheet1.write(row, 11, 'JUMLAH', header_table)
        worksheet1.write(row1, 11, '2f', header_table)
        worksheet1.write(row, 12, 'SATUAN', header_table)
        worksheet1.write(row1, 12, '2g', header_table)
        worksheet1.write(row, 13, 'KOEFISIEN', header_table)
        worksheet1.write(row1, 13, '2h', header_table)
        worksheet1.merge_range('O12:T12', 'BAHAN BAKU TERKANDUNG', header_table)
        worksheet1.merge_range('O13:Q13', 'TERKANDUNG (%)', header_table)
        worksheet1.merge_range('O14:Q14', '3a', header_table)
        worksheet1.merge_range('R13:T13', 'WASTE / SCRAP (%)', header_table)
        worksheet1.merge_range('R14:T14', '3b', header_table)

        i = 0
        j = 0
        k = -1
        # location_ids = self.env['beacukai.config'].search([
        #     ('kode','=','Bahan Baku dan Bahan Penolong')
        #     ])

        # if not location_ids:
        #     raise UserError(_('Belum tersedia pengaturan lokasi untuk Laporan ini'))

        # loc = int(self.env['ir.config_parameter'].sudo(
        # ).get_param('location_bahanbakupenolong'))
        # location_id = self.env['stock.location'].browse(loc)

        # move_line_ids = self.env['stock.move'].search([
        #     ('date', '<=', self.date_to),
        #     ('state', '=', 'done'),
        #     ('bom_line_id', '!=', 0),
        #     '|', ('location_id', '=',
        #           location_id.id), ('location_dest_id', '=', location_id.id)
        # ])

        # saldo_awal = pemasukan = pengeluaran = penyesuaian = saldo_akhir = stock_opname = selisih = 0
        # keterangan = ''
        raw_finished = self.env['stock.move'].search([
                ('date', '<=', self.date_to),
                ('state', '=', 'done'),
                ('raw_material_production_id', '=', move_line_ids.production_id.id)
        ])
        # print("=======================================raw_finished : ",raw_finished)

        # if move_line_ids:
        for product in move_line_ids:
            row1 += 1
            i += 1
            # saldo_awal = pemasukan = pengeluaran = penyesuaian = saldo_akhir = stock_opname = selisih = 0
            # keterangan = ''

            # inventory_ids = self.env['stock.inventory.line'].search([
            #     ('product_id', '=', product.id),
            #     ('location_id', '=', location_id.id),
            #     ('inventory_id.date', '>=', self.date_from),
            #     ('inventory_id.date', '<=', self.date_to)
            # ])

            # if inventory_ids:
            #     for inventory in inventory_ids:
            #         stock_opname = inventory.product_qty

            # move_mrp_ids = self.env['mrp.production'].search(
            #     [('id', '=', product.production_id.id)])

            # if product.active:
            # for row in range(product):
            worksheet1.write(row1, 0, product.origin, set_center)
            worksheet1.write(row1, 1, i, set_center)
            worksheet1.write(
                row1, 2, product.product_id.default_code, set_border)
            worksheet1.write(row1, 3, product.hs_code, set_center)

            # for move_line in move_line_ids:
            #     if move_line.location_id == location_id and move_line.product_id.id == product.id and move_line.date < self.date_from:
            #         saldo_awal -= move_line.product_uom_qty
            #     elif move_line.location_dest_id == location_id and move_line.product_id.id == product.id and move_line.date < self.date_from:
            #         saldo_awal += move_line.product_uom_qty
            #     elif move_line.location_id == location_id and move_line.product_id.id == product.id and move_line.date >= self.date_from:
            #         if move_line.location_dest_id.usage == "inventory":
            #             penyesuaian -= move_line.product_uom_qty
            #         else:
            #             pengeluaran += move_line.product_uom_qty
            #     elif move_line.location_dest_id == location_id and move_line.product_id.id == product.id and move_line.date >= self.date_from:
            #         if move_line.location_id.usage == "inventory":
            #             penyesuaian += move_line.product_uom_qty
            #         else:
            #             pemasukan += move_line.product_uom_qty

            # saldo_akhir = saldo_awal + pemasukan - pengeluaran + penyesuaian
            # selisih = abs(saldo_akhir - stock_opname)
            # if selisih == 0:
            #     keterangan = "Sesuai"
            # else:
            #     keterangan = "Tidak Sesuai"

            worksheet1.write(
                row1, 4, product.product_id.name, set_border)
            worksheet1.write(
                row1, 5, product.product_uom_qty, set_right)
            worksheet1.write(
                row1, 6, product.uom_id.name, set_right)
            # for row1 in range(row+1):
            # product_finished = product.production_id
            # raw_finished = self.env['stock.move'].search([
            #     ('date', '<=', self.date_to),
            #     ('state', '=', 'done'),
            #     ('raw_material_production_id', '=', product_finished.id)
            # ])
            # print("=======================================raw_finished : ",raw_finished)
            # if product.bom_line_id:
            for bom_finished in raw_finished:
                j += 1
                # row2 = row1
                k += 1
                # for k in range(len(raw_finished)):
                worksheet1.write(row1+k, 7, j, set_right)
                # print("=====================================bom_finished.product_id.name = ",bom_finished.product_id.name)
                worksheet1.write(
                    row1+k, 8, bom_finished.product_id.default_code, set_right)
                worksheet1.write(
                    row1+k, 9, bom_finished.product_id.hs_code, set_right)
                worksheet1.write(
                    row1+k, 10, bom_finished.product_id.name, set_right)
                worksheet1.write(
                    row1+k, 11, bom_finished.product_uom_qty, set_right)
                worksheet1.write(
                    row1+k, 12, bom_finished.product_id.uom_id.name, set_right)
                koefisien = float(
                    bom_finished.product_uom_qty / product.product_uom_qty)
                worksheet1.write(
                    row1+k, 13, koefisien, set_right)
                percent_terkandung = 0.00
                qty_waste = int(
                    (bom_finished.product_uom_qty * bom_finished.product_id.waste)/100)
                percent_terkandung = 100.00 - bom_finished.product_id.waste
                qty_terkandung = int(
                    bom_finished.product_uom_qty - qty_waste)

                worksheet1.write(
                    row1+k, 14, str(percent_terkandung)+'%', set_right)
                worksheet1.write(row1+k, 15, qty_terkandung,set_right)
                worksheet1.write(row1+k, 16, bom_finished.product_id.uom_id.name, set_right)
                worksheet1.write(row1+k, 17, str(bom_finished.product_id.waste)+'%',set_right)
                worksheet1.write(row1+k, 18, qty_waste,set_right)
                worksheet1.write(row1+k, 19, bom_finished.product_id.uom_id.name, set_right)

            pengusaha = self.env['beacukai.apiu'].search([], limit=1)
            worksheet1.write(row1+7, 14, str(self.env.user.company_id.city).upper() +
                             ', ' + datetime.today().strftime('%d-%m-%Y'))
            worksheet1.write(row1+8, 14, str(self.env.user.company_id.name).upper())
            worksheet1.write(row1+13, 14, str(pengusaha.name).upper())
            worksheet1.write(row1+14, 14, str(pengusaha.jabatan).upper())

        workbook.close()
        out = base64.encodestring(fp.getvalue())
        self.write({'data': out, 'name': filename, 'state_position': 'get'})
        fp.close()
        ir_model_data = self.env['ir.model.data']
        form_res = ir_model_data.get_object_reference(
            'v10_bsc_beacukai', 'excel_laporan_konversi_pemakaian_bahan_form')
        form_id = form_res and form_res[1] or False
        return {
            'name': ('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'excel.laporan.konversi.pemakaian.bahan',
            'res_id': self.id,
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }
