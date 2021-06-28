from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

LOKASI_PERIKSA = [
('KP Tempat Pemuatan', 'KP Tempat Pemuatan'),
('Gudang Eksportir', 'Gudang Eksportir'),
('Tempat Lain yang Diizinkan', 'Tempat Lain yang Diizinkan'),
('TPS','TPS'),
('TPP','TPP'),
('TPB','TPB')
]

class BeacukaiSuratKeputusan30(models.Model):
    _name = "beacukai.surat.keputusan.30"    

    reference = fields.Many2one('beacukai.outgoing.30', 'Reference')
    name = fields.Char('Nomor Dokumen')
    jenis_dokumen = fields.Char('Jenis Dokumen')
    date = fields.Date('Tanggal')


class BeacukaiContainer30(models.Model):
    _name = "beacukai.container.30"    

    reference = fields.Many2one('beacukai.outgoing.30', 'Reference')
    name = fields.Char('Nomor Kontainer')
    container_size = fields.Char('Ukuran')
    container_type = fields.Char('Jenis')
    container_stuff = fields.Char('Stuff')
    container_part_of = fields.Char('Part of')
    container_keterangan = fields.Char('Keterangan')


class BeacukaiKemasan30(models.Model):
    _name = "beacukai.kemasan.30"    

    reference = fields.Many2one('beacukai.outgoing.30', 'Reference')
    jumlah = fields.Char('Jumlah')
    kode = fields.Char('Kode')
    merk = fields.Char('Merk')
    uraian = fields.Char('Uraian')    


class BeacukaiOutgoingLine30(models.Model):
    _name = "beacukai.outgoing.line.30"
    _inherit = ['beacukai.outgoing.line.mixin']

    reference = fields.Many2one('beacukai.outgoing.30', 'Reference')
    order_line_id = fields.Many2one('sale.order.line', 'SO Line')
    jenis_kemasan = fields.Many2one('beacukai.jenis.kemasan', 'Jenis Kemasan')
    bahan_baku_import_ids = fields.One2many('beacukai.outgoing.line.bahan.baku.import.30', 'reference', 
        string='Bahan Baku Import', copy=True)
    bahan_baku_local_ids = fields.One2many('beacukai.outgoing.line.bahan.baku.local.30', 'reference', 
        string='Bahan Baku Local', copy=True)
    mrp_ids = fields.One2many('beacukai.outgoing.line.mrp.25', 'reference',
                              string='Manufacturing Orders', copy=True)

class BeacukaiOutgoingLineBahanBakuImport30(models.Model):
    _name = "beacukai.outgoing.line.bahan.baku.import.30"    

    reference = fields.Many2one('beacukai.outgoing.line.30', 'Reference')
    source_document = fields.Char('Dok Asal')
    source_no = fields.Char('No')
    source_date = fields.Char('Tgl Dok')
    source_kppbc = fields.Char('KPPBC Dok')
    source_pengajuan = fields.Char('No. Aju')
    source_urutan = fields.Char('Urutan Ke')
        
    product_id = fields.Many2one('product.product', 'Kode Barang')
    product_code = fields.Char(related='product_id.default_code', string='Uraian Barang')
    product_hs_code = fields.Char(related='product_id.hs_code', string='HS Code')    
    product_type = fields.Char('Tipe')
    product_size = fields.Float('Ukuran')
    product_spec = fields.Char('Spesifikasi Lain')
    product_brand = fields.Many2one('beacukai.brand', 'Merk')
    harga_cif_usd = fields.Float('Harga CIF USD')    
    product_qty = fields.Float('Jumlah Satuan')
    ndpbm = fields.Float('NDPBM')
    product_uom_id = fields.Many2one('product.uom', string='Jenis Satuan')
    harga_cif_idr = fields.Float('CIF IDR')    
    product_netto = fields.Float('Netto')    

class BeacukaiOutgoingLineBahanBakuLocal30(models.Model):
    _name = "beacukai.outgoing.line.bahan.baku.local.30"    

    reference = fields.Many2one('beacukai.outgoing.line.30', 'Reference')
    source_document = fields.Char('Dok Asal')
    source_no = fields.Char('No')
    source_date = fields.Char('Tgl Dok')
    source_kppbc = fields.Char('KPPBC Dok')
    source_pengajuan = fields.Char('No. Aju')
    source_urutan = fields.Char('Urutan Ke')    
    product_id = fields.Many2one('product.product', 'Kode Barang')
    product_code = fields.Char(related='product_id.default_code', string='Uraian Barang')
    product_hs_code = fields.Char(related='product_id.hs_code', string='HS Code')    
    product_type = fields.Char('Tipe')
    product_size = fields.Float('Ukuran')
    product_spec = fields.Char('Spesifikasi Lain')
    product_brand = fields.Many2one('beacukai.brand', 'Merk')
    harga_perolehan = fields.Float('Hg Perolehan')    
    product_qty = fields.Float('Jumlah Satuan')
    harga_penyerahan = fields.Float('Harga Penyerahan')
    product_uom_id = fields.Many2one('product.uom', string='Satuan')    
    product_netto = fields.Float('Netto')    


# class BeacukaiOutgoingBahanBakuImport30(models.Model):
#     _name = "beacukai.outgoing.bahan.baku.import.30"    

#     source_document = fields.Char('Dok Asal')
#     source_no = fields.Char('No')
#     source_date = fields.Char('Tgl Dok')
#     source_kppbc = fields.Char('KPPBC Dok')
#     source_pengajuan = fields.Char('No. Aju')
#     source_urutan = fields.Char('Urutan Ke')
    
#     reference = fields.Many2one('beacukai.outgoing.30', 'Reference')    
#     product_id = fields.Many2one('product.product', 'Kode Barang')
#     product_code = fields.Char(related='product_id.default_code', string='Uraian Barang')
#     product_hs_code = fields.Char(related='product_id.hs_code', string='HS Code')    
#     product_type = fields.Char('Tipe')
#     product_size = fields.Float('Ukuran')
#     product_spec = fields.Char('Spesifikasi Lain')
#     product_brand = fields.Many2one('beacukai.brand', 'Merk')
#     harga_cif_usd = fields.Float('Harga CIF USD')    
#     product_qty = fields.Float('Jumlah Satuan')
#     ndpbm = fields.Float('NDPBM')
#     product_uom_id = fields.Many2one('product.uom', string='Jenis Satuan')
#     harga_cif_idr = fields.Float('CIF IDR')    
#     product_netto = fields.Float('Netto')    


# class BeacukaiOutgoingBahanBakuLocal30(models.Model):
#     _name = "beacukai.outgoing.bahan.baku.local.30"    

#     source_document = fields.Char('Dok Asal')
#     source_no = fields.Char('No')
#     source_date = fields.Char('Tgl Dok')
#     source_kppbc = fields.Char('KPPBC Dok')
#     source_pengajuan = fields.Char('No. Aju')
#     source_urutan = fields.Char('Urutan Ke')

#     reference = fields.Many2one('beacukai.outgoing.30', 'Reference')    
#     product_id = fields.Many2one('product.product', 'Kode Barang')
#     product_code = fields.Char(related='product_id.default_code', string='Uraian Barang')
#     product_hs_code = fields.Char(related='product_id.hs_code', string='HS Code')    
#     product_type = fields.Char('Tipe')
#     product_size = fields.Float('Ukuran')
#     product_spec = fields.Char('Spesifikasi Lain')
#     product_brand = fields.Many2one('beacukai.brand', 'Merk')
#     harga_perolehan = fields.Float('Hg Perolehan')    
#     product_qty = fields.Float('Jumlah Satuan')
#     harga_penyerahan = fields.Float('Harga Penyerahan')
#     product_uom_id = fields.Many2one('product.uom', string='Satuan')    
#     product_netto = fields.Float('Netto')    


class BeacukaiJenisEkspor(models.Model):
    _name = "beacukai.jenis.ekspor"    
    
    name = fields.Char('Uraian')
    kode = fields.Char('Kode')    


class BeacukaiKategoriEkspor(models.Model):
    _name = "beacukai.kategori.ekspor"    

    name = fields.Char('Uraian')
    kode = fields.Char('Kode')        


class BeacukaiCaraPerdagangan(models.Model):
    _name = "beacukai.cara.perdagangan"    

    name = fields.Char('Uraian')
    kode = fields.Char('Kode')    


class BeacukaiCaraPembayaran(models.Model):
    _name = "beacukai.cara.pembayaran"    

    name = fields.Char('Uraian')
    kode = fields.Char('Kode')        


class BeacukaiJenisUsaha(models.Model):
    _name = "beacukai.jenis.usaha"    

    name = fields.Char('Uraian')
    kode = fields.Char('Kode')        


class BeacukaiZoningKite(models.Model):
    _name = "beacukai.zoning.kite"    

    name = fields.Char('Uraian')
    kode = fields.Char('Kode')            


class BeacukaiJenisBarang(models.Model):
    _name = "beacukai.jenis.barang"    

    name = fields.Char('Uraian')
    kode = fields.Char('Kode')    


class BeacukaiTempatSimpanBarang(models.Model):
    _name = "beacukai.tempat.simpan.barang"    

    name = fields.Char('Uraian')
    kode = fields.Char('Kode')  


class BeacukaiStuffingCara(models.Model):
    _name = "beacukai.stuffing.cara"    

    name = fields.Char('Uraian')
    kode = fields.Char('Kode')                                      


class BeacukaiStuffingPart(models.Model):
    _name = "beacukai.stuffing.part"    

    name = fields.Char('Uraian')
    kode = fields.Char('Kode')  


class BeacukaiPelabuhan(models.Model):
    _name = "beacukai.pelabuhan"    
        
    kode = fields.Char('Kode')
    name = fields.Char('Uraian')              


class BeacukaiCaraPenyerahan(models.Model):
    _name = "beacukai.cara.penyerahan"    
        
    kode = fields.Char('Kode')
    name = fields.Char('Uraian')                  


class BeacukaiKantorPeriksa(models.Model):
    _name = "beacukai.kantor.periksa"    
        
    kode = fields.Char('Kode')
    name = fields.Char('Uraian')                      


class BeacukaiOutgoing30(models.Model):
    _name = "beacukai.outgoing.30"
    _inherit = ['mail.thread', 'beacukai.mixin']
    _order = "id desc"
    _rec_name = "submission_no"

    @api.model
    def _default_document_type_id(self):        
        document_type_id = self.env['beacukai.document.type'].search([('name', '=', '30')])
        if document_type_id:
            return document_type_id.id        

    """HEADER"""
    so_id = fields.Many2one('sale.order', string='Sales Order ID')
    name = fields.Char('No Dokumen')
    id_header = fields.Char('ID Header TPB')
    date = fields.Date('Tanggal')
    delivery_note_number = fields.Many2one('stock.picking', 'Nomor Pengiriman')
    delivery_note_date = fields.Datetime(related='delivery_note_number.min_date', string='Delivery Date')
    document_type_id = fields.Many2one('beacukai.document.type', 'Tipe', default=_default_document_type_id)
    submission_no = fields.Char('No Pengajuan')

    komoditi = fields.Selection([('Non Migas','Non Migas'),('Migas','Migas')], string='Komoditi')
    curah = fields.Selection([('Curah','Curah'),('Non Curah','Non Curah')], string='Curah')
    bruto = fields.Float('Bruto (Kg)')
    netto = fields.Float('Netto (Kg)')
    jenis_barang = fields.Integer('Jenis Barang')

    kantor_pabean_muat = fields.Many2one('beacukai.tpb', 'Kantor Pabean Muat')
    kantor_pabean_ekspor = fields.Many2one('beacukai.tpb', 'Kantor Pabean Ekspor')
    jenis_ekspor = fields.Many2one('beacukai.jenis.ekspor', 'Jenis Ekspor')
    kategori_ekspor = fields.Many2one('beacukai.kategori.ekspor', 'Kategori Ekspor')
    cara_perdagangan = fields.Many2one('beacukai.cara.perdagangan', 'Cara Perdagangan')
    cara_pembayaran = fields.Many2one('beacukai.cara.pembayaran', 'Cara Pembayaran')
    lokasi_tpb = fields.Char('Lokasi TPB')

    pkb_nama = fields.Char('Nama')
    pkb_npwp = fields.Char('NPWP')
    pkb_alamat = fields.Char('Alamat')
    pkb_telepon = fields.Char('Telepon')
    pkb_fax = fields.Char('Fax')
    pkb_niper = fields.Char('Niper')
    pkb_jenis_usaha = fields.Many2one('beacukai.jenis.usaha', 'Jenis Usaha')
    pkb_zoning_kite = fields.Many2one('beacukai.zoning.kite', 'Zoning KITE')
    pkb_jenis_barang = fields.Many2one('beacukai.jenis.barang', 'Jenis Barang')
    pkb_tempat_simpan_barang = fields.Many2one('beacukai.tempat.simpan.barang', 'Tempat Simpan')
    pkb_pemeriksaan_tanggal = fields.Datetime('Tanggal')
    pkb_pemeriksaan_alamat = fields.Char('Alamat')
    pkb_pemeriksaan_telepon = fields.Char('Telepon')
    pkb_pemeriksaan_fax = fields.Char('Fax')
    pkb_pemeriksaan_contact = fields.Char('Contact Person')
    pkb_stuffing_tanggal = fields.Date('Tanggal')
    pkb_stuffing_tempat = fields.Char('Tempat')
    pkb_stuffing_cara = fields.Many2one('beacukai.stuffing.cara', 'Cara Stuffing')
    pkb_part_of = fields.Many2one('beacukai.stuffing.part', 'Dlm Hal Part of')
    pkb_peti_kemas_20 = fields.Float('Peti Kemas 20')
    pkb_peti_kemas_40 = fields.Float('Peti Kemas 40')

    jenis_tpb = fields.Char('Jenis TPB', default='Kawasan Berikat')
    delivery_purpose_id = fields.Many2one('beacukai.delivery.purpose', 'Tujuan Pengiriman')
    register_number = fields.Char('No Pendaftaran')
    register_date = fields.Date('Tanggal Daftar')

    # Exportir
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
    company_npwp = fields.Char('NPWP', default=lambda self: self.env.user.company_id.vat)
    company_npwp_type = fields.Many2one('beacukai.npwp.type', 'Tipe NPWP')
    company_name = fields.Char('Nama Perusahaan', default=lambda self: self.env.user.company_id.name)
    company_address = fields.Text('Alamat', default=lambda self: self.env.user.company_id.street)
    company_permission_no = fields.Char('No. Izin', default=lambda self: self.env['ir.config_parameter'].get_param('no_tpb'))    
    company_api_type = fields.Many2one('ref.api.type', 'Jenis API')
    company_api_number = fields.Char('Nomor API')
    company_niper = fields.Char('NIPER')
    company_status = fields.Char('Status')

    """Penerima Barang"""
    penerima_id = fields.Many2one('res.partner', 'Nama Penerima')    
    penerima_name = fields.Char('Supplier Name')
    penerima_npwp = fields.Char('NPWP')
    penerima_npwp_type = fields.Many2one('beacukai.npwp.type', 'Tipe NPWP')
    penerima_address = fields.Text('Alamat')
    penerima_api_type = fields.Many2one('ref.api.type', 'Jenis API')
    penerima_api_number = fields.Char('Supplier API Number')
    penerima_country_id = fields.Many2one('res.country', 'Negara')

    """Pembeli TPB"""
    pembeli_id = fields.Char('Nama Pembeli')
    pembeli_npwp = fields.Char('NPWP')
    pembeli_npwp_type = fields.Many2one('beacukai.npwp.type', 'Tipe NPWP')
    pembeli_name = fields.Char('Nama Penerima')
    pembeli_address = fields.Text('Alamat')
    pembeli_permission_no = fields.Char('No. Izin')    
    pembeli_api_type = fields.Many2one('ref.api.type', 'Jenis API')
    pembeli_api_number = fields.Char('Nomor API')
    pembeli_country_id = fields.Many2one('res.country', 'Negara')

    """Dokumen Pelengkap Pabean"""
    invoice_number = fields.Many2one('account.invoice', 'Nomor Invoice')
    invoice_date = fields.Date('Tgl Invoice')
    packing_list_number = fields.Char('Nomor Packing List')
    packing_list_date = fields.Date('Tgl Packing List')
    lainnya_number = fields.Char('Nomor Dok Lain')
    lainnya_date = fields.Date('Tgl Dok Lain')

    contract_number = fields.Char('No Kontrak')
    fasilitas_impor = fields.Char('Fasilitas Impor')    
    currency_id = fields.Many2one('res.currency', 'Currency')
    ndpbm = fields.Float('NDPBM')
    harga_penyerahan = fields.Float('Harga Penyerahan')

    ## Data Pengangkutan
    cara_angkut_id = fields.Many2one('beacukai.cara.angkut', string='Cara Angkut')  
    nama_pengangkut = fields.Char('Nm Sarana Pengangkut')
    no_pengangkut = fields.Char('No. Pengangkut')
    tanggal_perkiraan_ekspor = fields.Date('Tgl Perkiraan Ekspor')

    ## Data Pelabuhan
    pelabuhan_muat_asal = fields.Many2one('beacukai.pelabuhan', string='Pel. Muat Asal')
    pelabuhan_muat_ekspor = fields.Many2one('beacukai.pelabuhan', string='Pel. Muat Ekspor')
    pelabuhan_bongkar = fields.Many2one('beacukai.pelabuhan', string='Pel. Bongkar')
    pelabuhan_tujuan = fields.Many2one('beacukai.pelabuhan', string='Pel. Tujuan')
    negara_ekspor = fields.Many2one('res.country', string='Negara Ekspor')

    ## Data Penyerahan
    cara_penyerahan = fields.Many2one('beacukai.cara.penyerahan', string='Cara Penyerahan')
    freight = fields.Float('Freight')
    jenis_asuransi = fields.Selection([('LN','LN'),('DN','DN')], string='Jenis Asuransi')
    nilai_asuransi = fields.Float('Nilai Asuransi')
    is_maklon = fields.Boolean('Maklon')
    nilai_maklon = fields.Float('Nilai Maklon')

    ## Data Tempat Pemeriksaan
    lokasi_periksa = fields.Selection(LOKASI_PERIKSA, string='Lokasi Periksa')
    tanggal_periksa = fields.Date('Tanggal Periksa')
    kantor_periksa = fields.Many2one('beacukai.kantor.periksa', string='Kantor Periksa')
    gudang_plb = fields.Char('Gudang PLB')

    ## Data Transaksi Ekspor
    ekspor_bank_dhe = fields.Char('Bank DHE')
    ekspor_currency_id = fields.Many2one('res.currency', 'Valuta')
    ekspor_fob = fields.Float('FOB')    

    ## Data Penerimaan Negara
    nilai_bk = fields.Float('Nilai BK')
    pph_22_ekspor = fields.Float('PPH 22 Ekspor')
    dana_pungutan_sawit = fields.Float('Dana Pungutan Sawit')

    """ Footer """
    footer_kota = fields.Char('Kota')
    footer_tanggal = fields.Date('Tanggal')
    footer_pemberitahu = fields.Char('Pemberitahu')
    footer_jabatan = fields.Char('Jabatan')

    """ One to many """
    surat_keputusan_ids = fields.One2many('beacukai.surat.keputusan.30', 'reference', string='Surat Keputusan Bersama', copy=True)
    container_ids = fields.One2many('beacukai.container.30', 'reference', string='Kontainer', copy=True)
    kemasan_ids = fields.One2many('beacukai.kemasan.30', 'reference', string='Kemasan', copy=True)
    line_ids = fields.One2many('beacukai.outgoing.line.30', 'reference', string='Detail Barang', copy=True)
    # bahan_baku_import_ids = fields.One2many('beacukai.outgoing.bahan.baku.import.30', 'reference', string='Bahan Baku Import', copy=True)
    # bahan_baku_local_ids = fields.One2many('beacukai.outgoing.bahan.baku.local.30', 'reference', string='Bahan Baku Local', copy=True)

    picking_count = fields.Integer(compute='_compute_picking_23', string='Receptions', default=0)
    picking_ids = fields.Many2many('stock.picking', compute='_compute_picking_23', string='Receptions', copy=False)

    state = fields.Selection([
        ('pengajuan', 'Pengajuan'),
        ('registrasi', 'Registrasi'),
        ('terima', 'Pengiriman Barang'),
        ('done', 'Selesai'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='pengajuan')

    @api.depends('line_ids.move_ids')
    def _compute_picking_23(self):
        for order in self:
            pickings = self.env['stock.picking']
            # pickings |= pickings.search([('bc_ref_type', '=', self._name),
            #                              '|', ('bc_ref_id', '=', order.id),
            #                              ('submission_no', '=', order.submission_no)])
            pickings |= pickings.search([
                ('submission_no', '=', order.submission_no)                
                ])
            # for line in order.line_ids:
            #     # We keep a limited scope on purpose. Ideally, we should also use move_orig_ids and
            #     # do some recursive search, but that could be prohibitive if not done correctly.
            #     moves = line.move_ids | line.move_ids.mapped(
            #         'returned_move_ids')
            #     moves = moves.filtered(lambda r: r.state != 'cancel')
            #     pickings |= moves.mapped('picking_id')
            order.picking_ids = pickings
            order.picking_count = len(pickings)

    @api.multi
    def button_copy(self):
        for res in self:
            res.penerima_name = res.company_name
            res.penerima_address = res.company_address
            res.penerima_npwp = res.company_npwp
            res.penerima_permission_no = res.company_permission_no
            res.penerima_api_type = res.company_api_type
            res.penerima_api_number = res.company_api_number

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('beacukai.outgoing.30') or 'New'
        inv_line_obj = self.env['account.invoice.line']
        inv_lines = inv_line_obj.search([('invoice_id', '=', vals.get('invoice_number', False))])
        for line in inv_lines:
            line.beacukai_reference = vals.get('submission_no', '')

        return super(BeacukaiOutgoing30, self).create(vals)

    @api.multi
    def write(self, vals):

        ori_no = self.submission_no
        new_no = vals['submission_no'] if 'submission_no' in vals else ori_no
        ori_inv_id = self.invoice_number.id
        new_inv_id = vals['invoice_number'] if 'invoice_number' in vals else ori_inv_id

        inv_line_obj = self.env['account.invoice.line']

        if ori_inv_id != new_inv_id:
            inv_lines = inv_line_obj.search([('invoice_id', '=', ori_inv_id)])
            for line in inv_lines:
                line.beacukai_reference = ''

        if (ori_no != new_no) or (ori_inv_id != new_inv_id):
            inv_lines = inv_line_obj.search([('invoice_id', '=', new_inv_id)])
            for line in inv_lines:
                line.beacukai_reference = new_no

        return super(BeacukaiOutgoing30, self).write(vals)

    def action_done(self):
        # override beacukai mixin
        if self.finish_date != '':
            return self.write({'state': 'done', 'finish_date': fields.Date.today()})
        else:
            raise UserError(_('Pastikan telah menginput finish date'))

    # @api.multi
    # def action_receive(self):
    #     # override beacukai mixin
    #     return self.write({'state': 'terima'})

    @api.multi
    def action_final_receive(self):
        for res in self:
            picking_id = ''
            orderline_id = ''
            if res.line_ids:
                if not res.so_id:
                    res.action_receive()
                elif res.so_id:                    
                    
                        # if not line.purchase_line_id and not line.purchase_id:
                        #     res.action_receive()
                        #     # raise UserError(_("Products are not linked with Purchase Order"))
                        # if line.order_line_id:
                        #     orderline_id = self.env['sale.order.line'].search([('id','=',line.order_line_id.id)])
                        #     if orderline_id:
                                # linemove_ids = orderline_id.move_ids
                    picking_ids = self.env['stock.picking'].search([
                        ('origin','=',res.so_id.name),
                        ('state','=','assigned')
                        ])

                    if picking_ids:
                        for picking in picking_ids:
                            for line in res.line_ids:                                    
                                if picking and picking.pack_operation_product_ids:
                                    for pack in picking.pack_operation_product_ids:                            
                                        if line.product_id == pack.product_id:
                                            pack.write({
                                                'qty_done' : pack.qty_done + line.product_qty
                                                })
                                        
                            wizard = picking.do_new_transfer()
                            # print "Wizard ", wizard
                            # wizard_id = wizard['res_id']
                            # self.env['stock.immediate.transfer'].browse(wizard_id).process()

            res.write({'state' : 'done'})

    @api.multi
    def action_receive(self):
        # picking_type = self.env['stock.picking.type'].search([('name','=','dokumen_penerimaan')],limit=1)

        for bcmove in self:
            _logger.info('picking test')
            # if bcmove.is_from_po:
            #     return self.write({'state': 'terima'})

            if bcmove.picking_type_id.default_location_dest_id.id:
                dst = bcmove.picking_type_id.default_location_dest_id.id
            else:
                dst = self.default_location_dest_id = self.env.ref(
                    'stock.stock_location_stock').id
            if bcmove.picking_type_id.default_location_src_id.id:
                src = bcmove.picking_type_id.default_location_src_id.id
            else:
                src = self.env.ref('stock.stock_location_suppliers').id
            # _logger.info(self.env.ref('stock.stock_location_suppliers').name)
            # _logger.info(dst)
            stok = self.env['stock.picking'].create({
                'move_type': 'direct',
                'picking_type_id': bcmove.picking_type_id.id,
                # 'is_beacukai_incoming_23': True,
                # 'beacukai_incoming_23_id': bcmove.id,
                'origin': bcmove.submission_no,
                'location_id': src,
                'bc_ref_type': self._name,
                'bc_ref_id': bcmove.id,
                'submission_no': bcmove.submission_no,
                'location_dest_id': dst,
            })
            if bcmove.line_ids:
                # _logger.info(bcmove.line_ids)
                for line in bcmove.line_ids:
                    pack_operation_product_ids = {
                        'picking_id': stok.id,
                        # 'bc_incoming_line_23_id': line.id,
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.product_qty,
                        'product_uom': line.product_uom_id.id,
                        'name': line.product_id.display_name,
                        'date_expected': bcmove.register_date,
                        'location_id': src,
                        'location_dest_id': dst
                    }
                    stok.move_lines.create(pack_operation_product_ids)

            if stok:
                wizard = stok.do_new_transfer()                
                wizard_id = wizard['res_id']                    
                self.env['stock.immediate.transfer'].browse(wizard_id).process()

        return bcmove.write({'state' : 'done'})