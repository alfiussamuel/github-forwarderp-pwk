from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class BeacukaiSuratKeputusan27(models.Model):
    _name = "beacukai.surat.keputusan.27"    

    reference = fields.Many2one('beacukai.outgoing.27', 'Reference')
    name = fields.Char('Nomor Dokumen')
    jenis_dokumen = fields.Char('Jenis Dokumen')
    date = fields.Date('Tanggal')


class BeacukaiContainer27(models.Model):
    _name = "beacukai.container.27"    

    reference = fields.Many2one('beacukai.outgoing.27', 'Reference')
    name = fields.Char('Nomor Kontainer')
    container_size = fields.Char('Ukuran')
    container_type = fields.Char('Tipe')
    container_keterangan = fields.Char('Keterangan')


class BeacukaiKemasan27(models.Model):
    _name = "beacukai.kemasan.27"    

    reference = fields.Many2one('beacukai.outgoing.27', 'Reference')
    jumlah = fields.Char('Jumlah')
    kode = fields.Char('Kode')
    uraian = fields.Char('Uraian')    


class BeacukaiOutgoingLine27(models.Model):
    _name = "beacukai.outgoing.line.27"
    _inherit = ['beacukai.outgoing.line.mixin']

    reference = fields.Many2one('beacukai.outgoing.27', 'Reference')
    jenis_kemasan = fields.Many2one('beacukai.jenis.kemasan', 'Jenis Kemasan')
    bahan_baku_import_ids = fields.One2many('beacukai.outgoing.line.bahan.baku.import.27', 'reference', 
        string='Bahan Baku Import', copy=True)
    bahan_baku_local_ids = fields.One2many('beacukai.outgoing.line.bahan.baku.local.27', 'reference', 
        string='Bahan Baku Local', copy=True)
    mrp_ids = fields.One2many('beacukai.outgoing.line.mrp.25', 'reference', 
        string='Manufacturing Orders', copy=True)

class BeacukaiOutgoingLineMrp25(models.Model):
    _name = "beacukai.outgoing.line.mrp.25"    

    reference = fields.Many2one('beacukai.outgoing.line.25', 'Reference')    
    mrp_id = fields.Many2one('mrp.order', 'Reference')

class BeacukaiOutgoingLineBahanBakuImport27(models.Model):
    _name = "beacukai.outgoing.line.bahan.baku.import.27"    

    reference = fields.Many2one('beacukai.outgoing.line.27', 'Reference')
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

class BeacukaiOutgoingLineBahanBakuLocal27(models.Model):
    _name = "beacukai.outgoing.line.bahan.baku.local.27"    

    reference = fields.Many2one('beacukai.outgoing.line.27', 'Reference')
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


# class BeacukaiOutgoingBahanBakuImport27(models.Model):
#     _name = "beacukai.outgoing.bahan.baku.import.27"    

#     source_document = fields.Char('Dok Asal')
#     source_no = fields.Char('No')
#     source_date = fields.Char('Tgl Dok')
#     source_kppbc = fields.Char('KPPBC Dok')
#     source_pengajuan = fields.Char('No. Aju')
#     source_urutan = fields.Char('Urutan Ke')
    
#     reference = fields.Many2one('beacukai.outgoing.27', 'Reference')    
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


# class BeacukaiOutgoingBahanBakuLocal27(models.Model):
#     _name = "beacukai.outgoing.bahan.baku.local.27"    

#     source_document = fields.Char('Dok Asal')
#     source_no = fields.Char('No')
#     source_date = fields.Char('Tgl Dok')
#     source_kppbc = fields.Char('KPPBC Dok')
#     source_pengajuan = fields.Char('No. Aju')
#     source_urutan = fields.Char('Urutan Ke')

#     reference = fields.Many2one('beacukai.outgoing.27', 'Reference')    
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


class BeacukaiOutgoing27(models.Model):
    _name = "beacukai.outgoing.27"
    _inherit = ['mail.thread', 'beacukai.mixin']
    _order = "id desc"
    _rec_name = "submission_no"

    @api.model
    def _default_document_type_id(self):        
        document_type_id = self.env['beacukai.document.type'].search([('name', '=', '27'),
                                                                      ('document_type', '=', 'outgoing')])
        if document_type_id:
            return document_type_id.id        

    """HEADER"""
    name = fields.Char('No Dokumen')
    id_header = fields.Char('ID Header TPB')
    date = fields.Date('Tanggal')
    delivery_note_number = fields.Many2one('stock.picking', 'Nomor Pengiriman')
    delivery_note_date = fields.Datetime(related='delivery_note_number.min_date', string='Delivery Date')
    document_type_id = fields.Many2one('beacukai.document.type', 'Tipe', default=_default_document_type_id)
    submission_no = fields.Char('No Pengajuan')
    kantor_pabean = fields.Many2one('beacukai.tpb')
    jenis_tpb = fields.Char('Jenis TPB', default='Kawasan Berikat')
    delivery_purpose_id = fields.Many2one('beacukai.delivery.purpose', 'Tujuan Pengiriman')
    register_number = fields.Char('No Pendaftaran')
    register_date = fields.Date('Tanggal Daftar')

    """Pengusaha TPB"""
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
    company_npwp = fields.Char('NPWP', default=lambda self: self.env.user.company_id.vat)
    company_name = fields.Char('Nama Perusahaan', default=lambda self: self.env.user.company_id.name)
    company_address = fields.Text('Alamat', default=lambda self: self.env.user.company_id.street)
    company_permission_no = fields.Char('No. Izin',
                                        default=lambda self: self.env['ir.config_parameter'].get_param('no_tpb'))
    company_api_type = fields.Many2one('ref.api.type', 'Jenis API')
    company_api_number = fields.Char('Nomor API')

    """Pemilik Barang"""
    supplier_id = fields.Many2one('res.partner', 'Nama Supplier')
    supplier_npwp = fields.Char('NPWP')
    supplier_address = fields.Text('Alamat')
    supplier_api_type = fields.Many2one('ref.api.type', 'Jenis API')
    supplier_api_number = fields.Char('Supplier API Number')

    """Pengusaha TPB"""
    penerima_id = fields.Char('Nama Penerima')
    penerima_npwp = fields.Char('NPWP')
    penerima_name = fields.Char('Nama Penerima')
    penerima_address = fields.Text('Alamat')
    penerima_permission_no = fields.Char('No. Izin')    
    penerima_api_type = fields.Many2one('ref.api.type', 'Jenis API')
    penerima_api_number = fields.Char('Nomor API')

    """Dokumen Pelengkap Pabean"""
    invoice_number = fields.Many2one('account.invoice', 'Nomor Invoice')
    packing_list_number = fields.Char('Nomor Packing List')
    contract_number = fields.Char('No Kontrak')
    fasilitas_impor = fields.Char('Fasilitas Impor')    
    currency_id = fields.Many2one('res.currency', 'Currency')
    ndpbm = fields.Float('NDPBM')
    harga_penyerahan = fields.Float('Harga Penyerahan')
    cara_angkut_id = fields.Many2one('beacukai.cara.angkut', string='Cara Angkut')
    bruto = fields.Float('Bruto (Kg)')
    netto = fields.Float('Netto (Kg)')

    """ One to many """
    surat_keputusan_ids = fields.One2many('beacukai.surat.keputusan.27', 'reference',
                                          string='Surat Keputusan Bersama', copy=True)
    container_ids = fields.One2many('beacukai.container.27', 'reference', string='Kontainer', copy=True)
    kemasan_ids = fields.One2many('beacukai.kemasan.27', 'reference', string='Kemasan', copy=True)
    line_ids = fields.One2many('beacukai.outgoing.line.27', 'reference', string='Detail Barang', copy=True)
    # bahan_baku_import_ids = fields.One2many('beacukai.outgoing.bahan.baku.import.27', 'reference',
    #                                         string='Bahan Baku Import', copy=True)
    # bahan_baku_local_ids = fields.One2many('beacukai.outgoing.bahan.baku.local.27', 'reference',
    #                                        string='Bahan Baku Local', copy=True)

    state = fields.Selection([
        ('pengajuan', 'Pengajuan'),
        ('registrasi', 'Registrasi'),
        ('terima', 'Pengiriman Barang'),
        ('done', 'Selesai'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='pengajuan')

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
        vals['name'] = self.env['ir.sequence'].next_by_code('beacukai.outgoing.27') or 'New'
        return super(BeacukaiOutgoing27, self).create(vals)

