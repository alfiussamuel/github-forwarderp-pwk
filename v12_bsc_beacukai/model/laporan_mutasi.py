from odoo import api,fields,models
    

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    mutasi_id = fields.Many2one('laporan.mutasi', string='Laporan Mutasi')
    mutasi_barang_jadi_id = fields.Many2one('laporan.mutasi.barang.jadi', string='Laporan Mutasi Barang Jadi')
    mutasi_mesin_id = fields.Many2one('laporan.mutasi.mesin', string='Laporan Mutasi Mesin')
    mutasi_reject_id = fields.Many2one('laporan.mutasi.reject', string='Laporan Mutasi Reject')
    tipe_mutasi = fields.Char('Tipe Mutasi')


class LaporanMutasiPertanggungJawaban(models.TransientModel):
    _name = 'laporan.pertanggungjawaban'

    @api.one
    def _compute_moves(self):
        self.moveline_ids = self.env['stock.move'].search([
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('state', '=', 'done'),
            ('product_id', '=', self.product_id.id),
            '|', ('location_dest_id', '=', self.location_id),
            ('location_id', '=', self.location_id)
        ])

    date = fields.Date('Tanggal Document')
    document_type_id = fields.Many2one('beacukai.document.type', 'Jenis Dokumen')
    document_number = fields.Char('Document Number')
    name = fields.Char('Document No.')
    report_name = fields.Char('Report Name')
    product_code = fields.Char('Kode Barang')
    product_id = fields.Many2one('product.product', 'Nama Barang')
    uom_id = fields.Many2one('uom.uom', 'Satuan')
    saldo_awal = fields.Float('Saldo Awal')
    pemasukan = fields.Float('Pemasukan')
    pengeluaran = fields.Float('Pengeluaran')
    penyesuaian = fields.Float('Penyesuaian')
    saldo_akhir = fields.Float('Saldo Akhir')
    stock_opname = fields.Float('Stock Opname')
    selisih = fields.Float('Selisih')
    keterangan = fields.Char('Keterangan')
    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
    location_id = fields.Integer('Location ID')
    location_ids = fields.Char('Location IDs')
    moveline_ids = fields.One2many('stock.move', string="Move Lines", compute='_compute_moves')


class LaporanMutasi(models.Model):
    _name = 'laporan.mutasi'


    date = fields.Date('Tanggal Document')
    document_type_id = fields.Many2one('beacukai.document.type', 'Jenis Dokumen')
    document_number = fields.Char('Document Number')
    name = fields.Char('Document No.')
    report_name = fields.Char('Report Name')
    product_code = fields.Char('Kode Barang')
    product_id = fields.Many2one('product.product', 'Nama Barang')
    uom_id = fields.Many2one('uom.uom', 'Satuan')
    saldo_awal = fields.Float('Saldo Awal')
    pemasukan = fields.Float('Pemasukan')
    pengeluaran = fields.Float('Pengeluaran')
    penyesuaian = fields.Float('Penyesuaian')
    saldo_akhir = fields.Float('Saldo Akhir')
    stock_opname = fields.Float('Stock Opname')
    selisih = fields.Float('Selisih')
    keterangan = fields.Char('Keterangan')
    count_lines = fields.Integer(compute='_get_count_lines', string='Total Moves', default=0)
    moveline_ids = fields.One2many('stock.move', 'mutasi_id', string="Move Lines")

    

    reference = fields.Many2one('beacukai.incoming','Reference',compute='_get_count_lines',)
    document_type_id = fields.Many2one('beacukai.document.type','Type',compute='_get_count_lines',)
    no_pendaftaran = fields.Char('No Pendaftaran',compute='_get_count_lines',)
    tgl_daftar = fields.Date('Tanggal Daftar',compute='_get_count_lines',)
    submission_no = fields.Char('No Aju',compute='_get_count_lines',)
    date = fields.Date('Tgl Aju',compute='_get_count_lines',)



    @api.depends('moveline_ids')
    def _get_count_lines(self):
        for res in self:
            if res.moveline_ids:
                res.count_lines = len(res.moveline_ids)

            for each in res.moveline_ids:
                if each.picking_id.beacukai_incoming_id:
                    res.reference = each.picking_id.beacukai_incoming_id.id
                    res.document_type_id = each.picking_id.beacukai_incoming_id.document_type_id.id
                    res.no_pendaftaran = each.picking_id.beacukai_incoming_id.register_number
                    res.tgl_daftar = each.picking_id.beacukai_incoming_id.register_date
                    res.submission_no = each.picking_id.beacukai_incoming_id.submission_no
                    res.date = each.picking_id.beacukai_incoming_id.date

    @api.multi
    def action_view_moves(self):        
        action = self.env.ref('stock.stock_move_action')
        result = action.read()[0]

        #override the context to get rid of the default filtering on picking type
        result.pop('id', None)
        result['context'] = {}
        move_ids = sum([order.moveline_ids.ids for order in self], [])
        #choose the view_mode accordingly
        if len(move_ids) >= 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, move_ids)) + "])]"
        # elif len(move_ids) == 1:
        #     res = self.env.ref('stock.view_move_form', False)
        #     result['views'] = [(res and res.id or False, 'form')]
        #     result['res_id'] = pick_ids and pick_ids[0] or False
        return result


	# @api.model
 #    def create(self, vals):          
 #    	vals['name'] = self.env['ir.sequence'].next_by_code('laporan.mutasi') or 'New'
 #        return super(LaporanMutasi, self).create(vals)

# class LaporanMutasiLine(models.Model):
#     _name = 'laporan.mutasi.line'
    
#     mutasi_id = fields.Many2one('laporan.mutasi', 'Laporan Mutasi')
#     move_id = fields.Many2one('stock.move', 'Move')    



class LaporanMutasiBarangJadi(models.Model):
    _name = 'laporan.mutasi.barang.jadi'


    date = fields.Date('Tanggal Document')
    document_type_id = fields.Many2one('beacukai.document.type', 'Jenis Dokumen')
    document_number = fields.Char('Document Number')
    name = fields.Char('Document No.')
    report_name = fields.Char('Report Name')
    product_code = fields.Char('Kode Barang')
    product_id = fields.Many2one('product.product', 'Nama Barang')
    uom_id = fields.Many2one('uom.uom', 'Satuan')
    saldo_awal = fields.Float('Saldo Awal')
    pemasukan = fields.Float('Pemasukan')
    pengeluaran = fields.Float('Pengeluaran')
    penyesuaian = fields.Float('Penyesuaian')
    saldo_akhir = fields.Float('Saldo Akhir')
    stock_opname = fields.Float('Stock Opname')
    selisih = fields.Float('Selisih')
    keterangan = fields.Char('Keterangan')
    count_lines = fields.Integer(compute='_get_count_lines', string='Total Moves', default=0)
    moveline_ids = fields.One2many('stock.move', 'mutasi_barang_jadi_id', string="Move Lines")

    

    reference = fields.Many2one('beacukai.incoming','Reference',compute='_get_count_lines',)
    document_type_id = fields.Many2one('beacukai.document.type','Type',compute='_get_count_lines',)
    no_pendaftaran = fields.Char('No Pendaftaran',compute='_get_count_lines',)
    tgl_daftar = fields.Date('Tanggal Daftar',compute='_get_count_lines',)
    submission_no = fields.Char('No Aju',compute='_get_count_lines',)
    date = fields.Date('Tgl Aju',compute='_get_count_lines',)



    @api.depends('moveline_ids')
    def _get_count_lines(self):
        for res in self:
            if res.moveline_ids:
                res.count_lines = len(res.moveline_ids)

            
            for each in res.moveline_ids:
                if each.picking_id.beacukai_outgoing_id:
                    res.reference = each.picking_id.beacukai_outgoing_id.id
                    res.document_type_id = each.picking_id.beacukai_outgoing_id.document_type_id.id
                    res.no_pendaftaran = each.picking_id.beacukai_outgoing_id.register_number
                    res.tgl_daftar = each.picking_id.beacukai_outgoing_id.register_date
                    res.submission_no = each.picking_id.beacukai_outgoing_id.submission_no
                    res.date = each.picking_id.beacukai_outgoing_id.date

    @api.multi
    def action_view_moves(self):        
        action = self.env.ref('stock.stock_move_action')
        result = action.read()[0]

        #override the context to get rid of the default filtering on picking type
        result.pop('id', None)
        result['context'] = {}
        move_ids = sum([order.moveline_ids.ids for order in self], [])
        #choose the view_mode accordingly
        if len(move_ids) >= 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, move_ids)) + "])]"
        # elif len(move_ids) == 1:
        #     res = self.env.ref('stock.view_move_form', False)
        #     result['views'] = [(res and res.id or False, 'form')]
        #     result['res_id'] = pick_ids and pick_ids[0] or False
        return result









class LaporanMutasiMesin(models.Model):
    _name = 'laporan.mutasi.mesin'


    date = fields.Date('Tanggal Document')
    document_type_id = fields.Many2one('beacukai.document.type', 'Jenis Dokumen')
    document_number = fields.Char('Document Number')
    name = fields.Char('Document No.')
    report_name = fields.Char('Report Name')
    product_code = fields.Char('Kode Barang')
    product_id = fields.Many2one('product.product', 'Nama Barang')
    uom_id = fields.Many2one('uom.uom', 'Satuan')
    saldo_awal = fields.Float('Saldo Awal')
    pemasukan = fields.Float('Pemasukan')
    pengeluaran = fields.Float('Pengeluaran')
    penyesuaian = fields.Float('Penyesuaian')
    saldo_akhir = fields.Float('Saldo Akhir')
    stock_opname = fields.Float('Stock Opname')
    selisih = fields.Float('Selisih')
    keterangan = fields.Char('Keterangan')
    count_lines = fields.Integer(compute='_get_count_lines', string='Total Moves', default=0)
    moveline_ids = fields.One2many('stock.move', 'mutasi_mesin_id', string="Move Lines")

    

    reference = fields.Many2one('beacukai.incoming','Reference',compute='_get_count_lines',)
    document_type_id = fields.Many2one('beacukai.document.type','Type',compute='_get_count_lines',)
    no_pendaftaran = fields.Char('No Pendaftaran',compute='_get_count_lines',)
    tgl_daftar = fields.Date('Tanggal Daftar',compute='_get_count_lines',)
    submission_no = fields.Char('No Aju',compute='_get_count_lines',)
    date = fields.Date('Tgl Aju',compute='_get_count_lines',)



    @api.depends('moveline_ids')
    def _get_count_lines(self):
        for res in self:
            if res.moveline_ids:
                res.count_lines = len(res.moveline_ids)

            for each in res.moveline_ids:
                if each.picking_id.beacukai_incoming_id:
                    res.reference = each.picking_id.beacukai_incoming_id.id
                    res.document_type_id = each.picking_id.beacukai_incoming_id.document_type_id.id
                    res.no_pendaftaran = each.picking_id.beacukai_incoming_id.register_number
                    res.tgl_daftar = each.picking_id.beacukai_incoming_id.register_date
                    res.submission_no = each.picking_id.beacukai_incoming_id.submission_no
                    res.date = each.picking_id.beacukai_incoming_id.date

    @api.multi
    def action_view_moves(self):        
        action = self.env.ref('stock.stock_move_action')
        result = action.read()[0]

        #override the context to get rid of the default filtering on picking type
        result.pop('id', None)
        result['context'] = {}
        move_ids = sum([order.moveline_ids.ids for order in self], [])
        #choose the view_mode accordingly
        if len(move_ids) >= 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, move_ids)) + "])]"
        # elif len(move_ids) == 1:
        #     res = self.env.ref('stock.view_move_form', False)
        #     result['views'] = [(res and res.id or False, 'form')]
        #     result['res_id'] = pick_ids and pick_ids[0] or False
        return result












class LaporanMutasiReject(models.Model):
    _name = 'laporan.mutasi.reject'


    date = fields.Date('Tanggal Document')
    document_type_id = fields.Many2one('beacukai.document.type', 'Jenis Dokumen')
    document_number = fields.Char('Document Number')
    name = fields.Char('Document No.')
    report_name = fields.Char('Report Name')
    product_code = fields.Char('Kode Barang')
    product_id = fields.Many2one('product.product', 'Nama Barang')
    uom_id = fields.Many2one('uom.uom', 'Satuan')
    saldo_awal = fields.Float('Saldo Awal')
    pemasukan = fields.Float('Pemasukan')
    pengeluaran = fields.Float('Pengeluaran')
    penyesuaian = fields.Float('Penyesuaian')
    saldo_akhir = fields.Float('Saldo Akhir')
    stock_opname = fields.Float('Stock Opname')
    selisih = fields.Float('Selisih')
    keterangan = fields.Char('Keterangan')
    count_lines = fields.Integer(compute='_get_count_lines', string='Total Moves', default=0)
    moveline_ids = fields.One2many('stock.move', 'mutasi_reject_id', string="Move Lines")

    

    reference = fields.Many2one('beacukai.incoming','Reference',compute='_get_count_lines',)
    document_type_id = fields.Many2one('beacukai.document.type','Type',compute='_get_count_lines',)
    no_pendaftaran = fields.Char('No Pendaftaran',compute='_get_count_lines',)
    tgl_daftar = fields.Date('Tanggal Daftar',compute='_get_count_lines',)
    submission_no = fields.Char('No Aju',compute='_get_count_lines',)
    date = fields.Date('Tgl Aju',compute='_get_count_lines',)



    @api.depends('moveline_ids')
    def _get_count_lines(self):
        for res in self:
            if res.moveline_ids:
                res.count_lines = len(res.moveline_ids)

            for each in res.moveline_ids:
                if each.picking_id.beacukai_incoming_id:
                    res.reference = each.picking_id.beacukai_incoming_id.id
                    res.document_type_id = each.picking_id.beacukai_incoming_id.document_type_id.id
                    res.no_pendaftaran = each.picking_id.beacukai_incoming_id.register_number
                    res.tgl_daftar = each.picking_id.beacukai_incoming_id.register_date
                    res.submission_no = each.picking_id.beacukai_incoming_id.submission_no
                    res.date = each.picking_id.beacukai_incoming_id.date

    @api.multi
    def action_view_moves(self):        
        action = self.env.ref('stock.stock_move_action')
        result = action.read()[0]

        #override the context to get rid of the default filtering on picking type
        result.pop('id', None)
        result['context'] = {}
        move_ids = sum([order.moveline_ids.ids for order in self], [])
        #choose the view_mode accordingly
        if len(move_ids) >= 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, move_ids)) + "])]"
        # elif len(move_ids) == 1:
        #     res = self.env.ref('stock.view_move_form', False)
        #     result['views'] = [(res and res.id or False, 'form')]
        #     result['res_id'] = pick_ids and pick_ids[0] or False
        return result











