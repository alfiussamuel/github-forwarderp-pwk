from odoo import api,fields,models,_
import time
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning
from datetime import datetime, date
from datetime import datetime, timedelta
from dateutil.relativedelta import *
from odoo.tools.safe_eval import safe_eval
import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_compare, float_round
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils
import math
import re    
from num2words import num2words


class PwkPackingListLineContainer(models.Model):    
    _name = "pwk.packing.list.line.container"

    reference = fields.Many2one('pwk.packing.list.line', 'Reference')
    position_id = fields.Many2one('pwk.position', 'Position')
    pallet_id = fields.Many2one('pwk.pallet', 'Pallet')
    strapping_id = fields.Many2one('pwk.strapping', 'Strapping')    
    total_crates = fields.Float('Total Crates', default=1)
    qty = fields.Float('Quantity / Crate')
    number = fields.Char('Number')


class PwkPackingListLineDetail(models.Model):    
    _name = "pwk.packing.list.line.detail"

    reference = fields.Many2one('pwk.packing.list.line', string='Reference')
    product_id = fields.Many2one('product.product', string='Product')
    thick = fields.Float(string='Thick', digits=dp.get_precision('OneDecimal'))
    width = fields.Float(string='Width', digits=dp.get_precision('ZeroDecimal'))
    length = fields.Float(string='Length', digits=dp.get_precision('ZeroDecimal'))
    quantity = fields.Float(string='Quantity', digits=dp.get_precision('ZeroDecimal'))
    ply = fields.Float(string='Ply', digits=dp.get_precision('ZeroDecimal'))


class PwkPackingListLine(models.Model):    
    _name = "pwk.packing.list.line"

    reference = fields.Many2one('pwk.packing.list', string='Reference')
    sale_id = fields.Many2one('sale.order', 'No. Order')
    sale_line_id = fields.Many2one('sale.order.line', 'No. Order Line')

    reference_date = fields.Date(related="reference.date", string='Packing List Date')
    reference_partner_id = fields.Many2one(related="reference.partner_id", comodel_name='res.partner', string='Buyer')
    reference_destination_id = fields.Many2one(related="reference.destination_id", comodel_name='pwk.destination', string='Destination')
    reference_po_number = fields.Char(related="reference.po_number", string='Contract')
    reference_marking = fields.Char(related="reference.marking", string='Marking')
    reference_tanggal_selesai = fields.Date(related="reference.tanggal_selesai", string='Penyelesaian Produksi')
    reference_tanggal_emisi = fields.Date(related="reference.tanggal_emisi", string='Hasil Uji Emisi')
    reference_tanggal_stuffing = fields.Date(related="reference.tanggal_stuffing", string='Tgl Stuffing')

    container_start_end = fields.Char('Container Start End')
    crate_number = fields.Integer('Crate Number')
    crate_qty_each = fields.Integer('Crate Qty each')

    start_container_no = fields.Integer(compute="_get_container_sequence", string='Start Container No.')
    end_container_no = fields.Integer(compute="_get_container_sequence", string='End Container No.')

    name = fields.Char('Name')
    product_id = fields.Many2one('product.product', string='Product')
    thick = fields.Float(compute="_get_fields", string='Thick', digits=dp.get_precision('OneDecimal'))
    width = fields.Float(compute="_get_fields", string='Width', digits=dp.get_precision('ZeroDecimal'))
    length = fields.Float(compute="_get_fields", string='Length', digits=dp.get_precision('ZeroDecimal'))
    glue_id = fields.Many2one(compute="_get_fields", comodel_name='pwk.glue', string='Glue')
    grade_id = fields.Many2one(compute="_get_fields", comodel_name='pwk.grade', string='Grade')
    marking = fields.Char(related='sale_line_id.marking', string='Marking')
    
    quantity = fields.Float(compute="_get_quantity", string='Quantity', digits=dp.get_precision('TwoDecimal'))
    volume = fields.Float(compute="_get_volume", string='Volume', digits=dp.get_precision('FourDecimal'))

    bom_ids = fields.One2many('pwk.packing.list.line.detail', 'reference', string='Lines')
    container_ids = fields.One2many('pwk.packing.list.line.container', 'reference', string='Container')

    bom_name_list = fields.Text(compute="_get_bom_name_list", string="BoM Name List")

    @api.multi
    def _get_bom_name_list(self):
        for res in self:
            bom_name_list = ''
            if res.bom_ids:
                for bom in res.bom_ids:
                    if bom_name_list:
                        bom_name_list = bom_name_list + '\n' + bom.product_id.name
                    else:
                        bom_name_list = bom_name_list + bom.product_id.name

            res.bom_name_list = bom_name_list

    @api.multi
    @api.depends('product_id')
    def name_get(self):
        result = []
        for res in self:
            name = res.product_id.name
            result.append((res.id, name))
        return result

    @api.depends('crate_number', 'crate_qty_each')
    def _get_container_sequence(self):
        for res in self:
            res.start_container_no = 0
            res.end_container_no = 0

    @api.depends('crate_number','crate_qty_each')
    def _get_quantity(self):
        for res in self:
            res.quantity = res.crate_number * res.crate_qty_each

    @api.depends('quantity')
    def _get_volume(self):
        for res in self:
            if res.quantity:
                res.volume = res.quantity * res.thick * res.width * res.length / 1000000000

    @api.depends('product_id')
    def _get_fields(self):
        for res in self:
            if res.product_id:
                res.thick = res.product_id.tebal
                res.width = res.product_id.lebar
                res.length = res.product_id.panjang
                res.glue_id = res.product_id.glue.id
                res.grade_id = res.product_id.grade.id


class PwkPackingListGroup(models.Model):    
    _name = "pwk.packing.list.group"

    reference = fields.Many2one('pwk.packing.list', string='Reference')
    product_id = fields.Many2one('product.product', string='Product')
    jenis_kayu_id = fields.Many2one('pwk.jenis.kayu', string='Jenis Kayu')
    

class PwkPackingList(models.Model):    
    _name = "pwk.packing.list"

    name = fields.Char('Nomor Packing List')
    date = fields.Date('Date', default=fields.Date.today())
    certificate_id = fields.Many2one('pwk.certificate', 'Certificate')
    is_logo = fields.Boolean('Show Legal Logo', default=True)
    
    product_name_list = fields.Char(compute="_get_product_name_list", string="Product Name List")

    partner_id = fields.Many2one(compute="_get_fields", comodel_name='res.partner', string='Buyer')
    destination_id = fields.Many2one(compute="_get_fields", comodel_name='pwk.destination', string='Destination')
    payment_term_id = fields.Many2one(compute="_get_fields", comodel_name='account.payment.term', string='Payment Terms')
    marking = fields.Char(compute="_get_fields", string='Marking')
    po_number = fields.Char(compute="_get_fields", string='Contract')

    line_ids = fields.One2many('pwk.packing.list.line', 'reference', string='Lines')
    group_ids = fields.One2many('pwk.packing.list.group', 'reference', string='Groups')
    state = fields.Selection([('Draft','Draft'),('Done','Done')], string="Status", default="Draft")

    tanggal_selesai = fields.Date('Penyelesaian Produksi')
    tanggal_emisi = fields.Date('Hasil Uji Emisi')
    tanggal_p1 = fields.Date('Prod P1 Terakhir')
    tanggal_p2 = fields.Date('Prod P2 Terakhir')
    tanggal_pengambilan = fields.Date('Rencana Pengambilan')
    tanggal_pengiriman = fields.Date('Rencana Pengiriman')
    tanggal_stuffing = fields.Date('Tanggal Stuffing')

    total_volume = fields.Float(compute="_get_total_volume", string="Total Volume")
    notes_quantity = fields.Char('Notes Quantity')
    notes = fields.Text('Notes')

    qty_muatan = fields.Char('Qty Muatan')

    is_picking = fields.Boolean('Picking created')
    picking_id = fields.Many2one('stock.picking', 'Delivery Order')

    @api.depends('line_ids.product_id')
    def _get_product_name_list(self):
        for res in self:
            product_name_list = ''
            if res.line_ids:
                for line in res.line_ids:
                    if product_name_list:
                        product_name_list += (', ' + line.product_id.name)
                    else:
                        product_name_list += line.product_id.name

            res.product_name_list = product_name_list

    @api.depends('line_ids.volume')
    def _get_total_volume(self):
        for res in self:
            total_volume = 0
            if res.line_ids:
                for line in res.line_ids:
                    total_volume += line.volume

            res.total_volume = total_volume

    @api.depends('line_ids.sale_line_id')
    def _get_fields(self):
        for res in self:
            if res.line_ids:
                res.partner_id = res.line_ids[0].sale_id.partner_id.id
                res.destination_id = res.line_ids[0].sale_id.destination_id.id
                res.payment_term_id = res.line_ids[0].sale_id.payment_term_id.id
                res.marking = res.line_ids[0].sale_id.marking
                res.po_number = res.line_ids[0].sale_id.po_number

    def get_sequence(self, name=False, obj=False, year_month=False, context=None):
        sequence_id = self.env['ir.sequence'].search([
            ('name', '=', name),
            ('code', '=', obj),
            ('suffix', '=', year_month)
        ])
        if not sequence_id :
            sequence_id = self.env['ir.sequence'].sudo().create({
                'name': name,
                'code': obj,
                'implementation': 'no_gap',
                'suffix': year_month,
                'padding': 3
            })
        return sequence_id.next_by_id()

    @api.model
    def create(self, vals):
        year_month = '/PPIC-PWK/%(month)s/%(year)s'
        vals['name'] = self.get_sequence('Packing List', 'pwk.packing.list', '%s' % year_month)
        return super(PwkPackingList, self).create(vals)

    @api.multi
    def print_packing_list_produksi(self):                
        return self.env.ref('v12_pwk.packing_list_produksi').report_action(self)

    # @api.multi
    # def action_create_picking(self):
    #     for res in self:
    #         picking_id = self.env['stock.picking'].create({

    #         })

    #         for line in res.line_ids:
    #             self.env['stock.move'].create({
    #                 'product_id': line.product_id.id,

    #             })

    #         res.write({
    #             'is_picking': True,
    #             'picking_id': picking_id.id
    #         })
