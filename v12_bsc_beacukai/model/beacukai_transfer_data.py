from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import date


class TpbContainer(models.Model):
    _name = "tpb.container"

    reference_container = fields.Many2one(
        'beacukai.incoming.23', string='Reference BC23', index=True, ondelete='cascade')
    submission_no_23 = fields.Char(
        related='reference_container.submission_no', readonly=True)
    container_number = fields.Char('No. Kontainer', required=True)
    desc = fields.Char('Keterangan')
    container_size_id = fields.Many2one(
        'ref.container.size', string='Ukuran', required=True)
    container_type_id = fields.Many2one(
        'ref.container.type', string='Tipe', required=True)


class TpbPackage(models.Model):
    _name = "tpb.package"

    reference_package = fields.Many2one(
        'beacukai.incoming.23', string='Reference Header BC23', index=True, ondelete='cascade')
    submission_no_23 = fields.Char(
        related='reference_package.submission_no', readonly=True)
    package_qty = fields.Integer('Jumlah Kemasan', required=True)
    merc = fields.Char('Merk')
    code = fields.Char('Kode')
    package = fields.Char('Kemasan')
    package_type_id = fields.Many2one(
        'ref.package.type', string='Tipe', required=True)


class TpbDocument(models.Model):
    _name = "tpb.document"

    reference_document = fields.Many2one(
        'beacukai.incoming.23', string='Reference Header BC23', index=True, ondelete='cascade')
    submission_no_23 = fields.Char(
        related='reference_document.submission_no', readonly=True)
    document_ref = fields.Many2one(
        'ref.document', string='Dokumen', required=True)
    document_num = fields.Char('Nomor Dokumen', required=True)
    document_date = fields.Date('Tanggal Dokumen', required=True)


class TpbGoodsTarif(models.Model):
    _name = "tpb.goods.tariff"

    reference_goods_tariff = fields.Many2one(
        'beacukai.incoming.23', string='Reference Header BC23', index=True, ondelete='cascade')
    submission_no_23 = fields.Char(
        related='reference_goods_tariff.submission_no', readonly=True)
    tariff_type = fields.Selection([
        ('BM', 'BM - BEA MASUK'),
        ('BMKITE', 'BM - BEA MASUK KITE'),
        ('PPN', 'PPN'),
        ('PPH', 'PPH')
    ], string='Jenis Tarif', required=True)
    # tariff_code = fields.Selection([
    #     ('1','1 - ADVOLORUM'),
    #     ('2','2 - SPESIFIK')
    #     ],string='Kode Tarif',required=True)
    # submission_no_23 = fields.Char(related='reference_goods_tariff.submission_no',readonly=True)
    # tariff_type = fields.Char('Jenis Tarif')
    tariff_code = fields.Many2one(
        'ref.tariff.type', string='Kode Tarif', required=True)
    tariff_value = fields.Float('Nilai Tarif', required=True)
    facility_code = fields.Many2one(
        'ref.tariff.facility', string='Kode Fasilitas', required=True)
    facility_tarif = fields.Float('Tarif Fasilitas', required=True)

    comodity_code = fields.Many2one('ref.comodity', string='Kode Komoditi')
    qty_code = fields.Many2one('ref.satuan', string='Kode Satuan')
    qty_unit = fields.Float('Jumlah Satuan')


class TpbGoodsDocument(models.Model):
    _name = "tpb.goods.document"

    reference_goods_document = fields.Many2one(
        'beacukai.incoming.23', string='Reference Header BC23', index=True, ondelete='cascade')
    submission_no_23 = fields.Char(
        related='reference_goods_document.submission_no', readonly=True)
    doc_serial = fields.Many2one(
        'tpb.document', string='Seri Dokumen', index=True, ondelete='cascade')
    doc_goods_id = fields.Many2one(
        'beacukai.incoming.line.23', string='ID Barang', index=True, ondelete='cascade')
    doc_header_id = fields.Many2one(
        'beacukai.incoming.23', string='ID Header', index=True, ondelete='cascade')
