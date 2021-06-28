# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
# from cStringIO import StringIO
import base64
import xlsxwriter
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning
import logging

_logger = logging.getLogger(__name__)


class ReportBahanbaku(models.AbstractModel):
    _name = 'report.v12_bsc_beacukai.report_bahanbaku'

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
        sales_records = []

        location_id = int(self.env['ir.config_parameter'].sudo(
        ).get_param('location_bahanbakupenolong'))

        move_line_ids = self.env['stock.move'].search([
            ('date', '<=', docs.date_to),
            ('state', '=', 'done'),
            '|', ('location_id', '=',
                  location_id), ('location_dest_id', '=', location_id)
        ])

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'product': move_line_ids,
            'header': self.env['beacukai.apiu'].search([], limit=1)
        }
        return self.env['report'].render('v12_bsc_beacukai.report_bahanbaku', docargs)

# class ReportLaporanBahanBakuPenolong(models.Model):
#     _name = "bahan.baku.report"
#     _auto = False

#     attendee_id = fields.Many2one(comodel_name='event.registration', string='Registration')
#     question_id = fields.Many2one(comodel_name='event.question', string='Question')
#     answer_id = fields.Many2one(comodel_name='event.answer', string='Answer')
#     event_id = fields.Many2one(comodel_name='event.event', string='Event')

#     @api.model_cr
#     def init(self):
#         """ Event Question main report """
#         tools.drop_view_if_exists(self._cr, 'bahan_baku_report')
#         self._cr.execute(""" CREATE VIEW bahan_baku_report AS (
#             SELECT MIN(id) as id,
#                 move_id,
#                 location_id,
#                 company_id,
#                 product_id,
#                 product_categ_id,
#                 product_template_id,
#                 SUM(quantity * CASE )  as saldo_awal,
#                 SUM(quantity) as quantity,
#                 date,
#                 COALESCE(SUM(price_unit_on_quant * quantity) / NULLIF(SUM(quantity), 0), 0) as price_unit_on_quant,
#                 source,
#                 string_agg(DISTINCT serial_number, ', ' ORDER BY serial_number) AS serial_number
#                 FROM
#                 ((SELECT
#                     stock_move.id AS id,
#                     stock_move.id AS move_id,
#                     dest_location.id AS location_id,
#                     dest_location.company_id AS company_id,
#                     stock_move.product_id AS product_id,
#                     product_template.id AS product_template_id,
#                     product_template.categ_id AS product_categ_id,
#                     quant.qty AS quantity,
#                     stock_move.date AS date,
#                     quant.cost as price_unit_on_quant,
#                     stock_move.origin AS source,
#                     stock_production_lot.name AS serial_number
#                 FROM
#                     stock_quant as quant
#                 JOIN
#                     stock_quant_move_rel ON stock_quant_move_rel.quant_id = quant.id
#                 JOIN
#                     stock_move ON stock_move.id = stock_quant_move_rel.move_id
#                 LEFT JOIN
#                     stock_production_lot ON stock_production_lot.id = quant.lot_id
#                 JOIN
#                     stock_location dest_location ON stock_move.location_dest_id = dest_location.id
#                 JOIN
#                     stock_location source_location ON stock_move.location_id = source_location.id
#                 JOIN
#                     product_product ON product_product.id = stock_move.product_id
#                 JOIN
#                     product_template ON product_template.id = product_product.product_tmpl_id
#                 WHERE quant.qty>0 AND stock_move.state = 'done' AND dest_location.usage in ('internal', 'transit')
#                 AND (
#                     not (source_location.company_id is null and dest_location.company_id is null) or
#                     source_location.company_id != dest_location.company_id or
#                     source_location.usage not in ('internal', 'transit'))
#                 ) UNION ALL
#                 (SELECT
#                     (-1) * stock_move.id AS id,
#                     stock_move.id AS move_id,
#                     source_location.id AS location_id,
#                     source_location.company_id AS company_id,
#                     stock_move.product_id AS product_id,
#                     product_template.id AS product_template_id,
#                     product_template.categ_id AS product_categ_id,
#                     - quant.qty AS quantity,
#                     stock_move.date AS date,
#                     quant.cost as price_unit_on_quant,
#                     stock_move.origin AS source,
#                     stock_production_lot.name AS serial_number
#                 FROM
#                     stock_quant as quant
#                 JOIN
#                     stock_quant_move_rel ON stock_quant_move_rel.quant_id = quant.id
#                 JOIN
#                     stock_move ON stock_move.id = stock_quant_move_rel.move_id
#                 LEFT JOIN
#                     stock_production_lot ON stock_production_lot.id = quant.lot_id
#                 JOIN
#                     stock_location source_location ON stock_move.location_id = source_location.id
#                 JOIN
#                     stock_location dest_location ON stock_move.location_dest_id = dest_location.id
#                 JOIN
#                     product_product ON product_product.id = stock_move.product_id
#                 JOIN
#                     product_template ON product_template.id = product_product.product_tmpl_id
#                 WHERE quant.qty>0 AND stock_move.state = 'done' AND source_location.usage in ('internal', 'transit')
#                 AND (
#                     not (dest_location.company_id is null and source_location.company_id is null) or
#                     dest_location.company_id != source_location.company_id or
#                     dest_location.usage not in ('internal', 'transit'))
#                 ))
#                 AS foo
#                 GROUP BY move_id, location_id, company_id, product_id, product_categ_id, date, source, product_template_id
#             )""")


class ExcelLaporanPertanggungjawabanBahanBaku(models.TransientModel):
    _name = 'excel.laporan.pertanggungjawaban.bahan.baku'

    @api.multi
    def open_table(self):
        self.ensure_one()
        ctx = dict(
            self._context,
            date_to=self.date_to,
            date_from=self.date_from,
            group_by="product_id")

        action = self.env['ir.model.data'].xmlid_to_object(
            'v12_bsc_beacukai.action_laporan_mutasi')
        #action = self.env['ir.model.data'].xmlid_to_object('v12_bsc_beacukai.action_laporan_mutasi_bahan_baku')
        if not action:
            action = {
                'view_type': 'form',
                'view_mode': 'tree,graph,pivot',
                'res_model': 'laporan.mutasi',
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

        action['domain'] = "[('report_name','=','" + "Name" + "')]"
        action['name'] = _('Laporan Pertanggungjawaban Per ' +
                           str(self.date_from) + ' - ' + str(self.date_to))
        action['context'] = ctx
        return action

        # loc = self.env['ir.config_parameter'].sudo().get_param('location_bahanbakupenolong')
        # location_id = self.env['stock.location'].browse(loc)

        # action['domain'] = "[('date', '>=', '" + self.date_from + "'),('date', '<=', '" + self.date_to + "'),'|',('location_id', '=', " + loc + "),('location_dest_id', '=', " + loc + ")]"
        # action['name'] = _('Laporan Pertanggungjawaban Bahan Baku')
        # action['context'] = ctx
        # return action

    def get_move_line(self, id_product):
        product = self.env['product.product'].browse(id_product)
        loc = int(self.env['ir.config_parameter'].sudo(
        ).get_param('location_bahanbakupenolong'))
        location_id = self.env['stock.location'].browse(loc)
        move_line_ids = self.env['stock.move'].search([
            ('date', '<=', self.date_to),
            ('state', '=', 'done'),
            '|', ('location_id', '=',
                  location_id.id), ('location_dest_id', '=', location_id.id)
        ])
        awalan = masukan = keluaran = penyesuaian = saldo_akhir = stock_opname = selisih = 0
        keterangan = ''
        for product in move_line_ids.mapped('product_id'):
            inventory_ids = self.env['stock.inventory.line'].search([
                ('product_id', '=', product.id),
                ('inventory_location_id', '=', location_id.id),
                ('inventory_id.date', '>=', self.date_from),
                ('inventory_id.date', '<=', self.date_to)
            ])
            adjustment_ids = self.env['stock.move'].search([
                # ('state','=','done'),
                # ('date', '>=',
                #  res.date_from),
                # ('date', '<=',
                #  res.date_to),
                ('product_id','=',product.id),
                ('location_id.name','ilike','%Inventory adjustment%')
                ])
            incoming_ids = self.env['stock.move'].search([
                ('state', '=', 'done'),
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('product_id','=',product.id),
                ('location_dest_id', '=', location_id.id),
                ('picking_id.is_beacukai_incoming_23', '=', True)
                ])
            # print "Incoming IDS ", incoming_ids
            outgoing_ids = self.env['stock.move'].search([
                ('state','=','done'),
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('product_id','=',product.id),
                ('location_id', '=', location_id.id),
                ('location_dest_id','!=',location_id.id)
                # ('picking_id','ilike','BC/OUT%')
            ])

            if inventory_ids:
                for inventory in inventory_ids:
                    stock_opname = inventory.product_qty

            for move_line in move_line_ids:
                _logger.info(move_line)
            #     if move_line.location_id == location_id and move_line.product_id.id == product.id and move_line.date < self.date_from:
            #         saldo_awal -= move_line.product_uom_qty
                if stock_opname:
                    awalan = inventory.product_qty
                else:
                    if move_line.location_dest_id == location_id and move_line.product_id.id == product.id and move_line.date < self.date_from:
                        awalan += move_line.product_uom_qty
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

            # for adjust in adjustment_ids:
                # if product.product_id.id == adjust.product_id.id:
                #     mutasi_id.write({'saldo_awal': product.product_uom_qty})
                #     awalan = product.product_uom_qty
                # else:
                #     mutasi_id.write({'saldo_awal': 0})
                #     awalan = 0
                # awalan = adjust.product_uom_qty
            for masuk in incoming_ids:
                # if product.product_id.id == masuk.product_id.id:
                #     mutasi_id.write({'pemasukan': product.product_uom_qty})
                #     masukan = product.product_uom_qty
                # else:
                #     mutasi_id.write({'pemasukan': 0})
                #     masukan = 0
                masukan += masuk.product_uom_qty
            for keluar in outgoing_ids:
                # if product.product_id.id == keluar.product_id.id:
                #     mutasi_id.write({'pengeluaran': product.product_uom_qty})
                #     keluaran = product.product_uom_qty
                # else:
                #     mutasi_id.write({'pengeluaran': 0})
                #     keluaran = 0
                keluaran += keluar.product_uom_qty
            saldo_akhir = awalan + masukan - keluaran + penyesuaian
            _logger.info('location_id')
            _logger.info(location_id)
            # _logger.info(pengeluaran)
            _logger.info(penyesuaian)
            _logger.info(stock_opname)
            selisih = abs(saldo_akhir - stock_opname)
            if selisih == 0:
                keterangan = "Sesuai"
            else:
                keterangan = "Tidak Sesuai"
            res = {
                'saldo_awal': awalan,
                'pemasukan': masukan,
                'pengeluaran': keluaran,
                'penyesuaian': penyesuaian,
                'saldo_akhir': saldo_akhir,
                'stock_opname': stock_opname,
                'selisih': selisih,
                'keterangan': keterangan,
            }
            _logger.info(res)
            _logger.info(res['saldo_awal'])
            return res

    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date', default=fields.Date.today())
    state_position = fields.Selection(
        [('choose', 'choose'), ('get', 'get')], default='choose')
    #location_id = fields.Many2one('stock.location', string="Location", domain="[('usage','=','internal')]")
    location_id = fields.Many2one('stock.location', 'Location')
    data = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)

    @api.multi
    def generate_preview(self):
        self.ensure_one()
        mutasi_ids = []

        loc = int(self.env['ir.config_parameter'].sudo().get_param('location_bahanbakupenolong'))
        location_id = self.env['stock.location'].browse(loc)

        for res in self:
            moveline_ids = self.env['stock.move'].search([
                ('state', '=', 'done'),
                ('date', '>=', res.date_from),
                ('date', '<=', res.date_to),
                '|', ('location_id', '=', location_id.id),
                ('location_dest_id', '=', location_id.id)
            ])
            if moveline_ids:
                report_name = "Laporan Pertanggungjawaban " + " , " + res.date_from + " - " + res.date_to
                current_report_ids = self.env['laporan.mutasi'].search(
                    [('report_name', '=', report_name)])
                # print(
                #     "============================3============================current_report_ids : ", current_report_ids)
                if current_report_ids:
                    for current_report_id in current_report_ids:
                        current_report_id.unlink()

                for product in moveline_ids.mapped('product_id'):
                    mutasi_id = self.env['laporan.mutasi'].create({
                        'name': report_name,
                        'report_name': report_name,
                        'product_code': product.default_code,
                        'product_id': product.id,
                        'uom_id': product.uom_id.id,
                    })
                    # print(
                    #     "=================================4======================================mutasi_ids : ", mutasi_id)
                    mutasi_ids.append(mutasi_id)

                    awalan = masukan = keluaran = penyesuaian = stock_opname = 0

                    inventory_ids = self.env['stock.inventory.line'].search([
                        ('product_id', '=', product.id),
                        ('inventory_location_id', '=', location_id.id),
                        ('inventory_id.date', '>=', res.date_from),
                        ('inventory_id.date', '<=', res.date_to)
                    ])
                    adjustment_ids = self.env['stock.move'].search([
                        # ('state','=','done'),
                        # ('date', '>=',
                        #  res.date_from),
                        # ('date', '<=',
                        #  res.date_to),
                        ('product_id','=',product.id),
                        ('location_id.name','ilike','%Inventory adjustment%')
                        ])
                    incoming_ids = self.env['stock.move'].search([
                        ('state', '=', 'done'),
                        ('date', '>=',
                         res.date_from),
                        ('date', '<=',
                         res.date_to),
                        ('product_id','=',product.id),
                        ('location_dest_id', '=', location_id.id),
                        ('picking_id.is_beacukai_incoming_23','=',True)
                        ])
                    outgoing_ids = self.env['stock.move'].search([
                        ('state','=','done'),
                        ('date', '>=',
                         res.date_from),
                        ('date', '<=',
                         res.date_to),
                        ('product_id','=',product.id),
                        ('location_id', '=', location_id.id),
                        ('location_dest_id','!=',location_id.id)
                    ])

                    # if inventory_ids:
                    for inventory in inventory_ids:
                        stock_opname = inventory.product_qty

                    # if product.active:
                    for move_line in moveline_ids:

                        if stock_opname:
                            awalan = inventory.product_qty
                        else:
                            if move_line.location_dest_id.id == location_id.id and move_line.product_id.id == product.id and move_line.date_expected < self.date_from:
                                awalan += move_line.product_uom_qty
                                # print("================================6=2=============================saldo_awal : ",saldo_awal)
                                move_line.write({'mutasi_id': mutasi_id.id, 'tipe_mutasi': 'Saldo Awal'})
                    for masuk in incoming_ids:
                        masukan += masuk.product_uom_qty
                    for keluar in outgoing_ids:
                        keluaran += keluar.product_uom_qty

                    saldo_akhir = awalan + masukan - keluaran + penyesuaian
                    selisih = abs(saldo_akhir - stock_opname)
                    if selisih == 0:
                        keterangan = "Sesuai"
                    else:
                        keterangan = "Tidak Sesuai"

                    mutasi_id.write({
                        'saldo_awal': awalan,
                        'pemasukan': masukan,
                        'pengeluaran': keluaran,
                        'penyesuaian': penyesuaian,
                        'saldo_akhir': saldo_akhir,
                        'stock_opname': stock_opname,
                        'selisih': selisih,
                        'keterangan': keterangan,
                    })

        if mutasi_ids:
            ctx = dict(
                self._context)

            #action = self.env['ir.model.data'].xmlid_to_object('v12_bsc_beacukai.action_laporan_mutasi')
            action = self.env['ir.model.data'].xmlid_to_object(
                'v12_bsc_beacukai.action_laporan_mutasi_bahan_baku')
            if not action:
                action = {
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'res_model': 'laporan.mutasi',
                    'type': 'ir.actions.act_window',
                }
            else:
                action = action[0].read()[0]

            action['domain'] = "[('report_name','=','" + report_name + "')]"
            action['name'] = _('Laporan Pertanggungjawaban Per ' +
                               str(self.date_from) + ' - ' + str(self.date_to))
            action['context'] = ctx
            return action
        else:
            raise Warning('Data Tidak Ditemukan')

    @api.multi
    def preview_pdf(self):
        data = {}
        data['form'] = self.read(['date_from', 'date_to'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['date_from', 'date_to'])[0])
        return self.env['report'].get_action(self, 'v12_bsc_beacukai.report_bahanbaku', data=data)

    @api.multi
    def generate_report(self):
        filename = 'Laporan Pertanggungjawaban Mutasi Bahan Baku dan Bahan Penolong.xlsx'

        # fp = StringIO()
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
        left_title.set_font_size('13')
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

        bc_type = self.env['ir.config_parameter'].sudo().get_param('bc_type')
        kbgb = ""
        if bc_type == 0:
            kbgb = "Kawasan Berikat"
        else:
            kbgb = "Gudang Berikat"

        worksheet1.merge_range(
            'A2:L2', 'Laporan Pertanggungjawaban Mutasi Bahan Baku dan Bahan Penolong', left_title)
        worksheet1.merge_range('A3:L3', kbgb+' ' +
                               self.env.user.company_id.name, left_title)
        worksheet1.merge_range('A4:L4', 'Periode: ' + datetime.strptime(self.date_from, '%Y-%m-%d').strftime(
            '%d %m %Y') + ' s.d ' + datetime.strptime(self.date_from, '%Y-%m-%d').strftime('%d %m %Y'), left_title)
        row = 6
        worksheet1.write(row, 0, 'No', header_table)
        worksheet1.write(row, 1, 'Kode Barang', header_table)
        worksheet1.write(row, 2, 'Nama Barang', header_table)
        worksheet1.write(row, 3, 'Satuan', header_table)
        worksheet1.write(row, 4, 'Saldo Awal', header_table)
        worksheet1.write(row, 5, 'Pemasukan', header_table)
        worksheet1.write(row, 6, 'Pengeluaran', header_table)
        worksheet1.write(row, 7, 'Penyesuaian', header_table)
        worksheet1.write(row, 8, 'Saldo Buku/Akhir', header_table)
        worksheet1.write(row, 9, 'Stock Opname', header_table)
        worksheet1.write(row, 10, 'Selisih', header_table)
        worksheet1.write(row, 11, 'Keterangan', header_table)

        i = 0
        # location_ids = self.env['beacukai.config'].search([
        #     ('kode','=','Bahan Baku dan Bahan Penolong')
        #     ])

        # if not location_ids:
        #     raise UserError(_('Belum tersedia pengaturan lokasi untuk Laporan ini'))

        loc = int(self.env['ir.config_parameter'].sudo(
        ).get_param('location_bahanbakupenolong'))
        location_id = self.env['stock.location'].browse(loc)

        move_line_ids = self.env['stock.move'].search([
            ('date', '<=', self.date_to),
            ('state', '=', 'done'),
            '|', ('location_id', '=',location_id.id), 
            ('location_dest_id', '=', location_id.id)
        ])

        # adjustment_ids = move_line_ids.search([
        #     ('location_id.name','ilike','Inventory adjustment')
        # ])

        # incoming_ids = move_line_ids.search([
        #     ('location_dest_id', '=', location_id.id),
        #     ('picking_id','ilike','BC/IN%')
        # ])

        # outgoing_ids = move_line_ids.search([
        #     ('location_id', '=', location_id.id),
        #     ('location_dest_id','!=',location_id.id)
        #     # ('picking_id','ilike','BC/OUT%')
        # ])

        # saldo_awal = pemasukan = pengeluaran = penyesuaian = saldo_akhir = stock_opname = selisih = 0
        # keterangan = ''

        if move_line_ids:
            for product in move_line_ids.mapped('product_id'):
                awalan = masukan = keluaran = penyesuaian = saldo_akhir = stock_opname = selisih = 0
                keterangan = ''
                row += 1
                i += 1

                inventory_ids = self.env['stock.inventory.line'].search([
                    ('product_id', '=', product.id),
                    ('inventory_location_id', '=', location_id.id),
                    ('inventory_id.date', '>=', self.date_from),
                    ('inventory_id.date', '<=', self.date_to)
                ])
                adjustment_ids = self.env['stock.move'].search([
                        # ('state','=','done'),
                        # ('date', '>=',
                        #  res.date_from),
                        # ('date', '<=',
                        #  res.date_to),
                        ('product_id','=',product.id),
                        ('location_id.name','ilike','%Inventory adjustment%')
                        ])
                incoming_ids = self.env['stock.move'].search([
                    ('state', '=', 'done'),
                    ('date', '>=',
                     self.date_from),
                    ('date', '<=',
                     self.date_to),
                    ('product_id','=',product.id),
                    ('location_dest_id', '=', location_id.id),
                    ('picking_id.beacukai_incoming_id','!=',False)
                    ])
                outgoing_ids = self.env['stock.move'].search([
                    ('state','=','done'),
                    ('date', '>=',
                     self.date_from),
                    ('date', '<=',
                     self.date_to),
                    ('product_id','=',product.id),
                    ('location_id', '=', location_id.id),
                    ('location_dest_id','!=',location_id.id)
                    # ('picking_id','ilike','BC/OUT%')
                ])
                if inventory_ids:
                    for inventory in inventory_ids:
                        stock_opname = inventory.product_qty

                # if product.active:
                worksheet1.write(row, 0, i, set_center)
                worksheet1.write(row, 1, product.default_code, set_border)
                worksheet1.write(row, 2, product.name, set_border)
                worksheet1.write(row, 3, product.uom_id.name, set_center)

                for move_line in move_line_ids:
                    # if move_line.location_id == location_id and move_line.product_id.id == product.id and move_line.date < self.date_from:
                    #     saldo_awal -= move_line.product_uom_qty
                    if stock_opname:
                        awalan = inventory.product_qty
                        worksheet1.write(row, 4, awalan, set_right)
                    else:
                        if move_line.location_dest_id == location_id and move_line.product_id.id == product.id and move_line.date < self.date_from:
                            awalan += move_line.product_uom_qty
                            worksheet1.write(row, 4, awalan, set_right)
                        else:
                            worksheet1.write(row, 4, awalan, set_right)
                    # elif move_line.location_id == location_id and move_line.product_id.id == product.id and move_line.date >= self.date_from:
                    #     if move_line.location_dest_id.usage == "inventory":
                    #         penyesuaian -= move_line.product_uom_qty
                    #     else:
                    #         pengeluaran += move_line.product_uom_qty
                    # elif move_line.location_dest_id == location_id and move_line.product_id.id == product.id and move_line.date >= self.date_from:
                    #     if move_line.location_id.usage == "inventory":
                    #         penyesuaian += move_line.product_uom_qty
                    #     else:
                    #         pemasukan += move_line.product_uom_qty
                # for adjust in adjustment_ids:
                    # if product.product_id.id == adjust.product_id.id:
                    #     # mutasi_id.write({'saldo_awal': product.product_uom_qty})
                    #     worksheet1.write(row, 4, product.product_uom_qty, set_right)
                    #     awalan = adjust.product_uom_qty
                    # else:
                    #     # mutasi_id.write({'saldo_awal': 0})
                    #     worksheet1.write(row, 4, 0, set_right)
                    #     awalan = 0
                    # worksheet1.write(row, 4, product.product_uom_qty, set_right)
                    # awalan = adjust.product_uom_qty
                # worksheet1.write(row, 4, awalan, set_right)
                for masuk in incoming_ids:
                    # if product.product_id.id == masuk.product_id.id:
                    #     # mutasi_id.write({'pemasukan': product.product_uom_qty})
                    #     worksheet1.write(row, 5, product.product_uom_qty, set_right)
                    #     masukan = masuk.product_uom_qty
                    # else:
                    #     # mutasi_id.write({'pemasukan': 0})
                    #     worksheet1.write(row, 5, 0, set_right)
                    #     masukan = 0
                    # worksheet1.write(row, 5, product.product_uom_qty, set_right)
                    masukan += masuk.product_uom_qty
                worksheet1.write(row, 5, masukan, set_right)
                for keluar in outgoing_ids:
                    # if product.product_id.id == keluar.product_id.id:
                    #     # mutasi_id.write({'pengeluaran': product.product_uom_qty})
                    #     worksheet1.write(row, 6, product.product_uom_qty, set_right)
                    #     keluaran = keluar.product_uom_qty
                    # else:
                    #     # mutasi_id.write({'pengeluaran': 0})
                    #     worksheet1.write(row, 6, 0, set_right)
                    #     keluaran = 0
                    # worksheet1.write(row, 6, product.product_uom_qty, set_right)
                    keluaran += keluar.product_uom_qty
                worksheet1.write(row, 6, keluaran, set_right)
                saldo_akhir = awalan + masukan - keluaran + penyesuaian
                selisih = abs(saldo_akhir - stock_opname)
                if selisih == 0:
                    keterangan = "Sesuai"
                else:
                    keterangan = "Tidak Sesuai"

                # worksheet1.write(row, 4, saldo_awal, set_right)
                # worksheet1.write(row, 5, pemasukan, set_right)
                # worksheet1.write(row, 6, pengeluaran, set_right)
                worksheet1.write(row, 7, penyesuaian, set_right)
                worksheet1.write(row, 8, saldo_akhir, set_right)
                worksheet1.write(row, 9, stock_opname, set_right)
                worksheet1.write(row, 10, selisih, set_right)
                worksheet1.write(row, 11, keterangan, set_right)

        pengusaha = self.env['beacukai.apiu'].search([], limit=1)
        worksheet1.write(row+3, 8, 'KAMI BERTANGGUNG JAWAB')
        worksheet1.write(row+4, 8, 'ATAS KEBENARAN LAPORAN INI')
        worksheet1.write(row+5, 8, str(self.env.user.company_id.city).upper() +
                         ', ' + datetime.today().strftime('%d %m %Y'))
        worksheet1.write(row+6, 8, 'PENGUSAHA DI '+str(kbgb).upper())
        pengusaha = self.env['beacukai.apiu'].search([], limit=1)
        worksheet1.write(row+10, 8, str(pengusaha.name).upper())
        worksheet1.write(row+11, 8, str(pengusaha.jabatan).upper())

        workbook.close()
        out = base64.encodestring(fp.getvalue())
        self.write({'data': out, 'name': filename, 'state_position': 'get'})
        fp.close()
        ir_model_data = self.env['ir.model.data']
        form_res = ir_model_data.get_object_reference(
            'v12_bsc_beacukai', 'excel_laporan_pertanggungjawaban_bahan_baku_form')
        form_id = form_res and form_res[1] or False
        return {
            'name': ('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'excel.laporan.pertanggungjawaban.bahan.baku',
            'res_id': self.id,
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }
