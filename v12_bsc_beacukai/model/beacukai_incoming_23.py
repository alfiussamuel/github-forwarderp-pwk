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
from odoo.tools.float_utils import float_compare, float_round
import odoo.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

# class StockQuant(models.Model):
#     _inherit = "stock.quant"

#     bc_23_id = fields.Many2one(comodel_name='beacukai.incoming.23', string='Document BC 23')
#     submission_no = fields.Char(string='Nomor Pengajuan')

#     @api.model
#     def _quant_create_from_move(self, qty, move, lot_id=False, owner_id=False,
#                                 src_package_id=False, dest_package_id=False,
#                                 force_location_from=False, force_location_to=False):
#         '''Create a quant in the destination location and create a negative
#         quant in the source location if it's an internal location. '''
#         print "Masuk quant create from move"
#         price_unit = move.get_price_unit()
#         location = force_location_to or move.location_dest_id
#         rounding = move.product_id.uom_id.rounding
#         # print "Moveeeeeeeeeeeeeeeeeeeee ", move
#         vals = {
#             'product_id': move.product_id.id,
#             'bc_23_id': move.bc_23_id.id,
#             'submission_no': move.submission_no,
#             'location_id': location.id,
#             'qty': float_round(qty, precision_rounding=rounding),
#             'cost': price_unit,
#             'history_ids': [(4, move.id)],
#             'in_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
#             'company_id': move.company_id.id,
#             'lot_id': lot_id,
#             'owner_id': owner_id,
#             'package_id': dest_package_id,
#         }
#         if move.location_id.usage == 'internal':
#             # if we were trying to move something from an internal location and reach here (quant creation),
#             # it means that a negative quant has to be created as well.
#             negative_vals = vals.copy()
#             negative_vals['location_id'] = force_location_from and force_location_from.id or move.location_id.id
#             negative_vals['qty'] = float_round(-qty, precision_rounding=rounding)
#             negative_vals['cost'] = price_unit
#             negative_vals['negative_move_id'] = move.id
#             negative_vals['package_id'] = src_package_id
#             negative_quant_id = self.sudo().create(negative_vals)
#             vals.update({'propagated_from_id': negative_quant_id.id})

#         picking_type = move.picking_id and move.picking_id.picking_type_id or False
#         if lot_id and move.product_id.tracking == 'serial' and (not picking_type or (picking_type.use_create_lots or picking_type.use_existing_lots)):
#             if qty != 1.0:
#                 raise UserError(_('You should only receive by the piece with the same serial number'))

#         # create the quant as superuser, because we want to restrict the creation of quant manually: we should always use this method to create quants
#         quant_id = self.sudo().create(vals)
#         # print "Quant ", quant_id
#         # print "Quant BC 23 ID ", quant_id.bc_23_id
#         # print "Quant Submission No ", quant_id.submission_no
#         return quant_id

class StockMove(models.Model):
    _inherit = "stock.move"

    bc_23_id = fields.Many2one(compute='_get_bc_23_id', comodel_name='beacukai.incoming.23', string='Document BC 23')
    submission_no = fields.Char(compute='_get_submission_no', string='Nomor Pengajuan')

    @api.depends('picking_id.origin')
    def _get_submission_no(self):
        for res in self:
            if res.picking_id.submission_no:
                res.submission_no = res.picking_id.submission_no
            elif res.picking_id.origin:
                res.submission_no = res.picking_id.origin

    @api.depends('picking_id.origin')
    def _get_bc_23_id(self):
        for res in self:
            if res.picking_id.origin:
                document_id = self.env['beacukai.incoming.23'].search([('submission_no','=',res.picking_id.origin)])
                if document_id:
                    res.bc_23_id = document_id[0].id

class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    bc_23_id = fields.Many2one(compute='_get_bc_23_id', comodel_name='beacukai.incoming.23', string='Document BC 23')
    submission_no = fields.Char(compute='_get_submission_no', string='Nomor Pengajuan')

    @api.depends('picking_id.origin')
    def _get_submission_no(self):
        for res in self:
            if res.picking_id.submission_no:
                res.submission_no = res.picking_id.submission_no
            elif res.picking_id.origin:
                res.submission_no = res.picking_id.origin

    @api.depends('picking_id.origin')
    def _get_bc_23_id(self):
        for res in self:
            if res.picking_id.origin:
                document_id = self.env['beacukai.incoming.23'].search([('submission_no','=',res.picking_id.origin)])
                if document_id:
                    res.bc_23_id = document_id[0].id

class BeacukaiIncoming23(models.Model):
    _name = "beacukai.incoming.23"
    _inherit = ['mail.thread']
    _order = "id desc"
    _rec_name = "submission_no"

    @api.multi
    def _get_default_picking_type_id(self):        
        picking_type_id = self.env['stock.picking.type'].search([('name','=','Receipts')])
        print ("Picking Type ", picking_type_id[0].id)
        return picking_type_id[0].id

    @api.multi
    def action_confirm(self):
        for incoming23 in self:
            view_id = self.env['bc.outgoing.register.number']
            new = view_id.create({'document_id': incoming23.id, 'ref_model': self._name})
            return {
                'type': 'ir.actions.act_window',
                'name': 'Input Nomor Registasi',
                'res_model': 'bc.outgoing.register.number',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': new.id,
                'view_id': self.env.ref('v10_bsc_beacukai.view_beacukai_input_register_number_out').id,
                'context': "{'is_incoming': True}",
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

    def _compute_document_type(self):
        res = self.env['beacukai.document.type'].search([('name', '=', '23'), ('document_type', '=', 'incoming')])
        return res and res.id or False

    name = fields.Char('Document No.')
    line_ids = fields.One2many(
        'beacukai.incoming.line.23', 'reference', string='TPB Barang', copy=True)
    picking_id = fields.Many2one('stock.picking', 'Shipment Document')
    tariff_ids = fields.One2many(
        'tpb.goods.tariff', 'reference_goods_tariff', string='TPB Tarif & Cukai', copy=True)

    """ Header """
    id_header = fields.Char(string="ID Header")
    document_type_id = fields.Many2one('beacukai.document.type', 'Tipe', default=_compute_document_type)
    apiu_id = fields.Many2one('beacukai.apiu', 'Pengusaha TPB')
    register_number = fields.Char('No Pendaftaran')
    register_date = fields.Date('Tanggal Daftar')
    date = fields.Date('Tanggal Aju', default=fields.Datetime.now)
    date_aju = fields.Date('Tanggal Aju', default=fields.Datetime.now)
    kode_harga = fields.Selection([('EXW', 'EXW'),
                                   ('CFR', 'CFR'),
                                   ('CIF', 'CIF'),
                                   ('FCA', 'FCA'),
                                   ('CPT', 'CPT'),
                                   ('CIP', 'CIP'),
                                   ('DAT', 'DAT'),
                                   ('DAP', 'DAP'),
                                   ('DDP', 'DDP'),
                                   ('FAS', 'FAS'), ], string='Kode Harga')

    """ Notification Data """
    # company_npwp = fields.Char(
    #     'NPWP', default=lambda self: self.env.user.company_id.vat, readonly=True)
    # company_name = fields.Char(
    #     'Nama Perusahaan', default=lambda self: self.env.user.company_id.name, readonly=True)
    # company_address = fields.Text(
    #     'Alamat Perusahaan', default=lambda self: self.env.user.company_id.street, readonly=True)
    # company_permission_no = fields.Char(
    #     'Izin Perusahaan', readonly=True, default=lambda self: self.env['ir.config_parameter'].get_param('no_tpb'))

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
    amount_usd = fields.Float('Jumlah USD')
    amount_idr = fields.Float('Jumlah IDR')    
    harga_penyerahan = fields.Float(string='Harga Penyerahan')

    """ Packaging Data """
    packing_number = fields.Char('No Packing dan Merek')
    packaging_number = fields.Float('Nomor dan Tipe Packaging')
    packaging_type = fields.Many2one(
        'product.uom', 'Number and Type Packaging')
    picking_count = fields.Integer(
        compute='_compute_picking_23', string='Receptions', default=0)
    is_shipped = fields.Boolean(compute="_compute_is_shipped")
    po_id = fields.Many2one('purchase.order', string='No PO')
    picking_type_id = fields.Many2one('stock.picking.type', 'Alur Ke Gudang', required=False, 
        default=lambda self: self.env['stock.picking.type'].search([('name', '=', "Receipts")], limit=1))

    """Header"""
    submission_no = fields.Char('Nomor Pengajuan')
    submission_no_char = fields.Char('Nomor Pengajuan Char')
    tpb_source_id = fields.Many2one('beacukai.tpb', 'KPPBC Pengawas')
    tpb_dest_id = fields.Many2one('beacukai.tpb', 'KPPBC Bongkar')
    delivery_purpose_id = fields.Many2one(
        'ref.destination.tpb', 'Tujuan TPB')

    """Pemasok"""
    supplier_id = fields.Many2one('res.partner', 'Nama Vendor')
    supplier_address = fields.Char(related='supplier_id.street',string='Alamat Vendor')
    supplier_country = fields.Char(related='supplier_id.country_id.name', readonly=True)
    # supplier_country_id = fields.Many2one('res.country', 'Negara Vendor')

    """Importir"""
    company_id_code = fields.Many2one('ref.code.id',string='Kode Identitas')
    company_npwp = fields.Char(
        'Nomor Identitas', default=lambda self: self.env.user.company_id.vat)
    company_name = fields.Char(
        'Nama Perusahaan', default=lambda self: self.env.user.company_id.name)
    company_address = fields.Text(
        'Alamat Perusahaan', default=lambda self: self.env.user.company_id.street)
    company_permission_no = fields.Char(
        'No. Izin Perusahaan', default=lambda self: self.env['ir.config_parameter'].get_param('no_tpb'))
    # company_api_type = fields.Selection([
    #     ('mode_apiu', 'APIU'),
    #     ('mode_apip', 'APIP'),
    #     string="Jenis API",
    #     required=False])
    company_api_type = fields.Many2one(
        'ref.api.type', 'Jenis API', required=False)
    company_api_number = fields.Char('Nomor API', required=False)

    """Pemilik"""
    owner_id_code = fields.Many2one('ref.code.id',string='Kode Identitas')
    owner_npwp = fields.Char(
        'Nomor Identitas', default=lambda self: self.env.user.company_id.vat)
    owner_name = fields.Char(
        'Nama Pemilik', default=lambda self: self.env.user.company_id.name)
    owner_address = fields.Text(
        'Alamat Pemilik', default=lambda self: self.env.user.company_id.street)
    # owner_api_type = fields.Selection([
    #     ('mode_apiu', 'APIU'),
    #     ('mode_apip', 'APIP'),
    # ], string='Jenis API',
    #     required=False)
    owner_api_type = fields.Many2one(
        'ref.api.type', 'Jenis API', required=False)
    owner_api_number = fields.Char('Nomor API', required=False)

    """ Pengangkutan """
    # mod_trans = fields.Selection([
    #     ('mode_sea', 'LAUT'),
    #     ('mode_train', 'KERETA API'),
    #     ('mode_ground', 'DARAT'),
    #     ('mode_air', 'UDARA'),
    #     ('mode_post', 'POS'),
    #     ('mode_multi', 'MULTI MODA'),
    #     ('mode_instal', 'INSTALASI'),
    #     ('mode_water', 'PERAIRAN'),
    #     ('mode_misc', 'LAINNYA')
    # ], string='Sarana Pengangkut', required=False)
    code_mode_transport = fields.Many2one('ref.mode.transport',string='Cara Pengangkutan',required=False)
    name_mode_transport = fields.Many2one('ref.ship', string='Nama Sarana Pengangkut', required=False)
    voy_fli_number = fields.Char('Voy/Flight',required=False)
    flag_code = fields.Many2one('ref.negara', 'Bendera',related='name_mode_transport.negara_id')
    port_code_1 = fields.Many2one('ref.port', 'Pelabuhan Muat', required=False)
    port_code_2 = fields.Many2one('ref.port', 'Pelabuhan Transit')
    port_code_3 = fields.Many2one(
        'ref.port', 'Pelabuhan Bongkar', required=False)

    """Dokumen"""
    document_ids = fields.One2many('tpb.document', 'reference_document', string='TPB Dokumen', copy=True)
    no_bc_1_1 = fields.Char('BC 1.1 No', required=False)
    tgl_bc_1_1 = fields.Date('BC 1.1 Tanggal', required=False)
    pos_bc_1_1 = fields.Char('BC 1.1 Pos', required=False)
    subpos_bc_1_1 = fields.Char('BC 1.1 Subpos', required=False)
    subsubpos_bc_1_1 = fields.Char('BC 1.1 Subsubpos', required=False)

    """Penimbunan"""
    tmp_timbun = fields.Many2one('ref.tps', 'Tmp Penimbunan', required=False)

    """Harga"""
    currency_id = fields.Many2one("res.currency", string='Valuta')
    ndpbm = fields.Float(string='NDPBM')
    product_fob = fields.Float(string='FOB')
    product_freight = fields.Float('Freight', required=False, default=0)
    product_insurance = fields.Float(
        'Asuransi LN/DN', required=False, default=0)

    cif_harga = fields.Float('Harga CIF')
    cif_biaya_tambahan = fields.Float('Biaya Tambahan')
    cif_diskon = fields.Float('Diskon')    
    cif_cost = fields.Float(compute="_get_product_cif", string='Nilai CIF', required=False)
    cif_amount = fields.Float(compute="_get_product_cif", string='Nilai CIF Rupiah', required=False, default=0)

    """Kontainer"""
    container_ids = fields.One2many(
        'tpb.container', 'reference_container', string='TPB Kontainer', copy=True)

    """Kemasan"""
    package_ids = fields.One2many(
        'tpb.package', 'reference_package', string='TPB Kemasan', copy=True)

    """Barang"""
    bruto_header = fields.Float('Bruto', required=False)
    netto_header = fields.Float('Netto', required=False)
    qty_header = fields.Integer('Jumlah Barang', required=False)

    """TTD"""
    city_signed = fields.Char('Kota', required=False)
    date_signed = fields.Date('Tanggal', required=False)
    teller_signed = fields.Char('Pemberitahu', required=False)
    position_signed = fields.Char('Jabatan', required=False)

    """Selain Ada Di Module"""
    code_doc_pabean = fields.Char(string='Kode Dokumen Pabean',default='23')


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
        'stock.picking', compute='_compute_picking_23', string='Receptions', copy=False)
    state = fields.Selection([
        ('pengajuan', 'Pengajuan'),
        ('registrasi', 'Registrasi'),
        ('terima', 'Penerimaan Barang'),
        ('done', 'Selesai'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='pengajuan')
    is_from_po = fields.Boolean('Created from PO', default=False)

    efaktur_number = fields.Char('E-Faktur')

    @api.constrains('submission_no')
    def _check_submission_no(self):
        if self.submission_no:
            if ' ' == self.submission_no[-1:]:
                self.submission_no = self.submission_no.strip()
                return

            valid = '0123456789'
            for c in self.submission_no:
                if c not in valid:
                    raise UserError("Nomor Pengajuan hanya bisa berupa digit")

    @api.depends('cif_harga','cif_biaya_tambahan','cif_diskon','ndpbm')
    def _get_product_cif(self):
        for res in self:
            total_cif = res.cif_harga + res.cif_biaya_tambahan - res.cif_diskon
            res.cif_cost = total_cif
            res.cif_amount = total_cif * res.ndpbm

    @api.multi
    def push_to_ceisa(self):
        raise Warning('Under Construction')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'beacukai.incoming.23') or 'New'
        return super(BeacukaiIncoming23, self).create(vals)

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
            order = self.env['purchase.order'].search([('bc_ref_type', '=', self._name),
                                                       ('bc_ref_id', '=', self.id)], limit=1)
            if order:
                order.button_done()

            return self.write({'state': 'done', 'finish_date': fields.Date.today()})
        else:
            raise UserError(
                _('Pastikan penerimaan barang telah selesai dan telah menginput finish date'))

    @api.depends('line_ids.move_ids')
    def _compute_picking_23(self):
        for order in self:
            pickings = self.env['stock.picking']
            pickings |= pickings.search([('bc_ref_type', '=', self._name),
                                         '|', ('bc_ref_id', '=', order.id),
                                         ('submission_no', '=', order.submission_no)])
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
            _logger.info('picking test')
            if bcmove.is_from_po:
                return self.write({'state': 'terima'})

            if bcmove.picking_type_id.default_location_dest_id.id:
                dst = bcmove.picking_type_id.default_location_dest_id.id
            else:
                dst = self.default_location_dest_id = self.env.ref(
                    'stock.stock_location_stock').id
            if bcmove.picking_type_id.default_location_src_id.id:
                src = bcmove.picking_type_id.default_location_src_id.id
            else:
                src = self.env.ref('stock.stock_location_suppliers').id
            _logger.info(self.env.ref('stock.stock_location_suppliers').name)
            _logger.info(dst)
            stok = self.env['stock.picking'].create({
                'move_type': 'direct',
                'picking_type_id': bcmove.picking_type_id.id,
                'is_beacukai_incoming_23': True,
                'beacukai_incoming_23_id': bcmove.id,
                'origin': bcmove.submission_no,
                'location_id': src,
                'location_dest_id': dst
            })
            if bcmove.line_ids:
                _logger.info(bcmove.line_ids)
                for line in bcmove.line_ids:
                    pack_operation_product_ids = {
                        'picking_id': stok.id,
                        'bc_incoming_line_23_id': line.id,
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.product_qty,
                        'product_uom': line.product_uom_id.id,
                        'name': line.product_id.display_name,
                        'date_expected': bcmove.register_date,
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
