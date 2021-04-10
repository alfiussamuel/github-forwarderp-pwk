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
    qty = fields.Float('Quantity / Crate', digits=dp.get_precision('ZeroDecimal'))
    number = fields.Char('Number')


class PwkPackingListLineRevision(models.Model):    
    _name = "pwk.packing.list.line.revision"

    sequence = fields.Integer('Sequence')
    notes = fields.Text('Revision Notes')
    date = fields.Date('Revision Date')
    reference = fields.Many2one('pwk.packing.list.line', string='Reference')
    product_id = fields.Many2one('product.product', string='Product')
    crate_number = fields.Integer('Total Crate')
    quantity = fields.Float(string='Quantity', digits=dp.get_precision('ZeroDecimal'))
    volume = fields.Float(compute="_get_volume", string='Volume', digits=dp.get_precision('FourDecimal'))

    @api.onchange('reference')
    def _onchange_data(self):
        self.product_id = self.reference.product_id.id
        self.quantity = self.reference.quantity
        self.volume = self.reference.volume

    @api.depends('quantity')
    def _get_volume(self):
        for res in self:
            if res.quantity:
                res.volume = res.quantity * res.product_id.tebal * res.product_id.lebar * res.product_id.panjang / 1000000000


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
    _order = 'jenis_kayu_id asc, width asc,length asc,thick asc'

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

    container_end = fields.Integer(compute="_get_container_sequence", string='Container End')
    container_manual = fields.Char(string='Crate Manual')
    container_start_end = fields.Char(compute="_get_container_sequence", string='Container Start End')
    container_start_end_revision = fields.Char(compute="_get_container_sequence", string='Container Start End Rev')
    crate_number = fields.Integer('Total Crate')
    crate_qty_each = fields.Integer('Crate Qty each')

    # start_container_no = fields.Integer(compute="_get_container_sequence", string='Start Container No.')
    # end_container_no = fields.Integer(compute="_get_container_sequence", string='End Container No.')

    name = fields.Char('Name')
    product_id = fields.Many2one('product.product', string='Product')
    thick = fields.Float(compute="_get_fields", string='Thick', digits=dp.get_precision('OneDecimal'), store=True)
    width = fields.Float(compute="_get_fields", string='Width', digits=dp.get_precision('ZeroDecimal'), store=True)
    length = fields.Float(compute="_get_fields", string='Length', digits=dp.get_precision('ZeroDecimal'), store=True)
    glue_id = fields.Many2one(compute="_get_fields", comodel_name='pwk.glue', string='Glue')
    grade_id = fields.Many2one(compute="_get_fields", comodel_name='pwk.grade', string='Grade')
    jenis_kayu_id = fields.Many2one(compute="_get_fields", comodel_name='pwk.jenis.kayu', string='Jenis Kayu', store=True)
    marking = fields.Char(related='sale_line_id.marking', string='Marking')

    
    quantity = fields.Float(compute="_get_quantity", string='Quantity', digits=dp.get_precision('ZeroDecimal'))
    volume = fields.Float(compute="_get_volume", string='Volume', digits=dp.get_precision('FourDecimal'))

    bom_ids = fields.One2many('pwk.packing.list.line.detail', 'reference', string='Lines')
    container_ids = fields.One2many('pwk.packing.list.line.container', 'reference', string='Container')
    revision_ids = fields.One2many('pwk.packing.list.line.revision', 'reference', string='Revision')

    bom_name_list = fields.Text(compute="_get_bom_name_list", string="BoM Name List")

    # Revision Fields
    revision_product_id = fields.Many2one(compute="_get_revision_fields", comodel_name='product.product', string='Rev Product')
    revision_quantity = fields.Float(compute="_get_revision_fields", string="Rev Quantity", digits=dp.get_precision('ZeroDecimal'))
    revision_quantity_only = fields.Float(compute="_get_revision_fields", string="Quantity", digits=dp.get_precision('ZeroDecimal'))
    revision_quantity_original = fields.Float(compute="_get_revision_fields", string="Quantity", digits=dp.get_precision('ZeroDecimal'))
    revision_volume = fields.Float(compute="_get_revision_fields", string="Rev Volume", digits=dp.get_precision('FourDecimal'))
    revision_volume_only = fields.Float(compute="_get_volume", string="Volume", digits=dp.get_precision('FourDecimal'))
    revision_volume_original = fields.Float(compute="_get_volume", string="Volume", digits=dp.get_precision('FourDecimal'))
    revision_crate_number = fields.Integer(compute="_get_revision_fields", string="Rev Crate")
    revision_crate_number_original = fields.Integer(compute="_get_revision_fields", string="Rev Crate")

    @api.depends('revision_ids.product_id', 'revision_ids.quantity', 'revision_ids.volume', 'product_id', 'quantity', 'volume')
    def _get_revision_fields(self):
        for res in self:
            revision_product_id = False
            revision_quantity = 0
            revision_quantity_only = 0
            revision_volume = 0
            revision_crate_number = 0
            revision_crate_number_original = 0

            if res.revision_ids:
                for revision in res.revision_ids:
                    if revision.product_id.id != res.product_id.id:
                        revision_product_id = revision.product_id.id
                        revision_crate_number = revision.crate_number
                        revision_quantity_only = revision.quantity

                    revision_quantity += revision.quantity
                    revision_volume += revision.volume

            if revision_quantity == 0:
                revision_quantity = res.quantity
            if revision_volume == 0:
                revision_volume = res.volume

            res.revision_product_id = revision_product_id
            res.revision_quantity = revision_quantity
            res.revision_quantity_only = revision_quantity_only
            res.revision_quantity_original = res.quantity - revision_quantity_only
            res.revision_volume = revision_volume
            res.revision_crate_number = revision_crate_number
            res.revision_crate_number_original = res.crate_number - revision_crate_number

    @api.multi
    def _get_bom_name_list(self):
        for res in self:
            bom_name_list = ''
            if res.bom_ids:
                for bom in res.bom_ids:
                    if bom_name_list:
                        bom_name_list = bom_name_list + '\n' + (bom.product_id.grade.name + ' ' + bom.product_id.jenis_kayu.name + ' ' + str(bom.product_id.tebal) + ' x ' + str(bom.ply)) + ' Ply'
                    else:
                        bom_name_list = bom_name_list + (bom.product_id.grade.name + ' ' + bom.product_id.jenis_kayu.name + ' ' + str(bom.product_id.tebal) + ' x ' + str(bom.ply)) + ' Ply'

            res.bom_name_list = bom_name_list

    @api.multi
    @api.depends('product_id')
    def name_get(self):
        result = []
        for res in self:
            name = res.product_id.name
            result.append((res.id, name))
        return result

    @api.multi
    def _get_container_sequence(self):
        for res in self:
            container_no = 1

            smaller_ids = self.env['pwk.packing.list.line'].search([
                ('id', '<', res.id),
                ('reference', '=', res.reference.id)
            ], order='id desc')

            print ("Smaller IDS desc ", smaller_ids)

            # smaller_ids = self.env['pwk.packing.list.line'].search([
            #     ('id', '<', res.id),
            #     ('reference', '=', res.reference.id)
            # ], order='id asc')

            # print ("Smaller IDS asc ", smaller_ids)

            if smaller_ids:
                container_no = smaller_ids[0].container_end + smaller_ids[0].revision_crate_number + 1
                print ("ID ", smaller_ids[0].id)
                print ("Product ", smaller_ids[0].product_id.name)
                print ("Container End ", smaller_ids[0].container_end)
                print ("Container No. ", container_no)
            
            container_start = container_no
            container_end = container_no + res.crate_number - 1
            container_no += res.crate_number

            container_start_end = ''
            container_start_end_revision = ''

            print ("Container Start ", container_start)
            print ("Container End ", container_end)

            if container_start == (container_end - res.revision_crate_number) and container_start > 10:
                print ("aaa")
                container_start_end = str(container_start)
            elif container_start == (container_end - res.revision_crate_number) and container_start < 10:
                print ("bbb")
                container_start_end = '0' + str(container_start)
            elif container_start < 10 and (container_end - res.revision_crate_number) < 10:
                container_start_end = '0' + str(container_start) + ' - ' + '0' + str(container_end - res.revision_crate_number)
            elif container_start >= 10 and (container_end - res.revision_crate_number) < 10:
                container_start_end = str(container_start) + ' - ' + '0' + str(container_end - res.revision_crate_number)
            elif container_start < 10 and (container_end - res.revision_crate_number) >= 10:
                container_start_end = '0' + str(container_start) + ' - ' + str(container_end - res.revision_crate_number)
            elif container_start >= 10 and (container_end - res.revision_crate_number) >= 10:
                container_start_end = str(container_start) + ' - ' + str(container_end - res.revision_crate_number)

            container_start_end_revision = container_start_end
            # Revision
            if res.revision_ids:
                revision_start = str(container_end)
                revision_end = str(container_end + res.revision_crate_number - 1)

                print ("Revision Start ", revision_start)
                print ("Revision End ", revision_end)

                if revision_start == revision_end and int(revision_start) >= 10:
                    container_start_end_revision = revision_start
                elif revision_start == revision_end and int(revision_start) < 10:
                    container_start_end_revision = '0' + revision_start
                elif int(revision_start) < 10 and int(revision_end) < 10:
                    container_start_end_revision = '0' + revision_start + ' - ' + '0' + revision_end
                elif int(revision_start) >= 10 and int(revision_end) < 10:
                    container_start_end_revision = revision_start + ' - ' + '0' + revision_end
                elif int(revision_start) < 10 and int(revision_end) >= 10:
                    container_start_end_revision = '0' + revision_start + ' - ' + revision_end
                elif int(revision_start) >= 10 and int(revision_end) >= 10:
                    container_start_end_revision = revision_start + ' - ' + revision_end

            print ("Container ", container_start_end)
            print ("Container Rev ", container_start_end_revision)

            res.container_end = container_end - res.revision_crate_number
            res.container_start_end = container_start_end
            res.container_start_end_revision = container_start_end_revision

    @api.depends('crate_number','crate_qty_each')
    def _get_quantity(self):
        for res in self:
            res.quantity = res.crate_number * res.crate_qty_each

    @api.depends('quantity', 'revision_quantity_only', 'revision_quantity_original')
    def _get_volume(self):
        for res in self:
            if res.quantity:
                res.volume = res.quantity * res.thick * res.width * res.length / 1000000000
                res.revision_volume_only = res.revision_quantity_only * res.thick * res.width * res.length / 1000000000
                res.revision_volume_original = res.revision_quantity_original * res.thick * res.width * res.length / 1000000000

    @api.depends('product_id')
    def _get_fields(self):
        for res in self:
            if res.product_id:
                res.thick = res.product_id.tebal
                res.width = res.product_id.lebar
                res.length = res.product_id.panjang
                res.glue_id = res.product_id.glue.id
                res.grade_id = res.product_id.grade.id
                res.jenis_kayu_id = res.product_id.jenis_kayu.id

    @api.multi
    def action_create_revision(self):
        for res in self:
            self.env['pwk.packing.list.line.revision'].create({
                'date' : fields.Date.today(),
                'reference': res.id,
                'product_id': res.product_id.id,
                'quantity': res.quantity,
                'volume': res.volume,
            })

            

class PwkPackingListGroup(models.Model):    
    _name = "pwk.packing.list.group"
    _order = "jenis_kayu_id asc"

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
    revision_notes = fields.Text('Revision Notes')

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
        date = datetime.strptime(vals.get('date'), '%Y-%m-%d')
        month = date.month
        year = date.year
        romawi = ''
        print ("Month ", month)

        if month == 1:
            romawi = 'I'
        elif month == 2:
            romawi = 'II'
        elif month == 3:
            romawi = 'III'
        elif month == 4:
            romawi = 'IV'
        elif month == 5:
            romawi = 'V'
        elif month == 6:
            romawi = 'VI'
        elif month == 7:
            romawi = 'VII'
        elif month == 8:
            romawi = 'VIII'
        elif month == 9:
            romawi = 'IX'
        elif month == 10:
            romawi = 'X'
        elif month == 11:
            romawi = 'XI'
        elif month == 12:
            romawi = 'XII'

        year_month = '/PPIC-PWK/' + str(romawi) + '/' + str(year)
        vals['name'] = self.get_sequence('Packing List', 'pwk.packing.list', '%s' % year_month)
        return super(PwkPackingList, self).create(vals)

    @api.multi
    def print_packing_list_produksi(self):                
        return self.env.ref('v12_pwk.packing_list_produksi').report_action(self)

    @api.multi
    def print_packing_list_produksi2(self):                
        return self.env.ref('v12_pwk.packing_list_produksi2').report_action(self)

    @api.multi
    def action_create_picking(self):
        for res in self:
            source_location_ids = self.env['stock.location'].search([('name', '=', 'GBJ')])
            if not source_location_ids:
                raise UserError(_('Lokasi Gudang Barang Jadi tidak ditemukan'))

            destination_location_ids = self.env['stock.location'].search([('name', '=', 'Customers')])
            if not destination_location_ids:
                raise UserError(_('Lokasi Customer tidak ditemukan'))

            picking_type_ids = self.env['stock.picking.type'].search([('name', '=', 'Delivery Orders PWK')])
            if not picking_type_ids:
                raise UserError(_('Operation Types tidak ditemukan'))

            picking_id = self.env['stock.picking'].create({
                'partner_id': res.partner_id.id,
                'location_id': source_location_ids[0].id,
                'location_dest_id': destination_location_ids[0].id,
                'picking_type_id': picking_type_ids[0].id,
                'scheduled_date': datetime.now(),
                'origin': res.name
            })

            for line in res.line_ids:
                product = line.product_id
                if line.revision_product_id:
                    product = line.revision_product_id

                self.env['stock.move'].create({
                    'picking_id': picking_id.id,
                    'product_id': product.id,
                    'name': product.name,
                    'product_uom_qty': line.quantity,
                    'product_uom': product.uom_id.id,
                    'location_id': source_location_ids[0].id,
                    'location_dest_id': destination_location_ids[0].id,
                    'date': datetime.now()
                })

            if picking_id:
                picking_id.action_confirm()
                picking_id.action_assign()

            res.write({
                'is_picking': True,
                'picking_id': picking_id.id
            })
