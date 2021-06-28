from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class BeacukaiDeliveryPurpose(models.Model):
    _inherit = "beacukai.delivery.purpose"

    kode_dokumen = fields.Many2one('beacukai.document.type', 'Kode Dokumen')
    kode_tujuan_pengiriman = fields.Char('Kode Tujuan Pengiriman')


class BeacukaiNpwpType(models.Model):
    _name = "beacukai.npwp.type"    

    name = fields.Char('NPWP Type')
    kode = fields.Char('Kode')


class BeacukaiCaraAngkut(models.Model):
    _name = "beacukai.cara.angkut"    

    name = fields.Char('Cara Angkut')
    kode = fields.Char('Kode')


class BeacukaiJenisKemasan(models.Model):
    _name = "beacukai.jenis.kemasan"    

    name = fields.Char('Jenis Kemasan')


class BeacukaiBrand(models.Model):
    _name = "beacukai.brand"    

    name = fields.Char('Brand')


class BeacukaiSuratKeputusan40(models.Model):
    _name = "beacukai.surat.keputusan.40"    

    reference = fields.Many2one('beacukai.incoming.40', 'Reference')
    name = fields.Char('Nomor Dokumen')    
    jenis_dokumen = fields.Char('Jenis Dokumen')
    date = fields.Date('Tanggal')


class BeacukaiContainer40(models.Model):
    _name = "beacukai.container.40"    

    reference = fields.Many2one('beacukai.incoming.40', 'Reference')
    name = fields.Char('Nomor Kontainer')
    container_size = fields.Char('Ukuran')
    container_type = fields.Char('Tipe')
    container_keterangan = fields.Char('Keterangan')


class BeacukaiKemasan40(models.Model):
    _name = "beacukai.kemasan.40"    

    reference = fields.Many2one('beacukai.incoming.40', 'Reference')
    jumlah = fields.Char('Jumlah')
    kode = fields.Char('Kode')
    uraian = fields.Char('Uraian')    


class BeacukaiIncomingLine40(models.Model):
    _name = "beacukai.incoming.line.40"
    _inherit = ['beacukai.incoming.line.mixin']

    reference = fields.Many2one('beacukai.incoming.40', 'Reference')
    jenis_kemasan = fields.Many2one('beacukai.jenis.kemasan', 'Jenis Kemasan')
    received_qty = fields.Float(compute="_get_received_qty", string="Received Qty")
    
    @api.depends('reference.picking_ids')
    def _get_received_qty(self):
        for res in self:
            received_qty = 0
            if res.reference.picking_ids:
                for picking in res.reference.picking_ids:
                    for pack in picking.pack_operation_product_ids:
                        if pack.product_id.id == res.product_id.id:
                            received_qty += pack.qty_done
            else:
                received_qty = res.product_qty
                
            res.received_qty = received_qty    

class Beacukaiincoming40(models.Model):
    _name = "beacukai.incoming.40"
    _inherit = ['mail.thread', 'beacukai.incoming.mixin']
    _order = "id desc"
    _rec_name = "submission_no"

    @api.model
    def _default_document_type_id(self):        
        document_type_id = self.env['beacukai.document.type'].search([('name', '=', '40')])
        if document_type_id:
            return document_type_id.id        

    """HEADER"""
    name = fields.Char('No Dokumen')
    id_header = fields.Char('ID Header TPB')
    date = fields.Date('Tanggal')
    delivery_note_number = fields.Many2one('stock.picking', 'Nomor Pengiriman')
    delivery_note_date = fields.Datetime(related='delivery_note_number.min_date', string='Delivery Date')
    document_type_id = fields.Many2one('beacukai.document.type', 'Tipe', default=_default_document_type_id)
    kantor_pabean = fields.Many2one('beacukai.tpb')
    jenis_tpb = fields.Char('Jenis TPB', default='KAWASAN BERIKAT')
    delivery_purpose_id = fields.Many2one('beacukai.delivery.purpose', 'Tujuan Pengiriman')
    register_number = fields.Char('No Pendaftaran')
    register_date = fields.Date('Tanggal Daftar')
    po_id = fields.Many2one('purchase.order', string='No PO')
    submission_no = fields.Char('Nomor Pengajuan')

    """Pengusaha TPB"""
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
    company_npwp_type = fields.Many2one('beacukai.npwp.type', 'Tipe NPWP')
    company_npwp = fields.Char('NPWP', default=lambda self: self.env.user.company_id.vat)
    company_name = fields.Char('Nama Perusahaan', default=lambda self: self.env.user.company_id.name)
    company_address = fields.Text('Alamat', default=lambda self: self.env.user.company_id.street)
    company_permission_no = fields.Char('No. Izin', default=lambda self: self.env['ir.config_parameter'].get_param('no_tpb'))    
    company_api_type = fields.Many2one('ref.api.type', 'Jenis API')
    company_api_number = fields.Char('Nomor API')

    """Pemilik Barang"""
    supplier_id = fields.Many2one('res.partner', 'Nama Supplier', domain="[('supplier', '=', True)]")
    supplier_name = fields.Char('Nama Supplier')
    supplier_npwp_type = fields.Many2one('beacukai.npwp.type', 'Tipe NPWP')
    supplier_npwp = fields.Char('NPWP')    
    supplier_address = fields.Text('Alamat')
    supplier_api_type = fields.Many2one('ref.api.type', 'Jenis API')
    supplier_api_number = fields.Char('Supplier API Number')

    """Pengusaha TPB"""
    penerima_id = fields.Char('Nama Penerima')
    penerima_npwp = fields.Char('NPWP')
    penerima_npwp_type = fields.Many2one('beacukai.npwp.type', 'Tipe NPWP')
    penerima_name = fields.Char('Nama Penerima')
    penerima_address = fields.Text('Alamat')
    penerima_permission_no = fields.Char('No. Izin')    
    penerima_api_type = fields.Many2one('ref.api.type', 'Jenis API')
    penerima_api_number = fields.Char('Nomor API')

    """Dokumen Pelengkap Pabean"""
    invoice_number = fields.Many2one('account.invoice', 'Nomor Invoice')
    packing_list_number = fields.Char('Nomor Packing List')
    contract_number = fields.Char('No Kontrak')
    faktur_pajak = fields.Char('Faktur Pajak')
    skep = fields.Char('SKEP')
    fasilitas_impor = fields.Char('Fasilitas Impor')    
    currency_id = fields.Many2one('res.currency', 'Currency')
    ndpbm = fields.Float('NDPBM')
    harga_penyerahan = fields.Float('Harga Penyerahan')
    cara_angkut_id = fields.Many2one('beacukai.cara.angkut', string='Cara Angkut')
    nomor_polisi = fields.Char('Nomor Polisi')    

    """ Data Barang """
    volume = fields.Integer('Volume (m3)')
    bruto = fields.Float('Berat Kotor (Kg)')
    netto = fields.Float('Berat Bersih (Kg)')

    """ Footer """
    footer_kota = fields.Char('Kota')
    footer_tanggal = fields.Date('Tanggal')
    footer_pemberitahu = fields.Char('Pemberitahu')
    footer_jabatan = fields.Char('Jabatan')

    """ One to many """
    surat_keputusan_ids = fields.One2many('beacukai.surat.keputusan.40', 'reference', string='Surat Keputusan Bersama', copy=True)
    container_ids = fields.One2many('beacukai.container.40', 'reference', string='Kontainer', copy=True)
    kemasan_ids = fields.One2many('beacukai.kemasan.40', 'reference', string='Kemasan', copy=True)
    line_ids = fields.One2many('beacukai.incoming.line.40', 'reference', string='Detail Barang', copy=True)    

    state = fields.Selection([
        ('pengajuan', 'Pengajuan'),
        ('registrasi', 'Registrasi'),
        ('terima', 'Penerimaan Barang'),
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
        vals['name'] = self.env['ir.sequence'].next_by_code('beacukai.incoming.40') or 'New'
        return super(Beacukaiincoming40, self).create(vals)
