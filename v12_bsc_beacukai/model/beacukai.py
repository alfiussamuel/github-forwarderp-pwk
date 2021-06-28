import time
import re
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError, except_orm, Warning, RedirectWarning, ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import odoo.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)


#""""""""""""""""""""""""""""""""""""" MASTER DATA """""""""""""""""""""""""""""""""""""
# class BeacukaiConfig(models.Model):
#     _name = "beacukai.config"
#     _rec_name= 'kode'

#     kode = fields.Selection([('Bahan Baku dan Bahan Penolong','Bahan Baku dan Bahan Penolong'),('Barang Jadi','Barang Jadi'),('Mesin dan Peralatan','Mesin dan Peralatan'),('Reject dan Scrap','Reject dan Scrap')], string='Laporan Pertanggungjawaban')
#     location_id = fields.Many2one('stock.location', 'Lokasi', domain="[('usage','=','internal')]")
#     location_bahanbakupenolong = fields.Many2one('stock.location', 'Bahan Baku dan Bahan Penolong', domain="[('usage','=','internal')]")
#     location_barangjadi = fields.Many2one('stock.location', 'Barang Jadi', domain="[('usage','=','internal')]")
#     location_mesindanperalatan = fields.Many2one('stock.location', 'Mesin dan Peralatan', domain="[('usage','=','internal')]")
#     location_reject = fields.Many2one('stock.location', 'Reject dan Scrap', domain="[('usage','=','internal')]")

PARAMS = [
    ('location_bahanbakupenolong'),
    ('location_barangjadi'),
    ('location_mesindanperalatan'),
    ('location_reject'),
]


class BeacukaiConfig(models.TransientModel):
    _name = "beacukai.config.location"
    _inherit = 'res.config.settings'
    location_bahanbakupenolong = fields.Many2one(
        'stock.location', 'Bahan Baku dan Bahan Penolong', domain="[('usage','=','internal')]")
    location_barangjadi = fields.Many2one(
        'stock.location', 'Barang Jadi', domain="[('usage','=','internal')]")
    location_mesindanperalatan = fields.Many2one(
        'stock.location', 'Mesin dan Peralatan', domain="[('usage','=','internal')]")
    location_reject = fields.Many2one(
        'stock.location', 'Reject dan Scrap', domain="[('usage','=','internal')]")
    location_wip = fields.Many2one(
        'stock.location', 'WIP', domain="[('usage','=','internal')]")

    @api.multi
    def set_beacukai_config(self):
        self.env['ir.config_parameter'].set_param(
            'location_bahanbakupenolong', (self.location_bahanbakupenolong.id))
        self.env['ir.config_parameter'].set_param(
            'location_barangjadi', (self.location_barangjadi.id))
        self.env['ir.config_parameter'].set_param(
            'location_mesindanperalatan', (self.location_mesindanperalatan.id))
        self.env['ir.config_parameter'].set_param(
            'location_reject', (self.location_reject.id))
        self.env['ir.config_parameter'].set_param(
            'location_wip', (self.location_wip.id))

    def get_default_beacukai_config(self, fields):
        val = {}
        val['location_bahanbakupenolong'] = int(
            self.env['ir.config_parameter'].get_param('location_bahanbakupenolong'))
        val['location_barangjadi'] = int(
            self.env['ir.config_parameter'].get_param('location_barangjadi'))
        val['location_mesindanperalatan'] = int(
            self.env['ir.config_parameter'].get_param('location_mesindanperalatan'))
        val['location_reject'] = int(
            self.env['ir.config_parameter'].get_param('location_reject'))
        val['location_wip'] = int(
            self.env['ir.config_parameter'].get_param('location_wip'))
        return dict(location_bahanbakupenolong=val['location_bahanbakupenolong'], location_barangjadi=val['location_barangjadi'], location_mesindanperalatan=val['location_mesindanperalatan'], location_reject=val['location_reject'], location_wip=val['location_wip'])


class BeacukaiTpb(models.Model):
    _name = "beacukai.tpb"
    _rec_name = 'office'

    name = fields.Char('Kode')
    office = fields.Char('Kantor')
    jabatan = fields.Char('Jabatan')
    type = fields.Char('Type')


class BeacukaiApiu(models.Model):
    _name = "beacukai.apiu"

    name = fields.Char('Nama Kryawan')
    employee_no = fields.Char('No Karyawan')
    jabatan = fields.Char('Jabatan')
    employee_id = fields.Char('No KTP/IMTA')


class BeacukaiDocumentType(models.Model):
    _name = "beacukai.document.type"

    name = fields.Char('Tipe Dokumen')
    document_type = fields.Selection([
        ('incoming', 'Pemasukan'),
        ('outgoing', 'Pengeluaran')
    ], string='Tipe Dokumen', default='incoming')


class BeacukaiDeliveryPurpose(models.Model):
    _name = "beacukai.delivery.purpose"

    name = fields.Char('Tujuan Pengiriman')

# """"""""""""""""""""""""""""""""""""" MASTER DATA """""""""""""""""""""""""""""""""""""


# """"""""""""""""""""""""""""""""""""" TRANSACTION """""""""""""""""""""""""""""""""""""

class BeacukaiIncomingLine(models.Model):
    _name = "beacukai.incoming.line"
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

    # id_header = fields.Char(string="ID Header")
    reference = fields.Many2one('beacukai.incoming',string='Reference',index=True, ondelete='cascade')
    submission_no = fields.Char(related='reference.submission_no',
                                readonly=True)
    date = fields.Date(related='reference.date',
                       readonly=True)
    product_id = fields.Many2one('product.product', 'Kode Barang')
    product_code = fields.Char('Kode Barang', related="product_id.name")
    product_name = fields.Char('Nama Barang')
    product_hs_code = fields.Char('HS Code')
    product_qty = fields.Float('Qty')
    saldo = fields.Float('Saldo')
    product_uom_id = fields.Many2one('product.uom', 'Satuan')
    product_price = fields.Float('Harga')
    product_amount = fields.Float(
        compute="_get_product_amount", string='Jumlah')
    product_incost = fields.Float('FOB')
    product_freight = fields.Float('Freight')
    product_bruto = fields.Float('Bruto')
    product_netto = fields.Float('Netto')
    move_ids = fields.One2many('stock.move', 'bc_incoming_line_id',
                               string='BC Incoming Line', readonly=True, ondelete='set null', copy=False)
    outgoing_ids = fields.One2many('beacukai.outgoing.line', 'incoming_line_id',
                                   string='BC Outgoing', readonly=True, ondelete='set null', copy=False)
    submission_no = fields.Char(related='reference.submission_no')
    document_type_id = fields.Char(related='reference.document_type_id.name')
    register_number = fields.Char(related='reference.register_number')
    register_date = fields.Date(related='reference.register_date')
    # date = fields.Date(related='reference.date')
    # delivery_note_number = fields.Integer(related='reference.delivery_note_number.name')
    delivery_note_date = fields.Datetime(
        related='reference.delivery_note_date')
    currency_id = fields.Many2one(
        "res.currency", related='product_id.currency_id')

    tpb_source_id = fields.Many2one(
        'beacukai.tpb', related="reference.tpb_source_id")
    tpb_dest_id = fields.Many2one(
        'beacukai.tpb', related="reference.tpb_dest_id")
    biaya_tambahan = fields.Float(string='Biaya Tambahan')
    cif = fields.Float(string='CIF')

    ###get from many2one parent ###
    no_bukti_penerimaan_barang = fields.Char(
        'Nomor Bukti Penerimaan Barang', related="reference.delivery_note_number.name")
    tgl_bukti_penerimaan_barang = fields.Datetime(
        'Tgl Bukti Penerimaan Barang', related="reference.delivery_note_date")
    # pengirim = fields.Many2one(
    #     'res.partner', 'Pengirim', related="reference.po_id.partner_id")
    pengirim = fields.Char('Pengirim',related="reference.po_id.partner_id.name")
    invoice_id = fields.Many2one(
        'account.invoice', related="reference.invoice_number")
    location_dest_id = fields.Many2one(
        'stock.location', 'Location', compute="_get_location_dest", store=True)
    location_trigger = fields.Boolean('Trigger Location', default=False)
    # location_dest_id = fields.Many2one('stock.location','Location')

    @api.one
    def generate_loc(self):
        for res in self:
            if res.location_trigger == False:
                res.location_trigger = True
            else:
                res.location_trigger = False

    @api.depends('location_trigger', 'move_ids')
    def _get_location_dest(self):
        for res in self:
            loc = int(self.env['ir.config_parameter'].get_param('location_wip'))
            location_id = self.env['stock.location'].browse(loc)
            # for each in res.move_ids:
            #     if each.location_dest_id == location_id:
            #         res.location_dest_id = each.location_dest_id.id
            move_ids = self.env['stock.move'].search([('location_dest_id', '=', loc),
                                                      ('state', '=', 'done'),
                                                      ('picking_id.beacukai_incoming_id', '=', res.reference.id)])
            for move in move_ids:
                res.location_dest_id = move.location_dest_id.id

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for res in self:
            res.product_name = res.product_id.product_tmpl_id.default_code
            res.product_hs_code = res.product_id.product_tmpl_id.hs_code
            res.product_uom_id = res.product_id.uom_id.id

    @api.depends('product_qty', 'product_price')
    def _get_product_amount(self):
        for res in self:
            res.product_amount = (res.product_qty or 0.0) * \
                (res.product_price or 0.0)
            res.saldo = res.product_qty


class BcIncomingRegisterNumber(models.TransientModel):
    _name = 'bc.incoming.register.number'
    register_number = fields.Char('No Daftar')
    register_date = fields.Date('Tanggal Daftar')
    incoming_id = fields.Many2one('beacukai.incoming', 'Incoming Document')
    incoming23_id = fields.Many2one('beacukai.incoming.23', 'Incoming Document 23')

    @api.multi
    def input_registrasi(self):
        _logger.info('incoming2')
        _logger.info(self.incoming_id)
        if self.incoming_id:
            self.incoming_id.write({
                'register_number': self.register_number,
                'register_date': self.register_date,
                'state': 'registrasi'
            })
        if self.incoming23_id:
            self.incoming23_id.write({
                'register_number': self.register_number,
                'register_date': self.register_date,
                'state': 'registrasi'
                })
        return True


class BeacukaiIncoming(models.Model):
    _name = "beacukai.incoming"
    _inherit = ['mail.thread']
    _order = "id desc"
    _rec_name = "submission_no"

    @api.multi
    def action_confirm(self):
        for incoming in self:
            _logger.info('incoming')
            _logger.info(incoming.id)
            view_id = self.env['bc.incoming.register.number']
            new = view_id.create({'incoming_id': incoming.id})
            return {
                'type': 'ir.actions.act_window',
                'name': 'Input Nomor Registasi',
                'res_model': 'bc.incoming.register.number',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': new.id,
                'view_id': self.env.ref('v10_bsc_beacukai.view_beacukai_input_register_number').id,
                'target': 'new',
            }

    @api.multi
    def bc_action_view_picking(self):
        '''
        This function returns an action that display existing picking orders of given purchase order ids.
        When only one found, show the picking immediately.
        '''
        action = self.env.ref('stock.action_picking_tree')
        result = action.read()[0]

        # override the context to get rid of the default filtering on picking type
        result.pop('id', None)
        result['context'] = {}
        pick_ids = sum([order.picking_ids.ids for order in self], [])
        # choose the view_mode accordingly
        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',[" + \
                ','.join(map(str, pick_ids)) + "])]"
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids and pick_ids[0] or False
        return result

    @api.depends('picking_ids', 'picking_ids.state')
    def _compute_is_shipped(self):
        for order in self:
            if order.picking_ids and all([x.state == 'done' for x in order.picking_ids]):
                order.is_shipped = True
                order.state = 'done'

    name = fields.Char('Document No.')
    line_ids = fields.One2many('beacukai.incoming.line', 'reference', 'Lines')
    picking_id = fields.Many2one('stock.picking', 'Shipment Document')

    """ Header """
    id_header = fields.Char(string="ID Header")
    submission_no = fields.Char('No Aju')
    document_type_id = fields.Many2one('beacukai.document.type', 'Tipe')
    tpb_source_id = fields.Many2one('beacukai.tpb', 'TPB Awal')
    apiu_id = fields.Many2one('beacukai.apiu', 'Pengusaha TPB')
    register_number = fields.Char('No Pendaftaran')
    register_date = fields.Date('Tanggal Daftar')
    tpb_dest_id = fields.Many2one('beacukai.tpb', 'TPB Akhir')
    date = fields.Date('Tanggal Aju')
    delivery_purpose_id = fields.Many2one(
        'beacukai.delivery.purpose', 'Tujuan Pengiriman')

    """ Notification Data """
    company_npwp = fields.Char(
        'NPWP', default=lambda self: self.env.user.company_id.vat, readonly=True)
    company_name = fields.Char(
        'Nama Perusahaan', default=lambda self: self.env.user.company_id.name, readonly=True)
    company_address = fields.Text(
        'Alamat Perusahaan', default=lambda self: self.env.user.company_id.street, readonly=True)
    company_permission_no = fields.Char(
        'Izin Perusahaan', readonly=True, default=lambda self: self.env['ir.config_parameter'].get_param('no_tpb'))
    supplier_id = fields.Many2one('res.partner', 'Nama Vendor')

    """ Complement Documents """
    fbl_awb_number = fields.Char('FBL/AWB No.')
    fbl_awb_date = fields.Date('FBL/AWB Tanggal')
    delivery_note_number = fields.Many2one('stock.picking', 'Nomor Pengiriman')
    delivery_note_date = fields.Datetime(
        related='delivery_note_number.min_date')
    invoice_number = fields.Many2one('account.invoice', 'Nomor Invoice')
    invoice_date = fields.Date(related='invoice_number.date_invoice')
    decree_number = fields.Char('No. Decree')
    decree_date = fields.Date('Tanggal Decree')
    contract_number = fields.Char('No. Kontrak')
    contract_date = fields.Date('Tanggal Kontrak')
    packing_list_number = fields.Char('No. Packing')
    packing_list_date = fields.Date('Tanggal Packing')
    other = fields.Char('Lainnya')
    finish_date = fields.Datetime('Tanggal Selesai')
    external_shipment_number = fields.Char('External Shipment Number')

    """ Trade Data """
    currency_id = fields.Many2one('res.currency', 'Mata Uang')
    npdbm = fields.Float('NPDBM')
    amount_usd = fields.Float('Jumlah USD')
    amount_idr = fields.Float('Jumlah IDR')

    """ Packaging Data """
    packing_number = fields.Char('No Packing dan Merek')
    packaging_number = fields.Float('Nomor dan Tipe Packaging')
    packaging_type = fields.Many2one(
        'product.uom', 'Number and Type Packaging')
    picking_count = fields.Integer(
        compute='_compute_picking', string='Receptions', default=0)
    is_shipped = fields.Boolean(compute="_compute_is_shipped")
    po_id = fields.Many2one('purchase.order', 'No PO')
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Alur Ke Gudang',
        required=False,
        help="Picking Type determines the way the picking should be shown in the view, reports, ...")

    category_product = fields.Selection([('lokal', 'Lokal'),
                                         ('import', 'Import')], 'Category', default="lokal")

    # #########DION###
    # tgl_bukti_penerimaan_barang = fields.Date('Tgl Bukti Penerimaan Barang')
    # no_bukti_penerimaan_barang = fields.Char('Nomor Bukti Penerimaan Barang')
    # product_id = fields.Many2one('product.product','Nama Product')
    # product_code = fields.Char('Kode Barang')
    # pengirim = fields.Many2one('res.partner','Pengirim')
    # product_qty = fields.Float('Jumlah')
    # product_uom = fields.Many2one('product.uom','Satuan')
    # amount = fields.Float('Nilai Barang')

    picking_ids = fields.Many2many(
        'stock.picking', compute='_compute_picking', string='Receptions', copy=False)
    state = fields.Selection([
        ('pengajuan', 'Pengajuan'),
        ('registrasi', 'Registrasi'),
        ('terima', 'Penerimaan Barang'),
        ('done', 'Selesai'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='pengajuan')

    efaktur_number = fields.Char('E-Faktur')

    @api.multi
    def push_to_ceisa(self):
        raise Warning('Under Construction')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'beacukai.incoming') or 'New'
        return super(BeacukaiIncoming, self).create(vals)

    # @api.onchange('product_id')
    # def onchange_product_id(self):
    #     for res in self:
    #         res.product_code = res.product_id.default_code

    @api.multi
    def action_done(self):
        self._compute_is_shipped()
        _logger.info('is shipped')
        _logger.info(self.is_shipped)
        if self.finish_date != '':
            return self.write({'state': 'done', 'finish_date': fields.Date.today()})
        else:
            raise UserError(
                _('Pastikan penerimaan barang telah selesai dan telah menginput finish date'))

    @api.depends('line_ids.move_ids')
    def _compute_picking(self):
        for order in self:
            pickings = self.env['stock.picking']
            for line in order.line_ids:
                # We keep a limited scope on purpose. Ideally, we should also use move_orig_ids and
                # do some recursive search, but that could be prohibitive if not done correctly.
                moves = line.move_ids | line.move_ids.mapped(
                    'returned_move_ids')
                moves = moves.filtered(lambda r: r.state != 'cancel')
                pickings |= moves.mapped('picking_id')
            order.picking_ids = pickings
            order.picking_count = len(pickings)

    @api.multi
    def action_receive(self):
        # picking_type = self.env['stock.picking.type'].search([('name','=','dokumen_penerimaan')],limit=1)

        for bcmove in self:
            if bcmove.category_product == 'lokal':
                bcmove.state = 'done'
            else:
                _logger.info('picking test')
                if bcmove.picking_type_id.default_location_dest_id.id:
                    dst = bcmove.picking_type_id.default_location_dest_id.id
                else:
                    dst = self.default_location_dest_id = self.env.ref(
                        'stock.stock_location_stock').id
                if bcmove.picking_type_id.default_location_src_id.id:
                    src = bcmove.picking_type_id.default_location_src_id.id
                else:
                    src = self.env.ref('stock.stock_location_suppliers').id
                _logger.info(self.env.ref(
                    'stock.stock_location_suppliers').name)
                _logger.info(dst)
                stok = self.env['stock.picking'].create({
                    'move_type': 'direct',
                    'picking_type_id': bcmove.picking_type_id.id,
                    'is_beacukai_incoming': True,
                    'beacukai_incoming_id': bcmove.id,
                    'origin': bcmove.submission_no,
                    'location_id': src,
                    'location_dest_id': dst,
                    'min_date': datetime.now()
                })
                if bcmove.line_ids:
                    _logger.info(bcmove.line_ids)
                    for line in bcmove.line_ids:
                        pack_operation_product_ids = {
                            'picking_id': stok.id,
                            'bc_incoming_line_id': line.id,
                            'product_id': line.product_id.id,
                            'product_uom_qty': line.product_qty,
                            'product_uom': line.product_uom_id.id,
                            'name': bcmove.name,
                            'date_expected': bcmove.date,
                            'location_id': src,
                            'location_dest_id': dst
                        }
                        stok.move_lines.create(pack_operation_product_ids)
            # for bcmove in self:
            #     stok = self.env['stock.picking'].create({
            #             'move_type' : 'direct',
            #             'picking_type_id' : bcmove.picking_type_id.id,
            #             'is_beacukai_incoming' : True,
            #             'beacukai_incoming_id' : bcmove.id,
            #             'origin' : bcmove.submission_no,
            #             'location_id' : bcmove.picking_type_id.default_location_src_id.id,
            #             'location_dest_id' : bcmove.picking_type_id.default_location_dest_id.id
            #         })
            #     if bcmove.line_ids:
            #         _logger.info(bcmove.line_ids)
            #         for line in bcmove.line_ids:
            #             pack_operation_product_ids = {
            #                 'picking_id' : stok.id,
            #                 'bc_incoming_line_id' : line.id,
            #                 'product_id' : line.product_id.id,
            #                 'product_uom_qty' : line.product_qty,
            #                 'product_uom' : line.product_uom_id.id,
            #                 'name' : bcmove.name,
            #                 'date_expected' : bcmove.date,
            #                 'location_id' : bcmove.picking_type_id.default_location_src_id.id,
            #                 'location_dest_id' : bcmove.picking_type_id.default_location_dest_id.id
            #             }
            #             stok.move_lines.create(pack_operation_product_ids)
            # return True
                return self.write({'state': 'terima'})


class BeacukaiOutgoingLine(models.Model):
    _name = "beacukai.outgoing.line"
    _rec_name = "reference"

    reference = fields.Many2one('beacukai.outgoing', 'Reference')
    date = fields.Date(related='reference.date',
                       readonly=True)
    incoming_line_id = fields.Many2one(
        'beacukai.incoming.line', 'Data Penerimaan')
    incoming_line_23_id = fields.Many2one(
        'beacukai.incoming.line.23', 'Data Penerimaan BC23')
    product_id = fields.Many2one('product.product', 'Kode Barang')
    product_code = fields.Char(related='product_id.default_code')
    product_name = fields.Char('Kode Barang')
    product_hs_code = fields.Char('HS Code')
    product_qty = fields.Float('Qty')
    product_uom_id = fields.Many2one('product.uom', 'Satuan')
    product_price = fields.Float('Harga Barang')
    product_amount = fields.Float(
        compute="_get_product_amount", string='Jumlah')
    product_incost = fields.Float('In Cost')
    product_freight = fields.Float('Freight')
    product_bruto = fields.Float('Bruto')
    product_netto = fields.Float('Netto')
    move_ids = fields.One2many('stock.move', 'bc_outgoing_line_id',
                               string='Daftar Barang Pengeluaran', readonly=True, ondelete='set null', copy=False)
    qty_available = fields.Float('Stok Saat Ini')
    submission_no = fields.Char(related='reference.submission_no')
    document_type_id = fields.Char(related='reference.document_type_id.name')
    register_number = fields.Char(related='reference.register_number')
    register_date = fields.Date(related='reference.register_date')
    date = fields.Date(related='reference.date')
    # delivery_note_number = fields.Integer(related='reference.delivery_note_number.name')
    delivery_note_date = fields.Datetime(
        related='reference.delivery_note_date')
    currency_id = fields.Char(related='reference.currency_id.name')

    no_bukti_penerimaan_barang = fields.Char(
        'Nomor Bukti Penerimaan Barang', related="reference.delivery_note_number.name")
    tgl_bukti_penerimaan_barang = fields.Datetime(
        'Tgl Bukti Penerimaan Barang', related="reference.delivery_note_date")
    penerima = fields.Many2one('res.partner', 'Penerima')
    invoice_id = fields.Many2one(
        'account.invoice', related="reference.invoice_number")
    """ERROR"""
    manufacturing_order = fields.Many2one('mrp.production', 'MO')
    mo_line = fields.One2many(
        related='manufacturing_order.move_raw_ids', string='MO Lines')
    raw_source = fields.Selection([
        ('lokal', 'Lokal'),
        ('import', 'Import'),
    ], string='Sumber Material')
    date_expected = fields.Datetime('Expected Date')

    @api.onchange('raw_source')
    def _onchange_rs(self):
        res = {}
        if self.raw_source == 'lokal':
            res['domain'] = {'incoming_line_id': [
                ('reference.document_type_id.name', '=', '4.0')]}
        elif self.raw_source == 'import':
            res['domain'] = {'incoming_line_id': [
                ('reference.document_type_id.name', '=', '2.3')]}

        return res

    # @api.onchange('incoming_line_id')
    # def _onchange_incoming_line_id(self):
    #     for res in self:
    #         res.product_id = res.incoming_line_id.product_id.product_tmpl_id.id
    #         res.product_name = res.product_id.product_tmpl_id.default_code
    #         res.product_hs_code = res.product_id.product_tmpl_id.hs_code
    #         res.product_uom_id = res.product_id.uom_id.id

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for res in self:
            res.incoming_line_id = ''
            res.product_name = res.product_id.product_tmpl_id.default_code
            res.product_hs_code = res.product_id.product_tmpl_id.hs_code
            res.product_uom_id = res.product_id.uom_id.id
            res.qty_available = res.product_id.qty_available
            return {'domain': {'incoming_line_id': [('product_id', '=', res.product_id.id if res.product_id.qty_available > 0 else False)]}}

    @api.depends('product_qty', 'product_price')
    def _get_product_amount(self):
        for res in self:
            res.product_amount = (res.product_qty or 0.0) * \
                (res.product_price or 0.0)


class BcOutgoingRegisterNumber(models.TransientModel):
    _name = 'bc.outgoing.register.number'
    register_number = fields.Char('No Daftar')
    register_date = fields.Date('Tanggal Daftar')
    outgoing_id = fields.Many2one('beacukai.outgoing', 'Outgoing Document')

    @api.multi
    def input_registrasi(self):
        self.outgoing_id.write({
            'register_number': self.register_number,
            'register_date': self.register_date,
            'state': 'registrasi'
        })
        return True


class BeacukaiOutgoing(models.Model):
    _name = "beacukai.outgoing"
    _inherit = ['mail.thread']
    _order = "id desc"

    @api.multi
    def action_confirm(self):
        for outgoing in self:
            view_id = self.env['bc.outgoing.register.number']
            new = view_id.create({'outgoing_id': outgoing.id})
            return {
                'type': 'ir.actions.act_window',
                'name': 'Input Nomor Registasi',
                'res_model': 'bc.outgoing.register.number',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': new.id,
                'view_id': self.env.ref('v10_bsc_beacukai.view_beacukai_input_register_number_out').id,
                'target': 'new',
            }

    @api.multi
    def bc_action_view_picking(self):
        '''
        This function returns an action that display existing picking orders of given purchase order ids.
        When only one found, show the picking immediately.
        '''
        action = self.env.ref('stock.action_picking_tree')
        result = action.read()[0]

        # override the context to get rid of the default filtering on picking type
        result.pop('id', None)
        result['context'] = {}
        pick_ids = sum([order.picking_ids.ids for order in self], [])
        # choose the view_mode accordingly
        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',[" + \
                ','.join(map(str, pick_ids)) + "])]"
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids and pick_ids[0] or False
        return result

    @api.depends('line_ids.move_ids')
    def _compute_picking(self):
        for order in self:
            pickings = self.env['stock.picking']
            for line in order.line_ids:
                # We keep a limited scope on purpose. Ideally, we should also use move_orig_ids and
                # do some recursive search, but that could be prohibitive if not done correctly.
                moves = line.move_ids | line.move_ids.mapped(
                    'returned_move_ids')
                moves = moves.filtered(lambda r: r.state != 'cancel')
                pickings |= moves.mapped('picking_id')
            order.picking_ids = pickings
            order.picking_count = len(pickings)

    @api.depends('picking_ids', 'picking_ids.state')
    def _compute_is_shipped(self):
        for order in self:
            if order.picking_ids and all([x.state == 'done' for x in order.picking_ids]):
                order.is_shipped = True
                order.state = 'done'

    name = fields.Char('No Dokumen')
    line_ids = fields.One2many('beacukai.outgoing.line', 'reference', 'Lines')
    picking_id = fields.Many2one('stock.picking', 'Dokumen Pengiriman')

    """ Header """
    submission_no = fields.Char('No. Aju')
    document_type_id = fields.Many2one(
        'beacukai.document.type', 'Tipe Bea Cukai')
    tpb_source_id = fields.Many2one('beacukai.tpb', 'TPB Awal')
    apiu_id = fields.Many2one('beacukai.apiu', 'Pengusaha TPB')
    register_number = fields.Char('No Pendaftaran')
    register_date = fields.Date('Tanggal Daftar')
    tpb_dest_id = fields.Many2one('beacukai.tpb', 'TPB Akhir')
    date = fields.Date('Tanggal Aju')
    delivery_purpose_id = fields.Many2one(
        'beacukai.delivery.purpose', 'Tujuan Pengiriman')

    """ Notification Data """
    company_npwp = fields.Char(
        'NPWP', default=lambda self: self.env.user.company_id.vat, readonly=True)
    company_name = fields.Char(
        'Nama Perusahaan', default=lambda self: self.env.user.company_id.name, readonly=True)
    company_address = fields.Text(
        'Alamat Perusahaan', default=lambda self: self.env.user.company_id.street, readonly=True)
    company_permission_no = fields.Char(
        'Izin Perusahaan', readonly=True, default=lambda self: self.env['ir.config_parameter'].get_param('no_tpb'))
    supplier_id = fields.Many2one('res.partner', 'Nama Vendor')

    """ Complement Documents """
    fbl_awb_number = fields.Char('Nomor FBL/AWB')
    fbl_awb_date = fields.Date('Tanggal FBL/AWB')
    delivery_note_number = fields.Many2one('stock.picking', 'Nomor Pengiriman')
    delivery_note_date = fields.Datetime(
        related='delivery_note_number.min_date')
    invoice_number = fields.Many2one('account.invoice', 'Nomor Invoice')
    invoice_date = fields.Date('Tanggal Invoice')
    decree_number = fields.Char('Nomor Decree')
    decree_date = fields.Date('Tanggal Decree')
    contract_number = fields.Char('No Kontrak')
    contract_date = fields.Date('Tanggal Kontrak')
    packing_list_number = fields.Char('Nomor Packing List')
    packing_list_date = fields.Date('Tanggal Packing List')
    other = fields.Char('Lainnya')
    finish_date = fields.Datetime('Tanggal Selesai')
    out_date = fields.Datetime('Tanggal Keluar')

    """ Trade Data """
    currency_id = fields.Many2one('res.currency', 'Currency')
    npdbm = fields.Float('NPDBM')
    amount_usd = fields.Float('Amount USD')
    amount_idr = fields.Float('Amount IDR')

    """ Packaging Data """
    packing_number = fields.Char('Nomor Packing dan Merk')
    packaging_number = fields.Float('Nomor dan Tipe Packaging')
    packaging_type = fields.Many2one(
        'product.uom', 'Number and Type Packaging')

    """ Assurance Data """
    assurance_bm = fields.Float('BM')
    assurance_cukai = fields.Float('Cukai')
    assurance_ppn = fields.Float('PPN')
    assurance_ppnbm = fields.Float('PPnBM')
    assurance_pph = fields.Float('PPH')
    assurance_pnbp = fields.Float('PNPB')
    assurance_tax = fields.Float('Total Pajak')
    assurance_warranty_type = fields.Char('Tipe Garansi')
    assurance_warranty_no = fields.Char('Nomor Garansi')
    assurance_warranty_date = fields.Date('Tanggal Garansi')
    assurance_warranty_amount = fields.Float('Jumlah Garansi')
    assurance_warranty_due_date = fields.Date('Tanggal Selesai Garansi')
    assurance_warranty_warrantor = fields.Char('Pemberi Garansi')
    picking_count = fields.Integer(
        compute='_compute_picking', string='Receptions', default=0)
    is_shipped = fields.Boolean(compute="_compute_is_shipped")
    picking_ids = fields.Many2many(
        'stock.picking', compute='_compute_picking', string='Receptions', copy=False)
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Alur Ke Gudang',
        required=False,
        help="Picking Type determines the way the picking should be shown in the view, reports, ...")
    state = fields.Selection([
        ('pengajuan', 'Pengajuan'),
        ('registrasi', 'Registrasi'),
        ('terima', 'Pengiriman Barang'),
        ('done', 'Selesai'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='pengajuan')

    efaktur_number = fields.Char('E-Faktur')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'beacukai.outgoing') or '/'
        return super(BeacukaiOutgoing, self).create(vals)

    @api.multi
    def action_done(self):
        self._compute_is_shipped()
        _logger.info('is shipped')
        _logger.info(self.is_shipped)
        if self.finish_date != '':
            return self.write({'state': 'done', 'finish_date': fields.Date.today()})
        else:
            raise UserError(
                _('Pastikan pengiriman barang telah selesai dan telah menginput finish date'))
    # @api.multi
    # def action_confirm(self):
    #     return self.write({'state': 'registrasi'})

    @api.multi
    def action_receive(self):
        # picking_type = self.env['stock.picking.type'].search([('name','=','dokumen_pengeluaran')],limit=1)

        for bcmove in self:
            _logger.info('picking test')
            test = self.default_location_src_id = self.env.ref(
                'stock.stock_location_customers').id
            if bcmove.picking_type_id.default_location_dest_id.id:
                dst = bcmove.picking_type_id.default_location_dest_id.id
            else:
                dst = self.default_location_src_id = self.env.ref(
                    'stock.stock_location_customers').id
            if bcmove.picking_type_id.default_location_src_id.id:
                src = bcmove.picking_type_id.default_location_src_id.id
            else:
                src = self.default_location_dest_id = self.env.ref(
                    'stock.stock_location_stock').id
            _logger.info(src)
            _logger.info(dst)
            stok = self.env['stock.picking'].create({
                'move_type': 'direct',
                'picking_type_id': bcmove.picking_type_id.id,
                'is_beacukai_outgoing': True,
                'beacukai_outgoing_id': bcmove.id,
                'origin': bcmove.submission_no,
                'location_id': src,
                'location_dest_id': dst
            })
            if bcmove.line_ids:
                _logger.info(bcmove.line_ids)
                for line in bcmove.line_ids:
                    pack_operation_product_ids = {
                        'picking_id': stok.id,
                        'bc_outgoing_line_id': line.id,
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.product_qty,
                        'product_uom': line.product_uom_id.id,
                        'name': bcmove.name,
                        'date_expected': bcmove.date,
                        'location_id': src,
                        'location_dest_id': dst
                    }
                    stok.move_lines.create(pack_operation_product_ids)
        # return True
        return self.write({'state': 'terima'})


""""""""""""""""""""""""""""""""""""" TRANSACTION """""""""""""""""""""""""""""""""""""


class LaporanPosisiWIP(models.Model):
    _name = "laporan.posisi.wip"
    _inherit = ['mail.thread']
    _order = "id desc"

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[' + str(record.reference.submission_no) + ']' + '[' + str(
                record.reference.register_number) + ']'+'[' + str(record.product_qty) + ']'
            # name = self.reference.submission_no
            result.append((record.id, name))
        return result

    reference = fields.Many2one('beacukai.incoming', 'Reference')
    submission_no = fields.Char(related='reference.submission_no',
                                readonly=True)
    date = fields.Date(related='reference.date',
                       readonly=True)
    product_id = fields.Many2one('product.product', 'Kode Barang')
    product_code = fields.Char(
        'Kode Barang', related="product_id.default_code")
    product_name = fields.Char('Nama Barang', related="product_id.name")
    product_hs_code = fields.Char('HS Code', related="product_id.hs_code")
    product_qty = fields.Float('Qty')
    saldo = fields.Float('Saldo')
    product_uom_id = fields.Many2one('product.uom', 'Satuan')
    product_price = fields.Float('Harga')
    product_amount = fields.Float(
        compute="_get_product_amount", string='Jumlah')
    product_incost = fields.Float('In Cost')
    product_freight = fields.Float('Freight')
    product_bruto = fields.Float('Bruto')
    product_netto = fields.Float('Netto')
    # move_ids = fields.One2many('stock.move', 'bc_incoming_line_id', string='BC Incoming Line', readonly=True, ondelete='set null', copy=False)
    move_ids_wip = fields.One2many('stock.move', 'laporan_posisi_wip_id',
                                   string='BC Incoming Line', readonly=True, ondelete='set null', copy=False)
    outgoing_ids = fields.One2many('beacukai.outgoing.line', 'incoming_line_id',
                                   string='BC Outgoing', readonly=True, ondelete='set null', copy=False)
    submission_no = fields.Char(related='reference.submission_no')
    document_type_id = fields.Char(related='reference.document_type_id.name')
    register_number = fields.Char(related='reference.register_number')
    register_date = fields.Date(related='reference.register_date')
    date = fields.Date(related='reference.date')
    # delivery_note_number = fields.Integer(related='reference.delivery_note_number.name')
    delivery_note_date = fields.Datetime(
        related='reference.delivery_note_date')
    currency_id = fields.Many2one(
        "res.currency", related='product_id.currency_id')

    tpb_source_id = fields.Many2one(
        'beacukai.tpb', related="reference.tpb_source_id")
    tpb_dest_id = fields.Many2one(
        'beacukai.tpb', related="reference.tpb_dest_id")

    ###get from many2one parent ###
    no_bukti_penerimaan_barang = fields.Char('Nomor Bukti Penerimaan Barang')
    tgl_bukti_penerimaan_barang = fields.Date('Tgl Bukti Penerimaan Barang')
    # pengirim = fields.Many2one(
    #     'res.partner', 'Pengirim', related="reference.po_id.partner_id")
    pengirim = fields.Char('Pengirim', related="reference.po_id.partner_id.name")
    invoice_id = fields.Many2one(
        'account.invoice', related="reference.invoice_number")
    # location_dest_id = fields.Many2one('stock.location','Location',compute="_get_location_dest", store=True)
    location_dest_id = fields.Many2one('stock.location', 'Location')
    location_trigger = fields.Boolean('Trigger Location', default=False)
    picking_id = fields.Many2one('stock.picking', 'Picking')
    # location_dest_id = fields.Many2one('stock.location','Location')

    @api.one
    def generate_loc(self):
        for res in self:
            if res.location_trigger == False:
                res.location_trigger = True
            else:
                res.location_trigger = False

    @api.depends('location_trigger', 'move_ids_wip')
    def _get_location_dest(self):
        for res in self:
            loc = int(self.env['ir.config_parameter'].get_param(
                'location_wip'))
            location_id = self.env['stock.location'].browse(loc)
            move_ids = self.env['stock.move'].search([('location_dest_id', '=', loc),
                                                      ('state', '=', 'done'),
                                                      ('picking_id.beacukai_incoming_id', '=', res.reference.id)])
            for move in move_ids:
                res.location_dest_id = move.location_dest_id.id

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for res in self:
            res.product_name = res.product_id.product_tmpl_id.default_code
            res.product_hs_code = res.product_id.product_tmpl_id.hs_code
            res.product_uom_id = res.product_id.uom_id.id

    @api.depends('product_qty', 'product_price')
    def _get_product_amount(self):
        for res in self:
            res.product_amount = (res.product_qty or 0.0) * \
                (res.product_price or 0.0)
            res.saldo = res.product_qty


class LaporanPosisiWIPTransient(models.TransientModel):
    _name = "laporan.posisi.wip.transient"
    _order = "id desc"

    @api.one
    @api.depends('bc_ref_type', 'bc_ref_id')
    def _compute_reference(self):
        if self.bc_ref_type in self.env:
            res = self.env[self.bc_ref_type].search(['id', '=', self.bc_ref_id])
            if res:
                self.document_type_id = res.document_type_id
                self.register_number = res.register_number
                self.register_date = res.register_date

    bc_ref_type = fields.Char('Reference Type')
    bc_ref_id = fields.Integer('Reference Id')
    move_id = fields.Many2one('stock.move', 'Stock Move')

    product_id = fields.Many2one('product.product', 'Kode Barang', related="move_id.product_id")
    product_code = fields.Char('Kode Barang', related="product_id.default_code")
    product_name = fields.Char('Nama Barang', related="product_id.name")
    product_hs_code = fields.Char('HS Code', related="product_id.hs_code")
    product_uom_id = fields.Many2one('product.uom', 'Satuan', related='move_id.uom_id')
    product_qty = fields.Float('Qty', related='move_id.product_uom_qty')

    document_type_id = fields.Char('Document Type ID', compute='_compute_reference')
    register_number = fields.Char('Register Number', compute='_compute_reference')
    register_date = fields.Date('Register Date', compute='_compute_reference')

