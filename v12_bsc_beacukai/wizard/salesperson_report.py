# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
# from cStringIO import StringIO
import base64
import xlsxwriter
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning

import logging

_logger = logging.getLogger(__name__)



class SalespersonWizard(models.TransientModel):
    _name = "salesperson.wizard"
    _description = "Salesperson wizard"
    
    date_from = fields.Date(string='Tanggal Mulai')
    date_to = fields.Date(string='Tanggal Akhir')
    file = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)

    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['salesperson_id', 'date_from', 'date_to'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['salesperson_id', 'date_from', 'date_to'])[0])
        return self.env['report'].get_action(self, 'v12_bsc_beacukai.report_salesperson', data=data)

    @api.multi
    def open_table(self):
        self.ensure_one()
        ctx = dict(
            self._context,
            date_to=self.date_to,
            date_from=self.date_from)
        
        action = self.env['ir.model.data'].xmlid_to_object('v12_bsc_beacukai.action_beacukai_incoming_line')
        if not action:            
            action = {
                'view_type': 'form',
                'view_mode': 'tree,graph,pivot',
                'res_model': 'beacukai.incoming',
                'type': 'ir.actions.act_window',
            }
        else:
            action = action[0].read()[0]
            # print("===============================================================masuk action ")

        # action = {
        #         'view_type': 'form',
        #         'view_mode': 'tree,graph,pivot',
        #         'res_model': 'beacukai.outgoing.line',
        #         'type': 'ir.actions.act_window',
        #     }

        action['domain'] = "[('date', '>=', '" + self.date_from + "'),('date', '<=', '" + self.date_to + "')]"
        action['name'] = _('Laporan Pemasukan')
        action['context'] = ctx
        return action

    @api.multi
    def print_excel2(self,args1,args2):
        # self.ensure_one()
        _logger.info(self)
        _logger.info(args1)
        _logger.info(args2)

        filename = 'Laporan Pemasukan-%s.xlsx' %(datetime.now().strftime("%Y-%m-%d %H:%M"))

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

        worksheet1.merge_range('A2:L2', 'Laporan Pemasukan Barang Per Dokumen Pabean', left_title)
        worksheet1.merge_range('A3:L3', kbgb+" "+ self.env.user.company_id.name, left_title)
        worksheet1.merge_range('A4:L4', 'Periode: ' + datetime.strptime(args1, '%Y-%m-%d').strftime('%d-%m-%Y') + ' s.d ' + datetime.strptime(args2, '%Y-%m-%d').strftime('%d-%m-%Y'), left_title) 
        row = 6
        worksheet1.write(row, 0, 'No', header_table)
        worksheet1.write(row, 1, 'Jenis Dokumen', header_table)
        worksheet1.write(row, 2, 'Nomor Pendaftaran', header_table)
        worksheet1.write(row, 3, 'Tanggal Pendaftaran', header_table)
        worksheet1.write(row, 4, 'Nomor Pengajuan', header_table)
        worksheet1.write(row, 5, 'Tanggal Pengajuan', header_table)
        worksheet1.write(row, 6, 'Nomor Bukti Penerimaan Barang', header_table)
        worksheet1.write(row, 7, 'Tanggal Bukti Penerimaan Barang', header_table)
        worksheet1.write(row, 8, 'Nomor PO', header_table)
        worksheet1.write(row, 9, 'Kode Barang', header_table)
        worksheet1.write(row, 10, 'Pengirim', header_table)
        worksheet1.write(row, 11, 'Nama Barang', header_table)

        worksheet1.write(row, 12, 'Jumlah', header_table)
        worksheet1.write(row, 13, 'Satuan', header_table)
        worksheet1.write(row, 14, 'Nomor Invoice', header_table)
        worksheet1.write(row, 15, 'Mata Uang', header_table)
        worksheet1.write(row, 16, 'Nilai Barang', header_table)

        i = 0

        line_ids = self.env['beacukai.incoming.line'].search([
            ('date', '>=', args1),
            ('date', '<=', args2)
            ])

        if line_ids:
            for line in line_ids:                            
                row += 1
                i += 1 
                
                worksheet1.write(row, 0, i, set_center)
                worksheet1.write(row, 1, line.reference.document_type_id.name, set_border)
                worksheet1.write(row, 2, line.reference.register_number, set_border)
                worksheet1.write(row, 3, line.reference.register_date, set_border)
                worksheet1.write(row, 4, line.reference.submission_no, set_border)
                worksheet1.write(row, 5, line.reference.date, set_border)
                if line.reference.delivery_note_number:
                    worksheet1.write(row, 6, line.reference.delivery_note_number.name, set_border)
                else:
                    worksheet1.write(row, 6, "-", set_border)
                if line.reference.delivery_note_date:
                    worksheet1.write(row, 7, line.reference.delivery_note_date, set_border)
                else:
                    worksheet1.write(row, 7, "-", set_border)
                worksheet1.write(row, 8, line.reference.po_id.name, set_border)
                worksheet1.write(row, 9, line.product_id.name, set_border)
                if line.reference.po_id.partner_id.name:
                    worksheet1.write(row, 10, line.reference.po_id.partner_id.name, set_border)
                else:
                    worksheet1.write(row, 10, "-", set_border)
                worksheet1.write(row, 11, line.product_name, set_border) 
                worksheet1.write(row, 12, line.product_qty, set_border) 
                worksheet1.write(row, 13, line.product_uom_id.name, set_border) 
                if line.reference.invoice_number.number:
                    worksheet1.write(row, 14, line.reference.invoice_number.number, set_border) 
                else:
                    worksheet1.write(row, 14, "-", set_border)
                worksheet1.write(row, 15, "IDR", set_border)
                worksheet1.write(row, 16, line.cif_amount, set_border)

        worksheet1.write(row+3,8, 'KAMI BERTANGGUNG JAWAB')
        worksheet1.write(row+4,8, 'ATAS KEBENARAN LAPORAN INI')
        worksheet1.write(row+5,8, str(self.env.user.company_id.city).upper()+', ' + datetime.today().strftime('%d %m %Y'))
        worksheet1.write(row+6,8, 'PENGUSAHA DI '+str(kbgb).upper())
        pengusaha = self.env['beacukai.apiu'].search([],limit=1)
        worksheet1.write(row+10,8, str(pengusaha.name).upper())
        worksheet1.write(row+11,8, str(pengusaha.jabatan).upper())

        workbook.close()
        out = base64.encodestring(fp.getvalue())
        
        baru = self.create({'file':out, 'name': filename})
        fp.close()
        return {
            'type': 'ir.actions.act_url',
            'url': "/web/content/salesperson.wizard/%s/file/%s?download=true" % (baru.id,filename),
            'target': 'new'
        }


    @api.multi
    def print_excel(self):
        filename = 'Laporan Pemasukan-%s.xlsx' %(datetime.now().strftime("%Y-%m-%d %H:%M"))

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

        worksheet1.merge_range('A2:L2', 'Laporan Pemasukan Barang Per Dokumen Pabean', left_title)
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

        line_ids = self.env['beacukai.incoming.line'].search([
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to)
            ])

        if line_ids:
            for line in line_ids:                            
                row += 1
                i += 1 
                
                worksheet1.write(row, 0, i, set_center)
                worksheet1.write(row, 1, line.reference.document_type_id.name, set_border)
                worksheet1.write(row, 2, line.reference.register_number, set_border)
                worksheet1.write(row, 3, line.reference.register_date, set_border)
                worksheet1.write(row, 4, line.reference.submission_no, set_border)
                worksheet1.write(row, 5, line.reference.date, set_border)
                if line.reference.delivery_note_number:
                    worksheet1.write(row, 6, line.reference.delivery_note_number.name, set_border)
                else:
                    worksheet1.write(row, 6, "-", set_border)
                if line.reference.delivery_note_date:
                    worksheet1.write(row, 7, line.reference.delivery_note_date, set_border)
                else:
                    worksheet1.write(row, 7, "-", set_border)
                worksheet1.write(row, 8, line.product_id.name, set_border)
                if line.pengirim:
                    worksheet1.write(row, 9, line.pengirim, set_border)
                else:
                    worksheet1.write(row, 9, "-", set_border)
                worksheet1.write(row, 10, line.product_name, set_border) 
                worksheet1.write(row, 11, line.product_qty, set_border) 
                worksheet1.write(row, 12, line.product_uom_id.name, set_border) 
                if line.reference.invoice_number.number:
                    worksheet1.write(row, 13, line.reference.invoice_number.number, set_border) 
                else:
                    worksheet1.write(row, 13, "-", set_border)
                worksheet1.write(row, 14, "IDR", set_border)
                worksheet1.write(row, 15, line.cif_amount, set_border)

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
            'url': "/web/content/salesperson.wizard/%s/file/%s?download=true" % (self.id,filename),
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

class BcOutgoingWizard(models.TransientModel):
    _name = "bcreport.outgoing.wizard"
    _description = "Outgoing Report"
    
    date_from = fields.Date(string='Tanggal Mulai')
    date_to = fields.Date(string='Tanggal Akhir')
    product_id = fields.Many2one('product.product', string="Item Code")
    file = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)

    def get_line_data(self):
        self.ensure_one()
        data_models = [
            'beacukai.outgoing.line.25',
            'beacukai.outgoing.line.27',
            'beacukai.outgoing.line.30',
            'beacukai.outgoing.line.41',
            'beacukai.outgoing.line.261'
        ]

        args = [('reference.register_date', '>=', self.date_from),
                ('reference.register_date', '<=', self.date_to)]
        res = []

        for line_ids in [self.env[data_model].search(args) for data_model in data_models]:
            for line in line_ids:

                supplier = line.reference.supplier_id.name if hasattr(line.reference, 'supplier_id') else ''
                received_qty = line.received_qty if hasattr(line, 'received_qty') else line.product_qty

                res.append({
                    'doc_model': line._name,
                    'doc_id': line.id,
                    'document_type': line.reference.document_type_id.name,
                    'register_number': line.reference.register_number,
                    'register_date': line.reference.register_date,
                    'submission_no': line.reference.submission_no,
                    'ref_date': line.reference.date,
                    'delivery_note': line.reference.delivery_note_number.name,
                    'delivery_note_date': line.reference.delivery_note_date,
                    'supplier': supplier,
                    'product_code': line.product_id.name,
                    'product_name': line.product_code,
                    'received_qty': received_qty,
                    'product_qty': line.product_qty,
                    'product_uom': line.product_uom_id.name,
                    'cif_amount': line.cif_cost,
                    'currency': 'IDR',
                    'invoice_number': line.reference.invoice_number.number or '-'
                })

        return res

    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['date_from', 'date_to','product_id'])[0]
        data['orders'] = self.get_line_data()
        return self._print_report(data)

    def _print_report(self, data):        
        data['form'].update(self.read(['date_from', 'date_to','product_id'])[0])
        return self.env['report'].get_action(self, 'v12_bsc_beacukai.bc_report_outgoing', data=data)

    @api.multi
    def open_table(self):
        self.ensure_one()
        ctx = dict(
            self._context,
            date_to=self.date_to,
            date_from=self.date_from)

        action = self.env['ir.model.data'].xmlid_to_object('v12_bsc_beacukai.action_outgoing_preview')
        action = action[0].read()[0]

        bc_preview_obj = self.env['bcreport.preview']
        recs = self.env['bcreport.preview']

        for data in self.get_line_data():
            recs |= bc_preview_obj.create({
                'doc_model': data['doc_model'],
                'doc_id': data['doc_id'],
                'document_type': data['document_type'],
                'register_number': data['register_number'],
                'register_date': data['register_date'],
                'submission_no': data['submission_no'],
                'ref_date': data['ref_date'],
                'delivery_note_number': data['delivery_note'],
                'delivery_note_date': data['delivery_note_date'],
                'supplier': data['supplier'],
                'product_code': data['product_code'],
                'product_name': data['product_name'],
                'received_qty': data['received_qty'],
                'product_qty': data['product_qty'],
                'product_uom': data['product_uom'],
                'cif_amount': data['cif_amount'],
                'invoice_number': data['invoice_number']
            })

        action['domain'] = [('id', 'in', recs.ids)]
        action['name'] = _('Laporan Pengeluaran')
        action['display_name'] = _('Laporan Pengeluaran')
        action['context'] = ctx
        return action

    @api.multi
    def print_excel(self):
        filename = 'Laporan Pengeluaran-%s.xlsx' %(datetime.now().strftime("%Y-%m-%d %H:%M"))

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

        worksheet1.merge_range('A2:L2', 'Laporan Pengeluaran Per Dokumen Pabean', left_title)
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
        worksheet1.write(row, 9, 'Penerima', header_table)
        worksheet1.write(row, 10, 'Nama Barang', header_table)

        worksheet1.write(row, 11, 'Jumlah', header_table)
        worksheet1.write(row, 12, 'Satuan', header_table)
        worksheet1.write(row, 13, 'Nomor Invoice', header_table)
        worksheet1.write(row, 14, 'Mata Uang', header_table)
        worksheet1.write(row, 15, 'Nilai Barang', header_table)

        i = 0

        for line in self.get_line_data():
            row += 1
            i += 1

            worksheet1.write(row, 0, i, set_center)
            # worksheet1.write(row, 1, line.reference.document_type_id.name, set_border)
            worksheet1.write(row, 1, line['document_type'], set_border)
            worksheet1.write(row, 2, line['register_number'], set_border)
            worksheet1.write(row, 3, line['register_date'], set_border)
            worksheet1.write(row, 4, line['submission_no'], set_border)
            # worksheet1.write(row, 5, line.reference.date, set_border)
            worksheet1.write(row, 5, line['ref_date'], set_border)
            # if line.reference.delivery_note_number:
            #     worksheet1.write(row, 6, line.reference.delivery_note_number.name, set_border)
            # else:
            worksheet1.write(row, 6, "-", set_border)
            # if reference.delivery_note_date:
            #     worksheet1.write(row, 7, line.reference.delivery_note_date, set_border)
            # else:
            worksheet1.write(row, 7, "-", set_border)
            worksheet1.write(row, 8, line['product_code'], set_border)
            # if line.reference.po_id.partner_id.name:
            #     worksheet1.write(row, 9, line.reference.po_id.partner_id.name, set_border)
            # else:
            worksheet1.write(row, 9, "-", set_border)
            # worksheet1.write(row, 10, line.product_name, set_border)
            worksheet1.write(row, 10, line['product_name'], set_border)
            worksheet1.write(row, 11, line['received_qty'], set_border)
            worksheet1.write(row, 12, line['product_qty'], set_border)
            worksheet1.write(row, 13, line['invoice_number'], set_border)
            worksheet1.write(row, 14, line['currency'], set_border)
            # worksheet1.write(row, 15, line.product_amount, set_border)
            worksheet1.write(row, 15, line['cif_amount'], set_border)

        worksheet1.write(row+3,8, 'KAMI BERTANGGUNG JAWAB')
        worksheet1.write(row+4,8, 'ATAS KEBENARAN LAPORAN INI')
        worksheet1.write(row+5,8, str(self.env.user.company_id.city).upper()+', ' + datetime.today().strftime('%d-%m-%Y'))
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
            'url': "/web/content/bcreport.outgoing.wizard/%s/file/%s?download=true" % (self.id,filename),
            'target': 'new'
        }


class BcPreviewWizard(models.TransientModel):
    _name = "bcreport.preview"

    doc_model = fields.Char('Document Model')
    doc_id = fields.Integer('Document Id')
    document_type = fields.Char('Tipe Dokumen')
    register_number = fields.Char('No Pendaftaran')
    register_date = fields.Date('Tanggal Daftar')
    submission_no = fields.Char('Nomor Pengajuan')
    ref_date = fields.Date('Tanggal Aju')
    delivery_note_number = fields.Char('Delivery Note Number')
    delivery_note_date = fields.Datetime('Delivery Note Date')
    purchase_order = fields.Char('No PO')
    supplier = fields.Char('Nama Vendor')
    product_code = fields.Char('Product Code')
    product_name = fields.Char('Product Name')
    received_qty = fields.Float('Received Qty')
    product_qty = fields.Float('Qty')
    product_uom = fields.Char('UoM')
    cif_amount = fields.Float('Cif Amount')
    currency = fields.Char('Currency', default='IDR')
    invoice_number = fields.Char('Nomor Invoice')


class BcIncomingWizard(models.TransientModel):
    _name = "bcreport.incoming.wizard"
    _description = "Incoming Report"
    
    date_from = fields.Date(string='Tanggal Mulai')
    date_to = fields.Date(string='Tanggal Akhir')
    product_id = fields.Many2one('product.product', string="Item Code")
    file = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)

    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['date_from', 'date_to','product_id'])[0]
        data['orders'] = self.get_line_data()
        return self._print_report(data)

    def _print_report(self, data):        
        data['form'].update(self.read(['date_from', 'date_to','product_id'])[0])
        return self.env['report'].get_action(self, 'v12_bsc_beacukai.bc_report_incoming', data=data)

    def get_line_data(self):
        self.ensure_one()
        data_models = [
            'beacukai.incoming.line.23',
            'beacukai.incoming.line.27',
            'beacukai.incoming.line.40',
            'beacukai.incoming.line.262'
        ]

        args = [('reference.register_date', '>=', self.date_from),
                ('reference.register_date', '<=', self.date_to),
                ('reference.state', '=', 'done')]
        res = []

        for line_ids in [self.env[data_model].search(args) for data_model in data_models]:
            for line in line_ids:
                res.append({
                    'doc_model': line._name,
                    'doc_id': line.id,
                    'document_type': line.reference.document_type_id and line.reference.document_type_id.name,
                    'register_number': line.reference.register_number,
                    'register_date': line.reference.register_date,
                    'submission_no': line.reference.submission_no,
                    'ref_date': line.reference.date,
                    'delivery_note': line.reference.delivery_note_number.name,
                    'delivery_note_date': line.reference.delivery_note_date,
                    'purchase_order': line.reference.po_id.name,
                    'supplier': line.reference.supplier_id.name,
                    'product_code': line.product_id.name,
                    'product_name': line.product_code,
                    'received_qty': line.received_qty,
                    'product_qty': line.product_qty,
                    'product_uom': line.product_uom_id.name,
                    'cif_amount': line.cif_amount,
                    'invoice_number': line.reference.invoice_number.number
                })


        return res

    @api.multi
    def open_table(self):
        self.ensure_one()
        ctx = dict(
            self._context,
            date_to=self.date_to,
            date_from=self.date_from)

#<<<<<<< HEAD
        action = self.env['ir.model.data'].xmlid_to_object('v12_bsc_beacukai.action_incoming_preview')
        action = action[0].read()[0]

        bc_preview_obj = self.env['bcreport.preview']
        recs = self.env['bcreport.preview']

        for data in self.get_line_data():
            recs |= bc_preview_obj.create({
                'doc_model': data['doc_model'],
                'doc_id': data['doc_id'],
                'document_type': data['document_type'],
                'register_number': data['register_number'],
                'register_date': data['register_date'],
                'submission_no': data['submission_no'],
                'ref_date': data['ref_date'],
                'delivery_note_number': data['delivery_note'],
                'delivery_note_date': data['delivery_note_date'],
                'purchase_order': data['purchase_order'],
                'supplier': data['supplier'],
                'product_code': data['product_code'],
                'product_name': data['product_name'],
                'received_qty': data['received_qty'],
                'product_qty': data['product_qty'],
                'product_uom': data['product_uom'],
                'cif_amount': data['cif_amount'],
                'invoice_number': data['invoice_number']
            })

        action['domain'] = [('id', 'in', recs.ids)]
        action['name'] = _('Laporan Pemasukkan')
        action['display_name'] = _('Laporan Pemasukkan')
#=======
#        action = self.env['ir.model.data'].xmlid_to_object('v12_bsc_beacukai.action_beacukai_incoming_line_27')
        # if not action:
        #     action = {
        #         'view_type': 'form',
        #         'view_mode': 'tree,graph,pivot',
        #         'res_model': 'beacukai.incoming.line.27',
        #         'type': 'ir.actions.act_window',
        #     }
        # else:
#        action = action[0].read()[0]

        # action = {
        #         'view_type': 'form',
        #         'view_mode': 'tree,graph,pivot',
        #         'res_model': 'beacukai.outgoing.line',
        #         'type': 'ir.actions.act_window',
        #     }

#        action['domain'] = "[('reference.date', '>=', '" + self.date_from + "'),('reference.date', '<=', '" + self.date_to + "')]"
#        action['name'] = _('Laporan Pengeluaran')
#>>>>>>> a255489a717397a63f1b5d96a0ed9aa6a02eda70
        action['context'] = ctx
        return action

    @api.multi
    def print_excel(self):
        filename = 'Laporan Pemasukan-%s.xlsx' %(datetime.now().strftime("%Y-%m-%d %H:%M"))

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

        worksheet1.merge_range('A2:L2', 'Laporan Pemasukan Per Dokumen Pabean', left_title)
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
        worksheet1.write(row, 9, 'Penerima', header_table)
        worksheet1.write(row, 10, 'Nama Barang', header_table)

        worksheet1.write(row, 11, 'Jumlah', header_table)
        worksheet1.write(row, 12, 'Satuan', header_table)
        worksheet1.write(row, 13, 'Nomor Invoice', header_table)
        worksheet1.write(row, 14, 'Mata Uang', header_table)
        worksheet1.write(row, 15, 'Nilai Barang', header_table)

        i = 0

        for line in self.get_line_data():
            row += 1
            i += 1

            worksheet1.write(row, 0, i, set_center)
            worksheet1.write(row, 1, line['document_type'], set_border)
            worksheet1.write(row, 2, line['register_number'], set_border)
            worksheet1.write(row, 3, line['register_date'], set_border)
            worksheet1.write(row, 4, line['submission_no'], set_border)
            worksheet1.write(row, 5, line['ref_date'], set_border)
            worksheet1.write(row, 6, "-", set_border)
            worksheet1.write(row, 7, "-", set_border)
            worksheet1.write(row, 8, line['product_code'], set_border)
            worksheet1.write(row, 9, "-", set_border)
            worksheet1.write(row, 10, line['product_name'], set_border)
            worksheet1.write(row, 11, line['product_qty'], set_border)
            worksheet1.write(row, 12, line['product_uom'], set_border)
            worksheet1.write(row, 13, line['invoice_number'] or '-', set_border)
            worksheet1.write(row, 14, "IDR", set_border)
            worksheet1.write(row, 15, line['cif_amount'], set_border)

        worksheet1.write(row+3,8, 'KAMI BERTANGGUNG JAWAB')
        worksheet1.write(row+4,8, 'ATAS KEBENARAN LAPORAN INI')
        worksheet1.write(row+5,8, str(self.env.user.company_id.city).upper()+', ' + datetime.today().strftime('%d-%m-%Y'))
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
            'url': "/web/content/bcreport.incoming.wizard/%s/file/%s?download=true" % (self.id,filename),
            'target': 'new'
        }        

class BcPosisiWizard(models.TransientModel):
    _name = "bcreport.posisi.wizard"
    _description = "Laporan Posisi Barang"
    
    category = fields.Selection([
        ('RM', 'RM'),
        ('FG', 'FG'),
        ('Machine', 'Machine'),
        ('Scrap', 'Scrap'),
        ])
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')

    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['category', 'date_from', 'date_to'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['category', 'date_from', 'date_to'])[0])
        return self.env['report'].get_action(self, 'v12_bsc_beacukai.bc_report_posisi', data=data)

# WIP
class BcWipWizard(models.TransientModel):
    _name = "bcreport.wip.wizard"
    _description = "Laporan Posisi WIP"
    
    def get_move_line(self,id_product):
        product = self.env['product.product'].browse(id_product)
        loc = int(self.env['ir.config_parameter'].get_param('location_wip', default=''))
        location_id = self.env['stock.location'].browse(loc)
        move_line_ids = self.env['stock.move'].search([
            ('date', '<=', self.date_to),                
            ('state','=','done'),
            '|', ('location_id','=',location_id.id), ('location_dest_id','=',location_id.id)
            ])
        saldo_awal = pemasukan = pengeluaran = penyesuaian = saldo_akhir = stock_opname = selisih = 0
        keterangan = ''

        for move_line in move_line_ids:               
            if move_line.location_id == location_id and move_line.product_id.id == product.id and move_line.date < self.date_from:                        
                saldo_awal -= move_line.product_uom_qty
            elif move_line.location_dest_id == location_id and move_line.product_id.id == product.id and move_line.date < self.date_from:                        
                saldo_awal += move_line.product_uom_qty
            elif move_line.location_id == location_id and move_line.product_id.id == product.id and move_line.date >= self.date_from:                        
                if move_line.location_dest_id.usage == "inventory":
                    penyesuaian -= move_line.product_uom_qty
                else:
                    pengeluaran += move_line.product_uom_qty
            elif move_line.location_dest_id == location_id and move_line.product_id.id == product.id and move_line.date >= self.date_from:                        
                if move_line.location_id.usage == "inventory":
                    penyesuaian += move_line.product_uom_qty
                else:
                    pemasukan += move_line.product_uom_qty
        saldo_akhir = saldo_awal + pemasukan - pengeluaran + penyesuaian
        selisih = abs(saldo_akhir - stock_opname)
        if selisih == 0: 
            keterangan = "Sesuai"
        else:
            keterangan = "Tidak Sesuai"
        res = {
            'saldo_awal' : saldo_awal,
            'pemasukan' : pemasukan,
            'pengeluaran' : pengeluaran,
            'penyesuaian' : penyesuaian,
            'saldo_akhir' : saldo_akhir,
            'stock_opname' : stock_opname,
            'selisih' : selisih,
            'keterangan' : keterangan,
        }
        return res

    def get_laporan_posisi(self,product):
        saldo_akhir = 0
        laporan_posisi_wip = self.env['laporan.posisi.wip'].search([('product_id','=',product)])
        for each in laporan_posisi_wip:
            saldo_akhir += each.product_qty
            res = {
                'saldo_akhir' : saldo_akhir
            }
        return res

    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    file = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)

    @api.one
    def trigger_loc(self):
        for res in self:
            bc_incoming_line_ids = self.env['beacukai.incoming.line'].search([('id','!=',0)])
            for each in bc_incoming_line_ids:
                each.generate_loc()

    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['date_from', 'date_to'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['date_from', 'date_to'])[0])
        return self.env['report'].get_action(self, 'v12_bsc_beacukai.bc_report_wip', data=data)

    def get_move_lines(self):
        loc = self.env['ir.config_parameter'].sudo().get_param('location_wip')
        move_ids = self.env['stock.move'].search([
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('state', '=', 'done'),
            ('location_dest_id', '=', int(loc))
        ])
        return move_ids

    @api.multi
    def open_table(self):
        self.ensure_one()
        action = self.env['ir.model.data'].xmlid_to_object('v12_bsc_beacukai.action_laporan_posisi_wip_transient')
        if not action:
            action = {
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'laporan.posisi.wip.transient',
                'type': 'ir.actions.act_window',
            }
        else:
            action = action[0].read()[0]

        move_ids = self.get_move_lines()

        ids = []
        if move_ids:
            for move in move_ids:
                vals = {
                    'bc_ref_type' : move.picking_id.bc_ref_type,
                    'bc_ref_id' : move.picking_id.bc_ref_id,
                    'move_id' : move.id
                }
                ids.append(self.env['laporan.posisi.wip.transient'].create(vals))

            action['domain'] = "[('id', 'in', " + str([x.id for x in ids]) + ")]"
            action['name'] = _('Laporan WIP')
            return action
        else:
            raise Warning('Data Tidak Ditemukan')
        
    @api.multi
    def print_excel(self):
        filename = 'Laporan WIP-%s.xlsx' %(datetime.now().strftime("%Y-%m-%d %H:%M"))

        # fp = StringIO()
        # workbook  = xlsxwriter.Workbook('haha.xlsx')
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

        worksheet1.merge_range('A2:L2', 'Laporan Posisi WIP', left_title)
        worksheet1.merge_range('A3:L3', kbgb+" "+ self.env.user.company_id.name, left_title)
        worksheet1.merge_range('A4:L4', 'Periode: ' + datetime.strptime(self.date_from, '%Y-%m-%d').strftime('%d-%m-%Y') + ' s.d ' + datetime.strptime(self.date_to, '%Y-%m-%d').strftime('%d-%m-%Y'), left_title) 
        row = 6
        worksheet1.write(row, 0, 'No', header_table)
        worksheet1.write(row, 1, 'Kode Barang', header_table)
        worksheet1.write(row, 2, 'Nama Barang', header_table)
        worksheet1.write(row, 3, 'Satuan', header_table)
        worksheet1.write(row, 4, 'Jumlah', header_table)

        i = 0

        loc = int(self.env['ir.config_parameter'].get_param('location_wip', default=''))
        location_id = self.env['stock.location'].browse(loc)

        move_line_ids = self.env['stock.move'].search([
            ('date', '<=', self.date_to),                
            ('state','=','done'),
            '|', ('location_id','=',location_id.id), ('location_dest_id','=',location_id.id)
            ])

        saldo_awal = pemasukan = pengeluaran = penyesuaian = saldo_akhir = stock_opname = selisih = 0
        keterangan = ''

        if move_line_ids:
            for product in move_line_ids.mapped('product_id'):                
                saldo_awal = pemasukan = pengeluaran = penyesuaian = saldo_akhir = stock_opname = selisih = 0
                keterangan = ''                            
                row += 1
                i += 1 

                inventory_ids = self.env['stock.inventory.line'].search([
                    ('product_id','=',product.id),
                    ('location_id','=',location_id.id),
                    ('inventory_id.date','>=',self.date_from),
                    ('inventory_id.date','<=',self.date_to)
                    ])
                
                worksheet1.write(row, 0, i, set_center)
                worksheet1.write(row, 1, product.name, set_border)
                worksheet1.write(row, 2, product.default_code, set_border)
                worksheet1.write(row, 3, product.uom_id.name, set_center)
                for move_line in move_line_ids:               
                    if move_line.location_id == location_id and move_line.product_id.id == product.id and move_line.date < self.date_from:                        
                        saldo_awal -= move_line.product_uom_qty
                    elif move_line.location_dest_id == location_id and move_line.product_id.id == product.id and move_line.date < self.date_from:                        
                        saldo_awal += move_line.product_uom_qty
                    elif move_line.location_id == location_id and move_line.product_id.id == product.id and move_line.date >= self.date_from:                        
                        if move_line.location_dest_id.usage == "inventory":
                            penyesuaian -= move_line.product_uom_qty
                        else:
                            pengeluaran += move_line.product_uom_qty
                    elif move_line.location_dest_id == location_id and move_line.product_id.id == product.id and move_line.date >= self.date_from:                        
                        if move_line.location_id.usage == "inventory":
                            penyesuaian += move_line.product_uom_qty
                        else:
                            pemasukan += move_line.product_uom_qty
                    
                    saldo_akhir = saldo_awal + pemasukan - pengeluaran + penyesuaian
                    selisih = abs(saldo_akhir - stock_opname)
                    if selisih == 0: 
                        keterangan = "Sesuai"
                    else:
                        keterangan = "Tidak Sesuai"
                worksheet1.write(row, 4, saldo_akhir, set_border) 

        worksheet1.write(row+3,4, 'KAMI BERTANGGUNG JAWAB')
        worksheet1.write(row+4,4, 'ATAS KEBENARAN LAPORAN INI')
        worksheet1.write(row+5,4, str(self.env.user.company_id.city).upper()+', ' + datetime.today().strftime('%d-%m-%Y'))
        worksheet1.write(row+6,4, 'PENGUSAHA DI '+str(kbgb).upper())
        pengusaha = self.env['beacukai.apiu'].search([],limit=1)
        worksheet1.write(row+10,4, str(pengusaha.name).upper())
        worksheet1.write(row+11,4, str(pengusaha.jabatan).upper())

        workbook.close()
        out = base64.encodestring(fp.getvalue())
        
        self.write({'file':out, 'name': filename})
        fp.close()
        return {
            'type': 'ir.actions.act_url',
            # 'url': "/web/content?model=bcreport.wip.wizard&field=file&filename_field=name&id=%s" % (self.id),
            'url': "/web/content/bcreport.wip.wizard/%s/file/%s?download=true" % (self.id,filename),
            'target': 'new'
        }

    @api.multi
    def print_excel_new(self):
        filename = 'Laporan WIP-%s.xlsx' %(datetime.now().strftime("%Y-%m-%d %H:%M"))

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

        bc_type = self.env['ir.config_parameter'].get_param('bc_type')
        kbgb = ""
        if bc_type:
            kbgb = "Gudang Berikat"
        else:
            kbgb = "Kawasan Berikat"

        worksheet1.merge_range('A2:L2', 'Laporan Posisi WIP', left_title)
        worksheet1.merge_range('A3:L3', kbgb+" "+ self.env.user.company_id.name, left_title)
        worksheet1.merge_range('A4:L4', 'Periode: ' + datetime.strptime(self.date_from, '%Y-%m-%d').strftime('%d-%m-%Y') + ' s.d ' + datetime.strptime(self.date_to, '%Y-%m-%d').strftime('%d-%m-%Y'), left_title) 
        row = 6
        worksheet1.write(row, 0, 'No', header_table)
        worksheet1.write(row, 1, 'Kode Barang', header_table)
        worksheet1.write(row, 2, 'Nama Barang', header_table)
        worksheet1.write(row, 3, 'Satuan', header_table)
        worksheet1.write(row, 4, 'Jumlah', header_table)

        i = 0

        move_line_ids = self.get_move_lines()

        for move in move_line_ids:
            row += 1
            i += 1

            worksheet1.write(row, 0, i, set_center)
            worksheet1.write(row, 1, move.product_id.name, set_border)
            worksheet1.write(row, 2, move.product_id.default_code, set_border)
            worksheet1.write(row, 3, move.product_id.uom_id.name, set_center)
            worksheet1.write(row, 4, move.product_uom_qty, set_border)

        worksheet1.write(row+3,4, 'KAMI BERTANGGUNG JAWAB')
        worksheet1.write(row+4,4, 'ATAS KEBENARAN LAPORAN INI')
        worksheet1.write(row+5,4, str(self.env.user.company_id.city).upper()+', ' + datetime.today().strftime('%d-%m-%Y'))
        worksheet1.write(row+6,4, 'PENGUSAHA DI '+str(kbgb).upper())
        pengusaha = self.env['beacukai.apiu'].search([],limit=1)
        worksheet1.write(row+10,4, str(pengusaha.name).upper())
        worksheet1.write(row+11,4, str(pengusaha.jabatan).upper())

        workbook.close()
        out = base64.encodestring(fp.getvalue())
        
        self.write({'file':out, 'name': filename})
        fp.close()
        return {
            'type': 'ir.actions.act_url',
            'url': "/web/content/bcreport.wip.wizard/%s/file/%s?download=true" % (self.id, filename),
            'target': 'new'
        }
