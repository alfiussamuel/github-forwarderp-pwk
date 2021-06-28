# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
# from cStringIO import StringIO
import base64
import xlsxwriter
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning

import logging

_logger = logging.getLogger(__name__)



class Bc23Wizard(models.TransientModel):
    _name = "bc23.wizard"
    _description = "BC23 wizard"
    
    date_from = fields.Date(string='Tanggal Mulai')
    date_to = fields.Date(string='Tanggal Akhir')
    file = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)

    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['date_from', 'date_to'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['date_from', 'date_to'])[0])
        return self.env['report'].get_action(self, 'v12_bsc_beacukai.report_bc23', data=data)

    @api.multi
    def open_table(self):
        self.ensure_one()
        ctx = dict(
            self._context,
            date_to=self.date_to,
            date_from=self.date_from)

        action = self.env['ir.model.data'].xmlid_to_object('v12_bsc_beacukai.action_beacukai_incoming_line_bc_2_3')
        #action = self.env['ir.model.data'].xmlid_to_object('v12_bsc_beacukai.action_beacukai_incoming')
        if not action:
            action = {
                'view_type': 'form',
                'view_mode': 'tree,graph,pivot',
                'res_model': 'beacukai.incoming.23',
                'type': 'ir.actions.act_window',
            }
        else:
            action = action[0].read()[0]


        # action = {
        #         'view_type': 'form',
        #         'view_mode': 'tree,graph,pivot',
        #         'res_model': 'beacukai.outgoing.line',
        #         'type': 'ir.actions.act_window',
        #     }

        action['domain'] = "[('date_aju_line', '>=', '" + self.date_from + "'),('date_aju_line', '<=', '" + self.date_to + "')]"
        action['name'] = _('Laporan Pemasukan')
        action['context'] = ctx
        return action


    @api.multi
    def print_excel(self):
        filename = 'Laporan Pemasukan BC23-%s.xlsx' %(datetime.now().strftime("%Y-%m-%d %H:%M"))

        # fp = StringIO()
        workbook = xlsxwriter.Workbook(fp)
        #################################################################################
        center_title = workbook.add_format({'bold': 1, 'valign':'vcenter', 'align':'center'})
        center_title.set_font_size('13')
        center_title.set_bg_color('#eff0f2')
        center_title.set_border()
        #################################################################################
        left_title = workbook.add_format({'bold': 1, 'valign':'vcenter', 'align':'left'})
        left_title.set_font_size('13')
        left_title.set_bg_color('#eff0f2')
        left_title.set_border()
        #################################################################################
        bold_font = workbook.add_format({'bold': 1, 'valign':'vcenter', 'align':'left'})
        bold_font.set_text_wrap()
        #################################################################################
        header_table = workbook.add_format({'bold': 1, 'valign':'vcenter', 'align':'center'})
        header_table.set_text_wrap()
        header_table.set_bg_color('#eff0f2')
        header_table.set_border()
        #################################################################################
        footer_table = workbook.add_format({'bold': 1, 'valign':'vcenter', 'align':'right'})
        footer_table.set_text_wrap()
        footer_table.set_border()
        #################################################################################
        set_right = workbook.add_format({'valign':'vcenter', 'align':'right'})
        set_right.set_text_wrap()
        set_right.set_border()
        #################################################################################
        set_center = workbook.add_format({'valign':'vcenter', 'align':'center'})
        set_center.set_text_wrap()
        set_center.set_border()
        #################################################################################
        set_border = workbook.add_format({'valign':'vcenter', 'align':'left'})
        set_border.set_text_wrap()
        set_border.set_border()

        product_ids = self.env['product.product'].search([
            ('active','=',True)
            ])
                  
        worksheet1 = workbook.add_worksheet('All Account')
        worksheet1.set_column('A:A', 5)
        worksheet1.set_column('B:B', 20)
        worksheet1.set_column('C:C', 70)
        worksheet1.set_column('D:D', 10)
        worksheet1.set_column('E:E', 15)
        worksheet1.set_column('F:F', 15)
        worksheet1.set_column('G:G', 15)
        worksheet1.set_column('H:H', 15)
        worksheet1.set_column('I:I', 15)
        worksheet1.set_column('J:J', 15)
        worksheet1.set_column('K:K', 15)
        worksheet1.set_column('L:L', 15)
        worksheet1.set_row(1, 20)
        worksheet1.set_row(2, 20)
        worksheet1.set_row(3, 20)
        worksheet1.set_row(6, 30)

        # print self.env.user.company_id.name

        bc_type = self.env['ir.config_parameter'].get_param('bc_type')
        kbgb = ""
        if bc_type:
            kbgb = "Gudang Berikat"
        else:
            kbgb = "Kawasan Berikat"

        worksheet1.merge_range('A2:L2', 'Laporan Pemasukan Barang Per Dokumen BC 2.3', left_title)
        worksheet1.merge_range('A3:L3', kbgb+" "+ self.env.user.company_id.name, left_title)
        worksheet1.merge_range('A4:L4', 'Periode: ' + datetime.strptime(self.date_from, '%Y-%m-%d').strftime('%d-%m-%Y') + ' s.d ' + datetime.strptime(self.date_to, '%Y-%m-%d').strftime('%d-%m-%Y'), left_title) 
        row = 6
        worksheet1.write(row, 0, 'No', header_table)
        worksheet1.write(row, 1, 'Jenis Dokumen', header_table)
        worksheet1.write(row, 2, 'Nomor Pendaftaran', header_table)
        worksheet1.write(row, 3, 'Tanggal Pendaftaran', header_table)
        worksheet1.write(row, 4, 'Nomor Pengajuan', header_table)
        worksheet1.write(row, 5, 'Tanggal Pengajuan', header_table)
        worksheet1.write(row, 6, 'Nomor Bukti Penerimaan Barang', header_table)
        worksheet1.write(row, 7, 'Tanggal Bukti Penerimaan Barang', header_table)
        worksheet1.write(row, 8, 'Kode Barang', header_table)
        worksheet1.write(row, 9, 'Pengirim', header_table)
        worksheet1.write(row, 10, 'Nama Barang', header_table)

        worksheet1.write(row, 11, 'Jumlah', header_table)
        worksheet1.write(row, 12, 'Satuan', header_table)
        worksheet1.write(row, 13, 'Nomor Invoice', header_table)
        worksheet1.write(row, 14, 'Mata Uang', header_table)
        worksheet1.write(row, 15, 'Nilai Barang', header_table)

        i = 0

        line_ids = self.env['beacukai.incoming.line.23'].search([
            ('date_aju_line', '>=', self.date_from),
            ('date_aju_line', '<=', self.date_to)
            ])

        if line_ids:
            for line in line_ids:                            
                row += 1
                i += 1 
                
                worksheet1.write(row, 0, i, set_center)
                worksheet1.write(row, 1, line.reference23.document_type_id.name, set_border)
                worksheet1.write(row, 2, line.reference23.register_number, set_border)
                worksheet1.write(row, 3, line.reference23.register_date, set_border)
                worksheet1.write(row, 4, line.reference23.submission_no, set_border)
                worksheet1.write(row, 5, line.reference23.date_aju, set_border)
                if line.reference23.delivery_note_number:
                    worksheet1.write(row, 6, line.reference23.delivery_note_number.name, set_border)
                else:
                    worksheet1.write(row, 6, "-", set_border)
                if line.reference23.delivery_note_date:
                    worksheet1.write(row, 7, line.reference23.delivery_note_date, set_border)
                else:
                    worksheet1.write(row, 7, "-", set_border)
                worksheet1.write(row, 8, line.product_id.name, set_border)
                if line.reference23.po_id.partner_id.name:
                    worksheet1.write(row, 9, line.reference23.po_id.partner_id.name, set_border)
                else:
                    worksheet1.write(row, 9, "-", set_border)
                worksheet1.write(row, 10, line.product_name, set_border) 
                worksheet1.write(row, 11, line.product_qty, set_border) 
                worksheet1.write(row, 12, line.product_uom_id.name, set_border) 
                if line.reference23.invoice_number.number:
                    worksheet1.write(row, 13, line.reference23.invoice_number.number, set_border) 
                else:
                    worksheet1.write(row, 13, "-", set_border)
                worksheet1.write(row, 14, line.product_id.currency_id.name, set_border) 
                worksheet1.write(row, 15, line.product_amount, set_border) 

        worksheet1.write(row+3,8, 'KAMI BERTANGGUNG JAWAB')
        worksheet1.write(row+4,8, 'ATAS KEBENARAN LAPORAN INI')
        worksheet1.write(row+5,8, str(self.env.user.company_id.city).upper()+', ' + datetime.today().strftime('%d %m %Y'))
        worksheet1.write(row+6,8, 'PENGUSAHA DI '+str(kbgb).upper())
        pengusaha = self.env['beacukai.apiu'].search([],limit=1)
        worksheet1.write(row+10,8, str(pengusaha.name).upper())
        worksheet1.write(row+11,8, str(pengusaha.jabatan).upper())

        workbook.close()
        out = base64.encodestring(fp.getvalue())
        
        self.write({'file':out, 'name': filename})
        fp.close()
        return {
            'type': 'ir.actions.act_url',
            'url': "/web/content/bc23.wizard/%s/file/%s?download=true" % (self.id,filename),
            'target': 'new'
        }
        # ir_model_data = self.env['ir.model.data']
        # form_res = ir_model_data.get_object_reference(
        #     'v12_bsc_beacukai', 'excel_laporan_pertanggungjawaban_bahan_baku_form')
        # form_id = form_res and form_res[1] or False
        # return {
        #     'name': ('Download XLS'),
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'excel.laporan.pertanggungjawaban.bahan.baku',
        #     'res_id': self.id,
        #     'view_id': False,
        #     'views': [(form_id, 'form')],
        #     'type': 'ir.actions.act_window',
        #     'target': 'current'
        # }
