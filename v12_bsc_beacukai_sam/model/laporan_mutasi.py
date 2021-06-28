from odoo import api,fields,models
from odoo.addons import decimal_precision as dp
    

class LaporanMutasiPertanggungJawabanLine(models.TransientModel):
    _name = 'laporan.pertanggungjawaban.line'
    rec_name = 'name'

    @api.depends('submission_no')
    @api.one
    def _get_dok_details(self):
        self.ensure_one()
        types = dict(self.env['stock.picking']._fields['bc_ref_type'].selection)
        for model in types:
            if model in self.env:
                dok = self.env[model].search([('submission_no', '=', self.submission_no)], limit=1)
                if dok:
                    self.document_type = dok.document_type_id.name
                    self.register_number = dok.register_number
                    self.register_date = dok.register_date
                    return

    name = fields.Char('Name')
    move_id = fields.Many2one('stock.move', 'Stock Move')
    mutasi_id = fields.Many2one('laporan.pertanggungjawaban', 'Tipe Document')
    document_type = fields.Char('Tipe Document', compute="_get_dok_details")
    submission_no = fields.Char('Nomor Aju')
    register_number = fields.Char('No. Pendaftaran', compute="_get_dok_details")
    register_date = fields.Char('Tanggal Pendaftaran', compute="_get_dok_details")
    product_qty = fields.Float('Qty', digits=dp.get_precision('Product Unit of Measure'))
    hs_code = fields.Char(related='move_id.product_id.hs_code', string='HS Code')
    product_uom = fields.Many2one('product.uom', related='move_id.product_id.uom_id', string='UoM')
    product_name = fields.Char(related='move_id.product_id.name', string='Kode')
    product_code = fields.Char(related='move_id.product_id.code', string='Nama')
    location_id = fields.Char(related='move_id.location_id.name', string='Source Location')
    location_dest_id = fields.Char(related='move_id.location_dest_id.name', string='Destination Location')
    date = fields.Date(string='Tanggal')


class LaporanMutasiPertanggungJawaban(models.TransientModel):
    _inherit = 'laporan.pertanggungjawaban'

    @api.one
    def _compute_moves(self):
        location_production = self.env.ref('stock.location_production')
        move_obj = self.env['stock.move']
        mrp_obj = self.env['mrp.production']
        histories = move_obj
        new_moves = move_obj

        location_ids = [int(x) for x in self.location_ids.split(',')] if self.location_ids else []

        moves = move_obj.search([
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('state', '=', 'done'),
            ('product_id', '=', self.product_id.id),
            '|', ('location_dest_id', 'in', location_ids),
            ('location_id', 'in', location_ids)
        ])

        if self._context.get('is_brg_jadi', False):
            for move in moves:
                for quant in move.quant_ids:
                    histories |= quant.history_ids
            for move in histories:
                if move.location_id.id == location_production.id:
                    mrp_recs = mrp_obj.search([('name', '=', move.origin)], limit=1)
                    new_moves |= mrp_recs.move_raw_ids
            self.moveline_ids = new_moves
        else:
            self.moveline_ids = moves

    @api.multi
    def _compute_lines(self):
        self.ensure_one()
        res = []
        self.mutasi_line_ids.unlink()

        for move in self.moveline_ids:
            lines = {}
            for quant in move.quant_ids:
                lines[quant.submission_no or ''] = quant.qty + lines.get(quant.submission_no or '', 0)

            for submission_no in lines:
                res.append((0, 0, {
                    'name': move.product_id.display_name,
                    'submission_no': submission_no,
                    'move_id': move.id,
                    'date': move.date,
                    'product_qty': lines[submission_no]
                }))
        self.write({'mutasi_line_ids': res})

    mutasi_line_ids = fields.One2many('laporan.pertanggungjawaban.line', 'mutasi_id', string="Mutasi Lines")


class ExcelLaporanMutasi(models.TransientModel):
    _inherit = 'excel.laporan.mutasi'

    @api.multi
    def generate_preview(self):
        action = super(ExcelLaporanMutasi, self).generate_preview()
        laporan = self.env['laporan.pertanggungjawaban'].search(action['domain'])
        for x in laporan:
            x._compute_lines()

        return action
