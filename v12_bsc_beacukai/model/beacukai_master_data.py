from odoo import api, fields, models, _


# """"""""""""""""""""""""""""""""""""" MASTER DATA """""""""""""""""""""""""""""""""""""
class RefCategoryProduct(models.Model):
    _name = "ref.category.product"
    _rec_name = 'desc'

    name = fields.Char('Kode Kategori')
    desc = fields.Char('Deskripsi Kategori')
    destination_tpb_id = fields.Many2one('ref.destination.tpb',string='Kode Tujuan TPB')

class RefCodeId(models.Model):
    _name = "ref.code.id"
    _rec_name = 'desc'

    name = fields.Char('Kode ID')
    desc = fields.Char('Deskripsi Kode ID')

class RefTariffType(models.Model):
    _name = "ref.tariff.type"
    _rec_name = 'desc'

    name = fields.Char('Kode Jenis Tarif')
    desc = fields.Char('Deskripsi Jenis Tarif')


class RefOfficePabean(models.Model):
    _name = "ref.office.pabean"
    _rec_name = 'desc'

    name = fields.Char('Kode Kantor')
    desc = fields.Char('Deskripsi Kantor')


class RefDestinationTpb(models.Model):
    _name = "ref.destination.tpb"
    _rec_name = 'desc'

    name = fields.Char('Kode Tujuan Tpb')
    desc = fields.Char('Deskripsi Tujuan Tpb')


class RefSupplier(models.Model):
    _name = "ref.supplier"
    _rec_name = 'name'

    name = fields.Char('Nama')
    address = fields.Char('Alamat')
    npwp = fields.Char('NPWP')
    country_code = fields.Char('Kode Negara')
    ids_code = fields.Char('Kode ID')


class RefShip(models.Model):
    _name = "ref.ship"
    _rec_name = 'desc'

    negara_id = fields.Many2one('ref.negara',string='Kode Negara')
    name = fields.Char('Kode Bendera',related='negara_id.name')
    desc = fields.Char('Nama Kapal')


class RefModeTransport(models.Model):
    _name = "ref.mode.transport"
    _rec_name = 'desc'

    name = fields.Char('Kode Cara Angkut')
    desc = fields.Char('Deskripsi Cara Angkut')


class RefPackageType(models.Model):
    _name = "ref.package.type"
    _rec_name = 'desc'

    name = fields.Char('Kode Kemasan')
    desc = fields.Char('Deskripsi Kemasan')


class RefDocument(models.Model):
    _name = "ref.document"
    _rec_name = 'desc'

    name = fields.Char('Kode Dokumen')
    tipe = fields.Char('Tipe Dokumen')
    desc = fields.Char('Deskripsi Dokumen')


class RefContainerSize(models.Model):
    _name = "ref.container.size"
    _rec_name = 'desc'

    name = fields.Char('Kode Ukuran Kontainer')
    desc = fields.Char('Deskripsi Ukuran Kontainer')


class RefContainerType(models.Model):
    _name = "ref.container.type"
    _rec_name = 'desc'

    name = fields.Char('Kode Tipe Kontainer')
    desc = fields.Char('Deskripsi Tipe Kontainer')


class RefNegara(models.Model):
    _name = "ref.negara"
    _rec_name = 'desc'

    name = fields.Char('Kode Negara')
    desc = fields.Char('Deskripsi Negara')

class RefBendera(models.Model):
    _name = "ref.bendera"
    _rec_name = 'desc'

    name = fields.Char('Kode Bendera')
    desc = fields.Char('Deskripsi Bendera')

class RefPort(models.Model):
    _name = "ref.port"
    _rec_name = 'desc'

    information = fields.Char('Keterangan')
    office_code = fields.Char('Kode Kantor')
    name = fields.Char('Kode Pelabuhan')
    desc = fields.Char('Deskripsi Pelabuhan')


class RefTps(models.Model):
    _name = "ref.tps"
    _rec_name = 'desc'

    fl_active = fields.Char('FL Aktif')
    wh_type = fields.Char('Jenis Gudang')
    office_code = fields.Char('Kode Kantor')
    name = fields.Char('Kode')
    desc = fields.Char('Deskripsi')


class RefValuta(models.Model):
    _name = "ref.valuta"
    _rec_name = 'desc'

    name = fields.Char('Kode Valuta')
    desc = fields.Char('Deskripsi Valuta')


class RefSatuan(models.Model):
    _name = "ref.satuan"
    _rec_name = 'desc'

    name = fields.Char('Kode Satuan')
    desc = fields.Char('Deskripsi Satuan')


class RefFacility(models.Model):
    _name = "ref.facility"
    _rec_name = 'desc'

    name = fields.Char('Kode Fasilitas')
    desc = fields.Char('Deskripsi Fasilitas')


class RefSchemeTariff(models.Model):
    _name = "ref.scheme.tariff"
    _rec_name = 'desc'

    name = fields.Char('Kode Skema')
    desc = fields.Char('Deskripsi Skema')


class RefComodity(models.Model):
    _name = "ref.comodity"
    _rec_name = 'desc'

    name = fields.Char('Kode Komoditi')
    desc = fields.Char('Deskripsi Komoditi')


class RefApiType(models.Model):
    _name = "ref.api.type"
    _rec_name = 'desc'

    name = fields.Char('Kode Jenis API')
    desc = fields.Char('Deskripsi Jenis API')


class RefTariffFacility(models.Model):
    _name = "ref.tariff.facility"
    _rec_name = 'desc_facility'

    name_document = fields.Char('Kode Dokumen Pabean')
    name_facility = fields.Char('Kode Fasilitas')
    desc_facility = fields.Char('Uraian Fasilitas')
    desc_short = fields.Char('Uraian Pendek')


class RefPosTariff(models.Model):
    _name = "ref.pos.tariff"
    _rec_name = 'hs_number'

    tariff_type_bm = fields.Char(string="Jenis Tarif BM")
    tariff_type_cukai = fields.Char(string="Jenis Tarif Cukai")
    unit_code_bm = fields.Char(string="Kode Satuan BM")
    unit_code_cukai = fields.Char(string="Kode Satuan Cukai")
    hs_number = fields.Char(string="Nomor HS")
    hs_serial = fields.Integer(string="Seri HS")
    tariff_bm = fields.Float(string="Tarif BM")
    tariff_cukai = fields.Float(string="Tarif Cukai")
    tariff_pph = fields.Float(string="Tarif PPH")
    tariff_ppn = fields.Float(string="Tarif PPN")
    tariff_ppnbm = fields.Float(string="Tarif PPNBM")
