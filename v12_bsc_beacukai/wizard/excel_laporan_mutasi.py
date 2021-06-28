# -*- coding: utf-8 -*-
from datetime import datetime
from cStringIO import StringIO
import base64
import xlsxwriter
from odoo import models, fields, api, _
from odoo.exceptions import Warning
import time


class ReportMutasi(models.AbstractModel):
    _name = 'report.v10_bsc_beacukai.report_pertanggungjawaban_mutasi'

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        bc_type = self.env['ir.config_parameter'].sudo().get_param('bc_type')
        docs.bc_type = ""
        if bc_type == 0:
            docs.bc_type = "Kawasan Berikat"
        else:
            docs.bc_type = "Gudang Berikat"

        template_name = data['ctx'].get('template_name', 'v10_bsc_beacukai.report_pertanggungjawaban_mutasi')

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'report_name': data['ctx'].get('title', ''),
            'ctx': data['ctx'],
            'product': docs.get_report(docs.date_from, docs.date_to, data['locations']),
            'header': self.env['beacukai.apiu'].search([], limit=1)
        }
        return self.env['report'].render(template_name, docargs)


class ExcelLaporanMutasi(models.TransientModel):
    _name = 'excel.laporan.mutasi'

    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date', default=fields.Date.today())
    state_position = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    location_id = fields.Many2one('stock.location', string="Location")
    data = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)

    def get_location(self):
        ctx = dict(self._context)
        str_location = ctx.get('location', False)
        str_location2 = ctx.get('location2', False)
        locations = [int(self.env['ir.config_parameter'].sudo().get_param(str_location))]
        if str_location2:
            locations.append(int(self.env['ir.config_parameter'].sudo().get_param(str_location2)))

        return locations

    def get_report(self, date_from, date_to, locations):
        date_to = date_to + " 23:59:59" if date_to else date_to

        str_locations = "(" + ",".join([str(x) for x in locations]) + ")"

        query = "SELECT sm.product_id, pt.name, pt.default_code, pt.uom_id, pu.name AS uom_name, " \
                "COALESCE(penyesuaian, 0) AS penyesuaian, COALESCE(selisih, 0) AS selisih, " \
                "SUM(CASE " \
                "    WHEN sm.location_dest_id = sm.location_id AND sm.date < '{date_from}' THEN 0 " \
                "    WHEN sm.location_dest_id in {locations} AND sm.date < '{date_from}' THEN sm.product_uom_qty " \
                "    WHEN sm.location_id in {locations} AND sm.date < '{date_from}' THEN sm.product_uom_qty * -1 " \
                "	ELSE 0 END) AS saldo_awal, " \
                "SUM(CASE " \
                "    WHEN sm.location_dest_id = sm.location_id AND sm.date < '{date_to}' THEN 0 " \
                "    WHEN sm.location_dest_id in {locations} AND sm.date < '{date_to}' THEN sm.product_uom_qty " \
                "    WHEN sm.location_id in {locations} AND sm.date < '{date_to}' THEN sm.product_uom_qty * -1 " \
                "	ELSE 0 END) AS saldo_akhir, " \
                "SUM(CASE " \
                "    WHEN sm.location_dest_id in {locations} AND sm.date >= '{date_from}' AND sm.date <= '{date_to}' "\
                "    AND sm.inventory_id IS NULL " \
                "    THEN sm.product_uom_qty  " \
                "	ELSE 0 END) AS pemasukan, " \
                "SUM(CASE " \
                "    WHEN sm.location_id in {locations} AND sm.date >= '{date_from}' AND sm.date <= '{date_to}' " \
                "    AND sm.inventory_id IS NULL" \
                "    THEN sm.product_uom_qty  " \
                "	ELSE 0 END) AS pengeluaran, " \
                "COALESCE((SELECT sil.product_qty  " \
                "		 FROM stock_inventory_line sil " \
                "		 LEFT JOIN stock_inventory si ON si.id = sil.inventory_id " \
                "		 WHERE si.date >= '{date_from}'  " \
                "		     AND si.date <= '{date_to}'  " \
                "		     AND si.state = 'done' " \
                "		     AND sil.product_id = sm.product_id " \
                "		     AND sil.location_id in {locations} " \
                "		 ORDER By si.date DESC LIMIT 1), 0) AS stock_opname " \
                "FROM stock_move sm  " \
                "LEFT JOIN product_product pp ON pp.id = sm.product_id  " \
                "LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id  " \
                "LEFT JOIN product_uom pu ON pu.id = pt.uom_id  " \
                "LEFT JOIN (SELECT sil.product_id, " \
                "           SUM(sil.product_qty - sil.theoretical_qty) AS penyesuaian, " \
                "           SUM(ABS(sil.product_qty - sil.theoretical_qty)) AS selisih " \
                "           FROM stock_inventory_line sil " \
                "           LEFT JOIN stock_inventory si ON si.id = sil.inventory_id " \
                "		   WHERE si.date >= '{date_from}'  " \
                "		       AND si.date <= '{date_to}'  " \
                "		       AND si.state = 'done' " \
                "		       AND sil.location_id in {locations} " \
                "           GROUP BY sil.product_id " \
                "           ) sto ON sto.product_id = sm.product_id  " \
                "WHERE (sm.location_id in {locations} OR sm.location_dest_id in {locations})  " \
                "    AND state = 'done' " \
                "GROUP BY sm.product_id, pt.name, pu.name, " \
                "stock_opname, penyesuaian, selisih, pt.default_code, pt.uom_id".format(locations=str_locations,
                                                                                        date_from=date_from,
                                                                                        date_to=date_to
                                                                                        )
        self._cr.execute(query)
        res = []
        for x in self._cr.dictfetchall():
            if x['penyesuaian'] == 0:
                x['keterangan'] = 'Sesuai'
            elif x['penyesuaian'] < 0:
                x['keterangan'] = 'Selisih Kurang'
            else:
                x['keterangan'] = 'Selisih Lebih'

            res.append(x)
        return res

    @api.multi
    def generate_preview(self):
        self.ensure_one()
        ctx = dict(self._context)
        mutasi_ids = self.env['laporan.pertanggungjawaban']
        locations = self.get_location()

        for res in self:
            for x in self.get_report(res.date_from, res.date_to, locations):
                mutasi_ids |= self.env['laporan.pertanggungjawaban'].create({
                    'product_id': x['product_id'],
                    'product_code': x['name'],
                    'uom_id': x['uom_id'],
                    'saldo_awal': x['saldo_awal'],
                    'pemasukan': x['pemasukan'],
                    'pengeluaran': x['pengeluaran'],
                    'penyesuaian': x['penyesuaian'],
                    'saldo_akhir': x['saldo_akhir'],
                    'stock_opname': x['stock_opname'],
                    'selisih': x['selisih'],
                    'keterangan': x['keterangan'],
                    'location_ids': ",".join([str(x) for x in locations]),
                    'date_from': res.date_from,
                    'date_to': res.date_to
                })

        if mutasi_ids:
            display_name = ctx.get('title', '')
            action_xmlid = ctx.get('action_xmlid', 'v10_bsc_beacukai.action_laporan_pertanggungjawaban_mutasi')
            action = self.env['ir.model.data'].xmlid_to_object(action_xmlid)
            action = action[0].read()[0]
            action['domain'] = [('id', 'in', mutasi_ids.ids)]
            action['name'] = _('Laporan Mutasi Per ' +
                               str(self.date_from) + ' - ' + str(self.date_to))
            action['display_name'] = display_name
            action['target'] = 'main'
            action['context'] = ctx
            return action
        else:
            raise Warning('Data Tidak Ditemukan')

    @api.multi
    def preview_pdf(self):
        data = {'form': self.read(['date_from', 'date_to'])[0]}
        return self._print_report(data)

    def _print_report(self, data):
        ctx = dict(self._context)

        data['ctx'] = ctx
        data['locations'] = self.get_location()
        data['form'].update(self.read(['date_from', 'date_to'])[0])
        action = self.env['report'].get_action(self, 'v10_bsc_beacukai.report_pertanggungjawaban_mutasi', data=data)
        action['name'] = ctx.get('title', '')
        action['target'] = 'main'
        return action

    def get_styles(self, workbook):
        style = {}
        #################################################################################
        center_title = workbook.add_format(
            {'bold': 1, 'valign': 'vcenter', 'align': 'center'})
        center_title.set_font_size('13')
        center_title.set_bg_color('#eff0f2')
        center_title.set_border()
        style['center_title'] = center_title
        #################################################################################
        left_title = workbook.add_format(
            {'bold': 1, 'valign': 'vcenter', 'align': 'left'})
        left_title.set_font_size('13')
        left_title.set_bg_color('#eff0f2')
        left_title.set_border()
        style['left_title'] = left_title
        #################################################################################
        bold_font = workbook.add_format(
            {'bold': 1, 'valign': 'vcenter', 'align': 'left'})
        bold_font.set_text_wrap()
        style['bold_font'] = bold_font
        #################################################################################
        header_table = workbook.add_format(
            {'bold': 1, 'valign': 'vcenter', 'align': 'center'})
        header_table.set_text_wrap()
        header_table.set_bg_color('#eff0f2')
        header_table.set_border()
        style['header_table'] = header_table
        #################################################################################
        footer_table = workbook.add_format(
            {'bold': 1, 'valign': 'vcenter', 'align': 'right'})
        footer_table.set_text_wrap()
        footer_table.set_border()
        style['footer_table'] = footer_table
        #################################################################################
        set_right = workbook.add_format(
            {'valign': 'vcenter', 'align': 'right'})
        set_right.set_text_wrap()
        set_right.set_border()
        style['set_right'] = set_right
        #################################################################################
        set_center = workbook.add_format(
            {'valign': 'vcenter', 'align': 'center'})
        set_center.set_text_wrap()
        set_center.set_border()
        style['set_center'] = set_center
        #################################################################################
        set_border = workbook.add_format(
            {'valign': 'vcenter', 'align': 'left'})
        set_border.set_text_wrap()
        set_border.set_border()
        style['set_border'] = set_border

        return style

    def set_content(self, workbook, sheet, report_name, content_datas):
        style = self.get_styles(workbook)

        col_sizes = [5, 20, 70, 10, 15, 15, 15, 15, 15, 15, 15, 15]
        for col, size in enumerate(col_sizes):
            sheet.set_column(col, col, size)

        sheet.set_row(1, 20)
        sheet.set_row(2, 20)
        sheet.set_row(3, 20)
        sheet.set_row(6, 20)
        sheet.set_row(7, 20)

        bc_type = self.env['ir.config_parameter'].sudo().get_param('bc_type')
        if bc_type == 0:
            kbgb = "Kawasan Berikat"
        else:
            kbgb = "Gudang Berikat"

        sheet.merge_range(
            'A2:L2', report_name, style['left_title'])
        sheet.merge_range('A3:L3', kbgb + ' ' + self.env.user.company_id.name, style['left_title'])
        sheet.merge_range('A4:L4', 'Periode: ' + datetime.strptime(self.date_from, '%Y-%m-%d').strftime(
            '%d %m %Y') + ' s.d ' + datetime.strptime(self.date_to, '%Y-%m-%d').strftime('%d %m %Y'), style['left_title'])

        row = 7
        if report_name == 'Laporan Posisi WIP':
            signature_position = 4
            sheet.merge_range(6, 0, 7, 0, 'No', style['header_table'])
            sheet.merge_range(6, 1, 7, 1, 'Kode Barang', style['header_table'])
            sheet.merge_range(6, 2, 7, 2, 'Nama Barang', style['header_table'])
            sheet.merge_range(6, 3, 7, 3, 'Satuan', style['header_table'])
            sheet.merge_range(6, 4, 7, 4, 'Jumlah', style['header_table'])

            for nomor, x in enumerate(content_datas, start=1):
                row += 1
                sheet.write(row, 0, nomor, style['set_center'])
                sheet.write(row, 1, x['name'], style['set_border'])
                sheet.write(row, 2, x['default_code'], style['set_border'])
                sheet.write(row, 3, x['uom_name'], style['set_center'])
                sheet.write(row, 4, x['saldo_akhir'], style['set_right'])
        else:
            signature_position = 8
            sheet.merge_range(6, 0, 7, 0, 'No', style['header_table'])
            sheet.merge_range(6, 1, 7, 1, 'Kode Barang', style['header_table'])
            sheet.merge_range(6, 2, 7, 2, 'Nama Barang', style['header_table'])
            sheet.merge_range(6, 3, 7, 3, 'Satuan', style['header_table'])
            sheet.merge_range(6, 4, 7, 4, 'Saldo Awal', style['header_table'])
            sheet.merge_range(6, 5, 7, 5, 'Pemasukan', style['header_table'])
            sheet.merge_range(6, 6, 7, 6, 'Pengeluaran', style['header_table'])
            sheet.merge_range(6, 7, 7, 7, 'Penyesuaian', style['header_table'])
            sheet.merge_range(6, 8, 7, 8, 'Saldo Buku/Akhir', style['header_table'])
            sheet.merge_range(6, 9, 7, 9, 'Stock Opname', style['header_table'])
            sheet.merge_range(6, 10, 7, 10, 'Selisih', style['header_table'])
            sheet.merge_range(6, 11, 7, 11, 'Keterangan', style['header_table'])

            for nomor, x in enumerate(content_datas, start=1):
                row += 1
                sheet.write(row, 0, nomor, style['set_center'])
                sheet.write(row, 1, x['name'], style['set_border'])
                sheet.write(row, 2, x['default_code'], style['set_border'])
                sheet.write(row, 3, x['uom_name'], style['set_center'])
                sheet.write(row, 4, x['saldo_awal'], style['set_right'])
                sheet.write(row, 5, x['pemasukan'], style['set_right'])
                sheet.write(row, 6, x['pengeluaran'], style['set_right'])
                sheet.write(row, 7, x['penyesuaian'], style['set_right'])
                sheet.write(row, 8, x['saldo_akhir'], style['set_right'])
                sheet.write(row, 9, x['stock_opname'], style['set_right'])
                sheet.write(row, 10, x['selisih'], style['set_right'])
                sheet.write(row, 11, x['keterangan'], style['set_right'])

        sheet.write(row + 3, signature_position, 'KAMI BERTANGGUNG JAWAB')
        sheet.write(row + 4, signature_position, 'ATAS KEBENARAN LAPORAN INI')
        sheet.write(row + 5, signature_position, str(self.env.user.company_id.city).upper() +
                         ', ' + datetime.today().strftime('%d %m %Y'))
        sheet.write(row + 6, signature_position, 'PENGUSAHA DI ' + str(kbgb).upper())
        pengusaha = self.env['beacukai.apiu'].search([], limit=1)
        sheet.write(row + 10, signature_position, str(pengusaha.name).upper())
        sheet.write(row + 11, signature_position, str(pengusaha.jabatan).upper())


    @api.multi
    def generate_report(self):
        ctx = dict(self._context)
        report_name = ctx.get('title', '')
        locations = self.get_location()
        filename = '%s.xlsx' % report_name

        fp = StringIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet1 = workbook.add_worksheet('All Account')

        content_datas = self.get_report(self.date_from, self.date_to, locations)
        self.set_content(workbook, worksheet1, report_name, content_datas)
        workbook.close()
        out = base64.encodestring(fp.getvalue())
        self.write({'data': out, 'name': filename, 'state_position': 'get'})
        fp.close()
        ir_model_data = self.env['ir.model.data']
        form_res = ir_model_data.get_object_reference(
            'v10_bsc_beacukai', 'excel_laporan_mutasi_form')
        form_id = form_res and form_res[1] or False
        return {
            'name': ('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'excel.laporan.mutasi',
            'res_id': self.id,
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'main'
        }
