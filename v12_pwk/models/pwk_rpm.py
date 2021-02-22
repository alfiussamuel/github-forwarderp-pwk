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


class PwkRpmLineDetail1(models.Model):    
    _name = "pwk.rpm.line.detail1"

    reference = fields.Many2one('pwk.rpm.line', string='Reference')
    product_id = fields.Many2one('product.product', string='Product')
    thick = fields.Float(string='Thick')
    width = fields.Float(string='Width')    
    length = fields.Float(string='Length')
    quantity = fields.Float(string='Quantity')
    available_qty = fields.Float(compute="_get_available_qty", string="Qty Available")
    
    @api.depends('product_id')
    def _get_available_qty(self):
        for res in self:
            if res.product_id:
                res.available_qty = res.product_id.qty_available

class PwkRpmLineDetail2(models.Model):    
    _name = "pwk.rpm.line.detail2"

    reference = fields.Many2one('pwk.rpm.line', string='Reference')
    product_id = fields.Many2one('product.product', string='Product')
    thick = fields.Float(string='Thick')
    width = fields.Float(string='Width')
    length = fields.Float(string='Length')
    quantity = fields.Float(string='Quantity')
    available_qty = fields.Float(compute="_get_available_qty", string="Qty Available")
    
    @api.depends('product_id')
    def _get_available_qty(self):
        for res in self:
            if res.product_id:
                res.available_qty = res.product_id.qty_available

class PwkRpmLineDetail3(models.Model):    
    _name = "pwk.rpm.line.detail3"

    reference = fields.Many2one('pwk.rpm.line', string='Reference')
    product_id = fields.Many2one('product.product', string='Product')
    thick = fields.Float(string='Thick')
    width = fields.Float(string='Width')
    length = fields.Float(string='Length')
    quantity = fields.Float(string='Quantity')
    available_qty = fields.Float(compute="_get_available_qty", string="Qty Available")
    
    @api.depends('product_id')
    def _get_available_qty(self):
        for res in self:
            if res.product_id:
                res.available_qty = res.product_id.qty_available

class PwkRpmLineDetail4(models.Model):    
    _name = "pwk.rpm.line.detail4"

    reference = fields.Many2one('pwk.rpm.line', string='Reference')
    product_id = fields.Many2one('product.product', string='Product')
    thick = fields.Float(string='Thick')
    width = fields.Float(string='Width')
    length = fields.Float(string='Length')
    quantity = fields.Float(string='Quantity')
    available_qty = fields.Float(compute="_get_available_qty", string="Qty Available")
    
    @api.depends('product_id')
    def _get_available_qty(self):
        for res in self:
            if res.product_id:
                res.available_qty = res.product_id.qty_available

class PwkRpmLineDetail5(models.Model):    
    _name = "pwk.rpm.line.detail5"

    reference = fields.Many2one('pwk.rpm.line', string='Reference')
    product_id = fields.Many2one('product.product', string='Product')
    thick = fields.Float(string='Thick')
    width = fields.Float(string='Width')
    length = fields.Float(string='Length')
    quantity = fields.Float(string='Quantity')
    available_qty = fields.Float(compute="_get_available_qty", string="Qty Available")
    
    @api.depends('product_id')
    def _get_available_qty(self):
        for res in self:
            if res.product_id:
                res.available_qty = res.product_id.qty_available

class PwkRpmLine(models.Model):    
    _name = "pwk.rpm.line"

    reference = fields.Many2one('pwk.rpm', string='Reference')
    sale_id = fields.Many2one('sale.order', 'No. Order')
    sale_line_id = fields.Many2one('sale.order.line', 'No. Order Line')
    rpb_line_id = fields.Many2one('pwk.rpb.line', 'RPB Line')
    rpb_id = fields.Many2one('pwk.rpb', 'RPB')
    partner_id = fields.Many2one(compute="_get_sale_fields", comodel_name='res.partner', string='Buyer')
    product_id = fields.Many2one(compute="_get_sale_fields", comodel_name='product.product', string='Product')
    thick = fields.Float(compute="_get_sale_fields", string='Thick')
    width = fields.Float(compute="_get_sale_fields", string='Width')
    length = fields.Float(compute="_get_sale_fields", string='Length')
    glue_id = fields.Many2one(compute="_get_sale_fields", comodel_name='pwk.glue', string='Glue')
    grade_id = fields.Many2one(compute="_get_sale_fields", comodel_name='pwk.grade', string='Grade')        
    spare_qty = fields.Float('Qty Spare (%)', digits=dp.get_precision('ZeroDecimal'))  
    
    remaining_qty = fields.Float(string='Qty Remaining')
    remaining_volume = fields.Float(compute="_get_volume", string='Vol Remaining', digits=dp.get_precision('FourDecimal'))

    total_qty = fields.Float(string='Qty RPM')
    total_qty_spare = fields.Float(compute="_get_total_qty_spare", string='Qty RPM (Spare)')
    total_volume = fields.Float(compute="_get_volume", string='Vol RPM', digits=dp.get_precision('FourDecimal'))

    detail_ids_1 = fields.One2many('pwk.rpm.line.detail1', 'reference', string='Lines', ondelete="cascade")
    detail_ids_2 = fields.One2many('pwk.rpm.line.detail2', 'reference', string='Lines', ondelete="cascade")
    detail_ids_3 = fields.One2many('pwk.rpm.line.detail3', 'reference', string='Lines', ondelete="cascade")
    detail_ids_4 = fields.One2many('pwk.rpm.line.detail4', 'reference', string='Lines', ondelete="cascade")
    detail_ids_5 = fields.One2many('pwk.rpm.line.detail5', 'reference', string='Lines', ondelete="cascade")

    bom_id = fields.Many2one('mrp.bom', string='BoM')
    is_detail1 = fields.Boolean('Detail 1')
    is_detail2 = fields.Boolean('Detail 2')
    is_detail3 = fields.Boolean('Detail 3')
    is_detail4 = fields.Boolean('Detail 3')
    is_detail5 = fields.Boolean('Detail 3')
    is_selected_detail1 = fields.Boolean('Bill of Material 1')
    is_selected_detail2 = fields.Boolean('Bill of Material 2')
    is_selected_detail3 = fields.Boolean('Bill of Material 3')
    is_selected_detail4 = fields.Boolean('Bill of Material 4')
    is_selected_detail5 = fields.Boolean('Bill of Material 5')    

    @api.depends('total_qty', 'spare_qty')
    def _get_total_qty_spare(self):
        for res in self:
            res.total_qty_spare = res.total_qty + round((res.total_qty * res.spare_qty / 100))

    @api.depends('total_qty', 'remaining_qty')
    def _get_volume(self):
        for res in self:
            res.total_volume = res.total_qty * res.thick * res.width * res.length / 1000000000
            res.remaining_volume = res.remaining_qty * res.thick * res.width * res.length / 1000000000

    @api.depends('sale_line_id')
    def _get_sale_fields(self):
        for res in self:
            if res.sale_line_id:
                res.partner_id = res.sale_line_id.order_id.partner_id.id
                res.product_id = res.sale_line_id.product_id.id
                res.thick = res.sale_line_id.thick
                res.width = res.sale_line_id.width
                res.length = res.sale_line_id.length
                res.glue_id = res.sale_line_id.product_id.glue.id
                res.grade_id = res.sale_line_id.product_id.grade.id

    @api.multi
    def button_reload_bom(self):
        for line in self:
            if line.detail_ids_1:
                for detail in line.detail_ids_1:
                    detail.unlink()

            if line.detail_ids_2:
                for detail in line.detail_ids_2:
                    detail.unlink()

            if line.detail_ids_3:
                for detail in line.detail_ids_3:
                    detail.unlink()

            if line.detail_ids_4:
                for detail in line.detail_ids_4:
                    detail.unlink()

            if line.detail_ids_5:
                for detail in line.detail_ids_5:
                    detail.unlink()

            bom_ids = self.env['mrp.bom'].search([
                ('product_tmpl_id.name', '=', line.product_id.name)
            ])

            if bom_ids:
                if len(bom_ids) >= 1:
                    line.write({'is_detail1': True})
                    for bom_line in bom_ids[0].bom_line_ids:                        
                        self.env['pwk.rpm.line.detail1'].create({
                            'reference': line.id,
                            'product_id': bom_line.product_id.id,
                            'thick': bom_line.product_id.tebal,
                            'width': bom_line.product_id.lebar,
                            'length': bom_line.product_id.panjang,
                            'quantity': bom_line.product_qty * line.total_qty_spare
                        })

                if len(bom_ids) >= 2:
                    line.write({'is_detail2': True})
                    for bom_line in bom_ids[1].bom_line_ids:
                        self.env['pwk.rpm.line.detail2'].create({
                            'reference': line.id,
                            'product_id': bom_line.product_id.id,
                            'thick': bom_line.product_id.tebal,
                            'width': bom_line.product_id.lebar,
                            'length': bom_line.product_id.panjang,
                            'quantity': bom_line.product_qty * line.total_qty_spare
                        })
                    
                if len(bom_ids) >= 3:
                    line.write({'is_detail3': True})                    
                    for bom_line in bom_ids[2].bom_line_ids:
                        self.env['pwk.rpm.line.detail3'].create({
                            'reference': line.id,
                            'product_id': bom_line.product_id.id,
                            'thick': bom_line.product_id.tebal,
                            'width': bom_line.product_id.lebar,
                            'length': bom_line.product_id.panjang,
                            'quantity': bom_line.product_qty * line.total_qty_spare
                        })

                if len(bom_ids) >= 4:
                    line.write({'is_detail4': True})                    
                    for bom_line in bom_ids[3].bom_line_ids:
                        self.env['pwk.rpm.line.detail4'].create({
                            'reference': line.id,
                            'product_id': bom_line.product_id.id,
                            'thick': bom_line.product_id.tebal,
                            'width': bom_line.product_id.lebar,
                            'length': bom_line.product_id.panjang,
                            'quantity': bom_line.product_qty * line.total_qty_spare
                        })

                if len(bom_ids) >= 5:
                    line.write({'is_detail5': True})                    
                    for bom_line in bom_ids[4].bom_line_ids:
                        self.env['pwk.rpm.line.detail5'].create({
                            'reference': line.id,
                            'product_id': bom_line.product_id.id,
                            'thick': bom_line.product_id.tebal,
                            'width': bom_line.product_id.lebar,
                            'length': bom_line.product_id.panjang,
                            'quantity': bom_line.product_qty * line.total_qty_spare
                        })

class PwkRpm(models.Model):    
    _name = "pwk.rpm"

    month = fields.Selection([
        ('Januari','Januari'),
        ('Februari','Februari'),
        ('March','March'),
        ('April','April'),
        ('Mei','Mei'),
        ('Juni','Juni'),
        ('Juli','Juli'),
        ('Agustus','Agustus'),
        ('September','September'),
        ('Oktober','Oktober'),
        ('November','November'),
        ('Desember','Desember')
    ], string="Bulan")

    name = fields.Char('Nomor RPM')
    date_start = fields.Date('Periode')
    date_end = fields.Date('Periode')    
    rpb_id = fields.Many2one('pwk.rpb', string='RPB')    
    is_pr = fields.Boolean('Purchase Request')
    pr_id = fields.Many2one('pwk.purchase.request', string='Purchase Request')
    state = fields.Selection([('Draft','Draft'),('Purchase Request','Purchase Request')], string="Status", default="Draft")
    line_ids = fields.One2many('pwk.rpm.line', 'reference', string='Lines', ondelete="cascade")

    @api.multi
    def action_create_pr(self):
        for res in self:
            product_list = []

            if res.line_ids:
                request_id = self.env['pwk.purchase.request'].create({
                    'date': fields.Date.today(),
                })

                for line in res.line_ids:                    
                    if line.is_detail1 and line.is_selected_detail1:
                        bom_ids = line.detail_ids_1
                    elif line.is_detail2 and line.is_selected_detail2:
                        bom_ids = line.detail_ids_2
                    elif line.is_detail3 and line.is_selected_detail3:
                        bom_ids = line.detail_ids_3
                    elif line.is_detail4 and line.is_selected_detail4:
                        bom_ids = line.detail_ids_4
                    elif line.is_detail5 and line.is_selected_detail5:
                        bom_ids = line.detail_ids_5

                    for bom in bom_ids:
                        if bom.quantity > bom.available_qty:
                            if bom.product_id.id not in product_list:
                                product_list.append(bom.product_id.id)

                                self.env['pwk.purchase.request.line'].create({
                                    'reference': request_id.id,
                                    'product_id': bom.product_id.id,                    
                                    'quantity': bom.quantity - bom.available_qty,
                                })

                            else:
                                current_line_ids = self.env['pwk.purchase.request.line'].search([
                                    ('reference', '=', request_id.id),
                                    ('product_id', '=', bom.product_id.id),
                                ])

                                if current_line_ids:
                                    current_line_ids[0].write({
                                        'quantity': current_line_ids[0].quantity + (bom.quantity - bom.available_qty)
                                    })

            return res.write({
                'pr_id': request_id.id,
                'is_pr': True,
                'state': 'Purchase Request'
            })


    @api.multi
    def button_reload(self):              
        for res in self:
            if res.rpb_id:
                if res.line_ids:
                    for current_line in res.line_ids:
                        current_line.unlink()

                for line in res.rpb_id.line_ids:                
                    rpm_line_id = self.env['pwk.rpm.line'].create({
                        'reference': res.id,
                        'sale_line_id': line.sale_line_id.id,
                        'sale_id': line.sale_line_id.order_id.id,
                        'remaining_qty': line.outstanding_rpb_pcs
                    })

                    if line.is_selected_detail1:
                        bom_ids = line.detail_ids_1
                    elif line.is_selected_detail2:
                        bom_ids = line.detail_ids_2
                    elif line.is_selected_detail3:
                        bom_ids = line.detail_ids_3
                    elif line.is_selected_detail4:
                        bom_ids = line.detail_ids_4
                    elif line.is_selected_detail5:
                        bom_ids = line.detail_ids_5

                    for bom in bom_ids:
                        self.env['pwk.rpm.line.detail1'].create({
                            'reference': rpm_line_id.id,
                            'product_id': bom.product_id.id,
                            'thick': bom.thick,
                            'width': bom.width,
                            'length': bom.length,
                            'quantity': bom.quantity
                        })

                    rpm_line_id.write({
                        'is_selected_detail1': True,
                        'is_detail1': True
                    })

            return True    

    @api.multi
    def button_cancel(self):
        for res in self:
            res.write({
                'state': "Draft",                
                'is_pr': False
            })

            if res.pr_id:
                res.pr_id.unlink() 

    @api.multi
    def button_done(self):
        for res in self:
            res.state = "Done"

    def get_sequence(self, name=False, obj=False, year_month=False, context=None):
        sequence_id = self.env['ir.sequence'].search([
            ('name', '=', name),
            ('code', '=', obj),
            ('suffix', '=', '.' + year_month + '.RPM.PWK')
        ])
        if not sequence_id :
            sequence_id = self.env['ir.sequence'].sudo().create({
                'name': name,
                'code': obj,
                'implementation': 'no_gap',
                'suffix': '.' + year_month + '.RPM.PWK',
                'padding': 3
            })
        return sequence_id.next_by_id()

    @api.model
    def create(self, vals):
        month_name = ''
        # month = vals['date_start'].month
        # year = vals['date_start'].year

        # day_of_month = vals['date_start'].day
        # week_number = (day_of_month - 1) // 7 + 1

        # if month == 1:
        #     month_name = 'Jan'
        # elif month == 2:
        #     month_name = 'Feb'
        # elif month == 3:
        #     month_name = 'Mar'
        # elif month == 4:
        #     month_name = 'Apr'
        # elif month == 5:
        #     month_name = 'Mei'
        # elif month == 6:
        #     month_name = 'Jun'
        # elif month == 7:
        #     month_name = 'Jul'
        # elif month == 8:
        #     month_name = 'Agt'
        # elif month == 9:
        #     month_name = 'Sep'
        # elif month == 10:
        #     month_name = 'Okt'
        # elif month == 11:
        #     month_name = 'Nov'
        # elif month == 12:
        #     month_name = 'Des'

        year_month = 'Week-' + str('1') + '.' + str('Jan') + '-' + str('2021')

        vals['name'] = self.get_sequence('Rencana Produksi Mingguan', 'pwk.rpm', '%s' % year_month)
        return super(PwkRpm, self).create(vals)
