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


class PwkPurchaseRequestDateLine(models.Model):
    _name = "pwk.purchase.request.date.line"

    reference = fields.Many2one('pwk.purchase.request.date', string='Reference')        
    product_id = fields.Many2one('product.product', string='Product')
    thick = fields.Float(compute="_get_sale_fields", string='Thick', store=True)
    width = fields.Float(compute="_get_sale_fields", string='Width', store=True)
    length = fields.Float(compute="_get_sale_fields", string='Length', store=True)
    grade_id = fields.Many2one(compute="_get_sale_fields", comodel_name='pwk.grade', string='Grade', store=True)
    quantity = fields.Float(string='PCS')
    volume = fields.Float(compute="_get_volume", string='M3')

    @api.depends('quantity')
    def _get_volume(self):
        for res in self:
            res.volume = res.quantity * res.thick * res.width * res.length / 1000000000    

    @api.depends('product_id')
    def _get_sale_fields(self):
        for res in self:
            if res.product_id:
                res.thick = res.product_id.tebal
                res.width = res.product_id.lebar
                res.length = res.product_id.panjang
                res.grade_id = res.product_id.grade.id    

class PwkPurchaseRequestDate(models.Model):
    _name = "pwk.purchase.request.date"

    reference = fields.Many2one('pwk.purchase.request', string='Reference')            
    date_start = fields.Date('Start Period')
    date_end = fields.Date('End Period')    
    line_ids = fields.One2many('pwk.purchase.request.date.line', 'reference', string='Lines')

class PwkPurchaseRequestVolume(models.Model):
    _name = "pwk.purchase.request.volume"
    _order = "jenis_kayu asc, thick asc,width asc,length asc"

    reference = fields.Many2one('pwk.purchase.request', string='Reference')    
    product_id = fields.Many2one('product.product', string='Product')
    thick = fields.Float(compute="_get_sale_fields", string='Thick', store=True)
    width = fields.Float(compute="_get_sale_fields", string='Width', store=True)
    length = fields.Float(compute="_get_sale_fields", string='Length', store=True)
    jenis_kayu = fields.Char(compute="_get_sale_fields", string='Jenis Kayu', store=True)
    grade_id = fields.Many2one(compute="_get_sale_fields", comodel_name='pwk.grade', string='Grade', store=True)
    date_start = fields.Date('Start Period')
    date_end = fields.Date('End Period')

    volume_ordered = fields.Float(string='Volume PR', digits=dp.get_precision('FourDecimal'))

    quantity = fields.Float(compute="_get_quantity", string='Requested PCS', digits=dp.get_precision('ZeroDecimal'))
    volume = fields.Float(string='Requested M3', digits=dp.get_precision('FourDecimal'))
    
    quantity_pr = fields.Float(compute="_get_quantity", string='Assigned PCS', digits=dp.get_precision('ZeroDecimal'))
    volume_pr = fields.Float(compute="_get_volume", string='Assigned M3', digits=dp.get_precision('FourDecimal'))
    
    quantity_remaining = fields.Float(compute="_get_quantity", string='Remaining PCS', digits=dp.get_precision('ZeroDecimal'))
    volume_remaining = fields.Float(compute="_get_volume", string='Remaining M3', digits=dp.get_precision('FourDecimal'))
    
    product_uom_id = fields.Many2one("uom.uom", string='UoM')
    truck = fields.Char(string='Truck')    

    @api.multi
    def _get_quantity(self):
        for res in self:            
            res.quantity = res.volume / res.product_id.thick/ res.product_id.width / res.product_id.length * 1000000000    
            res.quantity_pr = res.volume_pr / res.product_id.thick / res.product_id.width / res.product_id.length * 1000000000    
            res.quantity_remaining = res.volume_remaining / res.product_id.thick / res.product_id.width / res.product_id.length * 1000000000    

    @api.multi
    def _get_volume(self):
        for res in self:
            volume_remaining = 0
            volume_pr = 0

            if res.reference.date_ids and res.reference.date_ids.line_ids:
                for line in res.reference.date_ids.line_ids:
                    if line.product_id == res.product_id:
                        volume_pr += line.quantity

            res.volume_pr = volume_pr
            res.volume_remaining = res.volume - volume_pr        

    @api.depends('product_id')
    def _get_sale_fields(self):
        for res in self:
            if res.product_id:
                res.thick = res.product_id.tebal
                res.width = res.product_id.lebar
                res.length = res.product_id.panjang
                res.grade_id = res.product_id.grade.id
                res.jenis_kayu = res.product_id.jenis_kayu.name

class PwkPurchaseRequestLine(models.Model):
    _name = "pwk.purchase.request.line"
    _order = "jenis_kayu asc, thick asc,width asc,length asc"

    reference = fields.Many2one('pwk.purchase.request', string='Reference')    
    is_selected = fields.Boolean('.')
    product_id = fields.Many2one('product.product', string='Product')
    thick = fields.Float(compute="_get_sale_fields", string='Thick', store=True)
    width = fields.Float(compute="_get_sale_fields", string='Width', store=True)
    length = fields.Float(compute="_get_sale_fields", string='Length', store=True)
    jenis_kayu = fields.Char(compute="_get_sale_fields", string='Jenis Kayu', store=True)
    grade_id = fields.Many2one(compute="_get_sale_fields", comodel_name='pwk.grade', string='Grade', store=True)
    date_start = fields.Date('Start Period')
    date_end = fields.Date('End Period')

    quantity_ordered = fields.Float(string='PCS', digits=dp.get_precision('ZeroDecimal'))
    volume_ordered = fields.Float(string='M3', digits=dp.get_precision('FourDecimal'))

    quantity = fields.Float(string='Requested PCS', digits=dp.get_precision('ZeroDecimal'))
    volume = fields.Float(compute="_get_volume", string='Requested M3', digits=dp.get_precision('FourDecimal'))
    
    quantity_pr = fields.Float(compute="_get_quantity", string='Assigned PCS', digits=dp.get_precision('ZeroDecimal'))
    volume_pr = fields.Float(compute="_get_volume", string='Assigned M3', digits=dp.get_precision('FourDecimal'))
    
    quantity_remaining = fields.Float(compute="_get_quantity", string='Remaining PCS', digits=dp.get_precision('ZeroDecimal'))
    volume_remaining = fields.Float(compute="_get_volume", string='Remaining M3', digits=dp.get_precision('FourDecimal'))
    
    product_uom_id = fields.Many2one("uom.uom", string='UoM')
    truck = fields.Char(string='Truck')    

    @api.multi
    def _get_quantity(self):
        for res in self:
            quantity_remaining = 0
            quantity_pr = 0

            if res.reference.date_ids and res.reference.date_ids.line_ids:
                for line in res.reference.date_ids.line_ids:
                    if line.product_id == res.product_id:
                        quantity_pr += line.quantity

            res.quantity_pr = quantity_pr
            res.quantity_remaining = res.quantity - quantity_pr

    @api.depends('quantity')
    def _get_volume(self):
        for res in self:
            res.volume = res.quantity * res.thick * res.width * res.length / 1000000000    
            res.volume_pr = res.quantity_pr * res.thick * res.width * res.length / 1000000000    
            res.volume_remaining = res.quantity_remaining * res.thick * res.width * res.length / 1000000000    

    @api.depends('product_id')
    def _get_sale_fields(self):
        for res in self:
            if res.product_id:
                res.thick = res.product_id.tebal
                res.width = res.product_id.lebar
                res.length = res.product_id.panjang
                res.grade_id = res.product_id.grade.id
                res.jenis_kayu = res.product_id.jenis_kayu.name

class PwkPurchaseRequest(models.Model):    
    _name = "pwk.purchase.request"

    pr_type = fields.Selection([('Bahan Baku','Bahan Baku'),('Bahan Penolong','Bahan Penolong')], string='Jenis PR')
    formula_type = fields.Selection([('PCS','PCS'),('M3','M3')], string='Satuan')
    date_id = fields.Many2one('pwk.purchase.request.date', string="Weekly PR")
    name = fields.Char('Nomor PR')
    date_start = fields.Date('Period')
    date_end = fields.Date('Period')
    qty_assign = fields.Integer('Quantity')
    date = fields.Date('Tanggal PR')    
    product_type = fields.Selection([
        ('Produksi','Produksi'),
        ('Mekanik','Mekanik'),
        ('Elektrik','Elektrik'),
        ('Jasa','Jasa')]
        , string="Tipe", default="Produksi")
    state = fields.Selection([
        ('Draft','Draft'),
        ('Department Approved','Department Approved'),
        ('Purchasing Approved','Purchasing Approved'),
        ('Cancelled','Cancelled')]
        , string="Status", default="Draft")
    line_ids = fields.One2many('pwk.purchase.request.line', 'reference', string='Lines')
    volume_ids = fields.One2many('pwk.purchase.request.volume', 'reference', string='Lines')
    date_ids = fields.One2many('pwk.purchase.request.date', 'reference', string='Dates')
    notes = fields.Text('Notes')

    @api.multi
    def button_assign(self):
        for res in self:
            if res.date_start and res.date_end:
                if res.formula_type == "PCS":
                    if res.line_ids:
                        for line in res.line_ids:                        
                            if line.quantity_ordered > 0:
                                if (line.quantity <= line.quantity_remaining):
                                    current_date_id = self.env['pwk.purchase.request.date'].search([
                                        ('reference', '=', res.id),
                                        ('date_start', '=', res.date_start),
                                        ('date_end', '=', res.date_end)
                                    ])

                                    if not current_date_id:
                                        current_date_id = self.env['pwk.purchase.request.date'].create({
                                            'reference': res.id,
                                            'date_start': res.date_start,
                                            'date_end': res.date_end,
                                        })

                                    self.env['pwk.purchase.request.date.line'].create({
                                        'reference': current_date_id.id,
                                        'product_id': line.product_id.id,
                                        'quantity': line.quantity_ordered
                                    })

                                    line.write({                                
                                        'is_selected': False,
                                        'quantity_ordered': 0
                                    })

                                else:
                                    raise UserError(_('Quantity PR melebihi Quantity yang di Request'))

                elif res.formula_type == "M3":
                    if res.volume_ids:
                        for line in res.volume_ids:                        
                            if line.volume_ordered > 0:
                                if (line.volume <= line.volume_remaining):
                                    current_date_id = self.env['pwk.purchase.request.date'].search([
                                        ('reference', '=', res.id),
                                        ('date_start', '=', res.date_start),
                                        ('date_end', '=', res.date_end)
                                    ])

                                    if not current_date_id:
                                        current_date_id = self.env['pwk.purchase.request.date'].create({
                                            'reference': res.id,
                                            'date_start': res.date_start,
                                            'date_end': res.date_end,
                                        })

                                    self.env['pwk.purchase.request.date.line'].create({
                                        'reference': current_date_id.id,
                                        'product_id': line.product_id.id,
                                        'quantity': line.volume_ordered
                                    })

                                    line.write({                                
                                        'is_selected': False,
                                        'volume_ordered': 0
                                    })

                                else:
                                    raise UserError(_('Quantity PR melebihi Quantity yang di Request'))
                
            else:
                raise UserError(_('Periode PR belum diisi'))          

            res.write({
                'date_start': False,
                'date_end': False,
            })


    @api.multi
    def button_draft(self):
        for res in self:
            res.state = "Draft"    

    @api.multi
    def button_approve1(self):
        for res in self:
            res.state = "Department Approved"

    @api.multi
    def button_approve2(self):
        for res in self:
            res.state = "Purchasing Approved"

    def get_sequence(self, name=False, obj=False, product=None, context=None):
        sequence_id = self.env['ir.sequence'].search([
            ('name', '=', name),
            ('code', '=', obj),
            ('suffix', '=', '.PR.' + product + '%(month)s-%(year)s')
        ])
        if not sequence_id :
            sequence_id = self.env['ir.sequence'].sudo().create({
                'name': name,
                'code': obj,
                'implementation': 'no_gap',
                'suffix': '.PR.' + product + '%(month)s-%(year)s',
                'padding': 3
            })
        return sequence_id.next_by_id()

    @api.model
    def create(self, vals):
        product_type = ""

        if vals.get('product_type') == "Produksi":
            product_type = "PD."
        elif vals.get('product_type') == "Mekanik":
            product_type = "MK."
        elif vals.get('product_type') == "Elektrik":
            product_type = "EL."
        elif vals.get('product_type') == "Jasa":
            product_type = "JS."

        vals['name'] = self.get_sequence('Purchase Request', 'pwk.purchase.request', '%s' % product_type)
        # vals['name'] = self.get_sequence('Rencana Produksi Bulanan', 'pwk.rpb', '%s' % year_month)
        return super(PwkPurchaseRequest, self).create(vals)    
