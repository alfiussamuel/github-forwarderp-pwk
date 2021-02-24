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

    crate_number = fields.Integer('Crate Number')
    crate_qty_each = fields.Integer('Crate Qty each')

    product_id = fields.Many2one('product.product', string='Product')
    thick = fields.Float(compute="_get_fields", string='Thick', digits=dp.get_precision('OneDecimal'))
    width = fields.Float(compute="_get_fields", string='Width', digits=dp.get_precision('ZeroDecimal'))
    length = fields.Float(compute="_get_fields", string='Length', digits=dp.get_precision('ZeroDecimal'))
    glue_id = fields.Many2one(compute="_get_fields", comodel_name='pwk.glue', string='Glue')
    grade_id = fields.Many2one(compute="_get_fields", comodel_name='pwk.grade', string='Grade')
    marking = fields.Char(related='sale_line_id.marking', string='Marking')
    
    quantity = fields.Float('Quantity', digits=dp.get_precision('TwoDecimal'))
    volume = fields.Float(compute="_get_volume", string='Volume', digits=dp.get_precision('FourDecimal'))

    bom_ids = fields.One2many('pwk.packing.list.line.detail', 'reference', string='Lines')


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
                

class PwkPackingList(models.Model):    
    _name = "pwk.packing.list"

    name = fields.Char('Nomor Packing List')
    date = fields.Date('Date', default=fields.Date.today())
    certificate_id = fields.Many2one('pwk.certificate', 'Certificate')
    is_logo = fields.Boolean('Show Legal Logo', default=True)
    
    partner_id = fields.Many2one(compute="_get_fields", comodel_name='res.partner', string='Buyer')
    destination_id = fields.Many2one(compute="_get_fields", comodel_name='pwk.destination', string='Destination')
    payment_term_id = fields.Many2one(compute="_get_fields", comodel_name='account.payment.term', string='Payment Terms')
    marking = fields.Char(compute="_get_fields", string='Marking')
    po_number = fields.Char(compute="_get_fields", string='Contract')

    line_ids = fields.One2many('pwk.packing.list.line', 'reference', string='Lines')
    state = fields.Selection([('Draft','Draft'),('Done','Done')], string="Status", default="Draft")

    tanggal_selesai = fields.Date('Target Produksi')
    tanggal_emisi = fields.Date('Hasil Uji Emisi')
    tanggal_terakhir = fields.Date('Produksi P1/P2')

    total_volume = fields.Float(compute="_get_total_volume", string="Total Volume")

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
            ('suffix', '=', '.' + year_month + '.PL.PWK')
        ])
        if not sequence_id :
            sequence_id = self.env['ir.sequence'].sudo().create({
                'name': name,
                'code': obj,
                'implementation': 'no_gap',
                'suffix': '.' + year_month + '.PL.PWK',
                'padding': 3
            })
        return sequence_id.next_by_id()

    @api.model
    def create(self, vals):
        year_month = ''
        vals['name'] = self.get_sequence('Packing List', 'pwk.packing.list', '%s' % year_month)
        return super(PwkPackingList, self).create(vals)

    @api.multi
    def print_packing_list_produksi(self):                
        return self.env.ref('v12_pwk.packing_list_produksi').report_action(self)
