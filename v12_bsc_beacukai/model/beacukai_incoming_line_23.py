from odoo import api, fields, models
import odoo.addons.decimal_precision as dp

import logging

_logger = logging.getLogger(__name__)


class BeacukaiIncomingLine23(models.Model):
    _name = "beacukai.incoming.line.23"
    # _rec_name = 'product_name'

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[' + str(record.reference.submission_no) + ']' + '[' + str(
                record.reference.register_number) + ']'+'[' + str(record.product_qty) + ']'
            # name = self.reference.submission_no
            result.append((record.id, name))
        return result

    # When Reloaded from Purchase Order
    purchase_id = fields.Many2one("purchase.order", string="Purchase Order")
    purchase_line_id = fields.Many2one("purchase.order.line", string="Purchase Order Line")


    reference = fields.Many2one(
        'beacukai.incoming.23', string='Reference BC23', index=True, ondelete='cascade')
    # reference = fields.Many2one('beacukai.incoming', 'Reference')    
    submission_no_23 = fields.Char(related='reference.submission_no',
                                   readonly=True)
    # submission_no = fields.Char(related='reference.submission_no',
    #                             readonly=True)
    date_aju_line = fields.Date(string='Tanggal Aju', related='reference.date_aju')
    """Data Barang"""
    product_id = fields.Many2one('product.product', 'Kode Barang')
    product_name = fields.Char('Uraian Barang', related="product_id.name")
    product_code = fields.Char('Kode Barang', related="product_id.default_code")

    product_type = fields.Char('Tipe')
    product_size = fields.Char('Ukuran')
    product_spec = fields.Char('Spesifikasi Lain')
    product_brand = fields.Char('Merk')
    volume = fields.Float('Volume (m3)')
    
    # product_hs_code = fields.Char(
    #     'HS Code', related="product_id.code_hs")
    # product_hs_code = fields.Many2one('ref.pos.tariff', 'Nomor HS')
    product_hs_code = fields.Char(related='product_id.hs_code', string='HS Code', readonly=True)
    product_categ = fields.Many2one(
        'product.category', 'Kategori Barang')

    # product_qty = fields.Float('Qty')
    saldo = fields.Float('Saldo')
    # product_uom_id = fields.Many2one('product.uom', 'Satuan')
    product_price = fields.Float('Harga')

    """Harga"""
    product_incost = fields.Float('Total/Detil (FOB)')
    product_discount = fields.Float(compute="_get_product_cif", string='BT-Diskon')
    product_price_invoice = fields.Float(compute="_get_product_cif", string='Harga Detil')    
    product_qty = fields.Float('Jumlah Satuan', digits=dp.get_precision('Product Unit of Measure'))
    product_uom_id = fields.Many2one('uom.uom', 'Satuan')
    product_price_qty = fields.Float(compute="_get_product_cif", string='Harga Satuan', digits=dp.get_precision('Product Unit of Measure'))    
    cif_cost = fields.Float(compute="_get_product_cif", string='Nilai CIF', required=True, digits=dp.get_precision('Product Unit of Measure'))
    cif_amount = fields.Float(compute="_get_product_cif", string='Nilai CIF Rupiah', required=True, default=0, digits=dp.get_precision('Product Unit of Measure'))

    # product_netto = fields.Float(string='Jumlah')
    product_freight = fields.Float('Freight', default=0)
    product_insurance = fields.Float('Asuransi LN/DN', default=0)        

    """Kemasan"""
    product_package_qty = fields.Integer('Jumlah Kemasan', digits=dp.get_precision('Product Unit of Measure'))
    product_package_type = fields.Many2one(
        'ref.package.type', 'Jenis Kemasan')
    product_netto = fields.Float('Netto', digits=dp.get_precision('Product Unit of Measure'))

    """Negara Asal"""
    product_country = fields.Many2one(
        'res.country', 'Negara Asal Barang')

    """Tarif&Fasilitas"""
    tariff_ids = fields.One2many(
        'tpb.goods.tariff', 'reference_goods_tariff', 'Lines Tarif & Cukai', copy=True)

    """Fasilitas"""
    facility_code = fields.Many2one('ref.facility', 'Kode Fasilitas')

    """Skema Tarif"""
    tariff_scheme_code = fields.Many2one(
        'ref.scheme.tariff', 'Kode Skema Tarif')

    """Selain ada di modul"""
    # product_status = fields.Char('Status', default="02")
    # product_serial = fields.Integer(
    #     'Seri Barang', related=self.id)

    product_bruto = fields.Float('Bruto')
    move_ids = fields.One2many('stock.move', 'bc_incoming_line_23_id',
                               string='BC Incoming Line', readonly=True, ondelete='set null', copy=False)
    outgoing_ids = fields.One2many('beacukai.outgoing.line', 'incoming_line_23_id',
                                   string='BC Outgoing', readonly=True, ondelete='set null', copy=False)
    # submission_no = fields.Char(related='reference.submission_no')
    # document_type_id = fields.Char(related='reference.document_type_id.name')
    register_number = fields.Char(related='reference.register_number')
    # register_date = fields.Date(related='reference.register_date')
    # date_aju_line = fields.Date(related='reference.date_aju')
    # delivery_note_number = fields.Integer(related='reference.delivery_note_number.name')
    # delivery_note_date = fields.Datetime(
    #     related='reference.delivery_note_date')
    """not used"""
    # currency_id = fields.Many2one(
    #     "res.currency", related='product_id.currency_id')
    currency_id = fields.Many2one(
        "res.currency", string="Valuta")
    biaya_tambahan = fields.Float(string='Biaya Tambahan')
    """not used"""
    # cif = fields.Float(string='CIF')

    # tpb_source_id = fields.Many2one(
    #     'beacukai.tpb', related="reference.tpb_source_id")
    # tpb_dest_id = fields.Many2one(
    #     'beacukai.tpb', related="reference.tpb_dest_id")

    # get from many2one parent
    """not used"""
    no_bukti_penerimaan_barang = fields.Char(
        'Nomor Bukti Penerimaan Barang', related="reference.delivery_note_number.name")
    tgl_bukti_penerimaan_barang = fields.Datetime(
        'Tgl Bukti Penerimaan Barang', related="reference.delivery_note_date")
    pengirim = fields.Many2one(
        'res.partner', 'Pengirim', related="reference.po_id.partner_id")
    invoice_id = fields.Many2one(
        'account.invoice', related="reference.invoice_number")
    order_id = fields.Many2one('purchase.order', string='Order Reference', ondelete='cascade')

    received_qty = fields.Float(compute="_get_received_qty", string="Received Qty", digits=dp.get_precision('Product Unit of Measure'))
    
    @api.depends('reference.picking_ids')
    def _get_received_qty(self):
        for res in self:
            received_qty = 0
            if res.reference.picking_ids:
                for picking in res.reference.picking_ids:
                    for pack in picking.pack_operation_product_ids:
                        if pack.product_id.id == res.product_id.id:
                            received_qty += pack.qty_done
                            
            res.received_qty = received_qty

    # location_dest_id = fields.Many2one(
    #     'stock.location', 'Location', compute="_get_location_dest", store=True)
    # location_trigger = fields.Boolean('Trigger Location', default=False)
    # location_dest_id = fields.Many2one('stock.location', 'Location')

    # @api.one
    # def generate_loc(self):
    #     for res in self:
    #         if res.location_trigger == False:
    #             res.location_trigger = True
    #         else:
    #             res.location_trigger = False

    # @api.depends('location_trigger', 'move_ids')
    # def _get_location_dest(self):
    #     for res in self:
    #         loc = int(self.env['ir.config_parameter'].get_param(
    #             'location_wip', default=''))
    #         location_id = self.env['stock.location'].browse(loc)
    #         # for each in res.move_ids:
    #         #     if each.location_dest_id == location_id:
    #         #         res.location_dest_id = each.location_dest_id.id
    #         move_ids = self.env['stock.move'].search([('location_dest_id', '=', loc),
    #                                                   ('state', '=', 'done'),
    #                                                   ('picking_id.beacukai_incoming_23_id', '=', res.reference.id)])
    #         for move in move_ids:
    #             res.location_dest_id = move.location_dest_id.id

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for res in self:
            res.product_uom_id = res.product_id.uom_id.id

    @api.depends('product_incost', 'reference.cif_cost', 'biaya_tambahan', 'product_qty', 'reference.ndpbm')
    def _get_product_cif(self):
        for res in self:            
            product_discount = res.product_incost / (res.reference.cif_cost or 1) * res.biaya_tambahan
            product_price_invoice = res.product_incost - product_discount
            product_price_qty = product_price_invoice / (res.product_qty or 1)
            cif_cost = product_price_invoice
            cif_amount = cif_cost * res.reference.ndpbm

            res.product_discount = product_discount
            res.product_price_invoice = product_price_invoice
            res.product_price_qty = product_price_qty
            res.cif_cost = cif_cost
            res.cif_amount = cif_amount

    # @api.depends('product_qty', 'product_price')
    # def _get_product_amount(self):
    #     for res in self:
    #         res.product_amount = (res.product_qty or 0.0) * \
    #             (res.product_price or 0.0)
    #         res.saldo = res.product_qty
