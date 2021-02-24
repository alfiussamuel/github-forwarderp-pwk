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


class PwkRpmContainerLine(models.Model):    
    _name = "pwk.rpm.container.line"

    reference = fields.Many2one('pwk.rpm.container', string='Reference')
    rpm_line_id = fields.Many2one('pwk.rpm.line', string="RPM Line")
    sale_id = fields.Many2one('sale.order', 'No. Order')
    sale_line_id = fields.Many2one('sale.order.line', 'No. Order Line')
    partner_id = fields.Many2one(compute="_get_sale_fields", comodel_name='res.partner', string='Buyer')
    product_id = fields.Many2one(compute="_get_sale_fields", comodel_name='product.product', string='Product')
    thick = fields.Float(compute="_get_sale_fields", string='Thick', digits=dp.get_precision('ZeroDecimal'))
    width = fields.Float(compute="_get_sale_fields", string='Width', digits=dp.get_precision('ZeroDecimal'))
    length = fields.Float(compute="_get_sale_fields", string='Length', digits=dp.get_precision('ZeroDecimal'))
    glue_id = fields.Many2one(compute="_get_sale_fields", comodel_name='pwk.glue', string='Glue')
    grade_id = fields.Many2one(compute="_get_sale_fields", comodel_name='pwk.grade', string='Grade')        
    total_volume = fields.Float(compute="_get_sale_fields", string='Total Volume', digits=dp.get_precision('FourDecimal'))
    job_order_status = fields.Char(compute="_get_sale_fields", string='Job Order Status')
    container_qty = fields.Float('Quantity', digits=dp.get_precision('TwoDecimal'))
    container_vol = fields.Float(compute="_get_container_vol", string='Cont Vol')

    @api.depends('container_qty')
    def _get_container_vol(self):
        for res in self:
            if res.container_qty:
                res.container_vol = res.container_qty * res.thick * res.width * res.length / 1000000000

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
                res.total_qty = res.sale_line_id.product_uom_qty
                res.total_volume = res.sale_line_id.volume
                res.job_order_status = res.sale_line_id.order_id.job_order_status

class PwkRpmContainer(models.Model):    
    _name = "pwk.rpm.container"

    reference = fields.Many2one('pwk.rpm', string='Reference')
    name = fields.Char('Container No.')
    line_ids = fields.One2many('pwk.rpm.container.line', 'reference', string='Lines', ondelete="cascade")
    total_product = fields.Float(compute="_get_qty", string='Jumlah Product', digits=dp.get_precision('TwoDecimal'))
    total_product_qty = fields.Float(compute="_get_qty", string='Jumlah Qty Product', digits=dp.get_precision('TwoDecimal'))

    @api.depends('line_ids')
    def _get_qty(self):
        for res in self:
            total_product = 0
            total_product_qty = 0

            if res.line_ids:
                for line in res.line_ids:
                    total_product += 1
                    total_product_qty + line.container_qty

            res.total_product = total_product
            res.total_product_qty = total_product

class PwkRpmLineDetail1(models.Model):    
    _name = "pwk.rpm.line.detail1"

    reference = fields.Many2one('pwk.rpm.line', string='Reference')
    product_id = fields.Many2one('product.product', string='Product')
    thick = fields.Float(string='Thick', digits=dp.get_precision('OneDecimal'))
    width = fields.Float(string='Width', digits=dp.get_precision('ZeroDecimal'))
    length = fields.Float(string='Length', digits=dp.get_precision('ZeroDecimal'))
    quantity = fields.Float(string='Quantity', digits=dp.get_precision('ZeroDecimal'))
    ply = fields.Float(string='Ply', digits=dp.get_precision('ZeroDecimal'))
    available_qty = fields.Float(compute="_get_available_qty", string="Qty Available", digits=dp.get_precision('ZeroDecimal'))
    notes = fields.Text('Notes')
    
    @api.depends('product_id')
    def _get_available_qty(self):
        for res in self:
            if res.product_id:
                res.available_qty = res.product_id.qty_available

class PwkRpmLineDetail2(models.Model):    
    _name = "pwk.rpm.line.detail2"

    reference = fields.Many2one('pwk.rpm.line', string='Reference')
    product_id = fields.Many2one('product.product', string='Product')
    thick = fields.Float(string='Thick', digits=dp.get_precision('OneDecimal'))
    width = fields.Float(string='Width', digits=dp.get_precision('ZeroDecimal'))
    length = fields.Float(string='Length', digits=dp.get_precision('ZeroDecimal'))
    quantity = fields.Float(string='Quantity', digits=dp.get_precision('ZeroDecimal'))
    ply = fields.Float(string='Ply', digits=dp.get_precision('ZeroDecimal'))
    available_qty = fields.Float(compute="_get_available_qty", string="Qty Available", digits=dp.get_precision('ZeroDecimal'))
    notes = fields.Text('Notes')
    
    @api.depends('product_id')
    def _get_available_qty(self):
        for res in self:
            if res.product_id:
                res.available_qty = res.product_id.qty_available

class PwkRpmLineDetail3(models.Model):    
    _name = "pwk.rpm.line.detail3"

    reference = fields.Many2one('pwk.rpm.line', string='Reference')
    product_id = fields.Many2one('product.product', string='Product')
    thick = fields.Float(string='Thick', digits=dp.get_precision('OneDecimal'))
    width = fields.Float(string='Width', digits=dp.get_precision('ZeroDecimal'))
    length = fields.Float(string='Length', digits=dp.get_precision('ZeroDecimal'))
    quantity = fields.Float(string='Quantity', digits=dp.get_precision('ZeroDecimal'))
    ply = fields.Float(string='Ply', digits=dp.get_precision('ZeroDecimal'))
    available_qty = fields.Float(compute="_get_available_qty", string="Qty Available", digits=dp.get_precision('ZeroDecimal'))
    notes = fields.Text('Notes')
    
    @api.depends('product_id')
    def _get_available_qty(self):
        for res in self:
            if res.product_id:
                res.available_qty = res.product_id.qty_available

class PwkRpmLineDetail4(models.Model):    
    _name = "pwk.rpm.line.detail4"

    reference = fields.Many2one('pwk.rpm.line', string='Reference')
    product_id = fields.Many2one('product.product', string='Product')
    thick = fields.Float(string='Thick', digits=dp.get_precision('OneDecimal'))
    width = fields.Float(string='Width', digits=dp.get_precision('ZeroDecimal'))
    length = fields.Float(string='Length', digits=dp.get_precision('ZeroDecimal'))
    quantity = fields.Float(string='Quantity', digits=dp.get_precision('ZeroDecimal'))
    ply = fields.Float(string='Ply', digits=dp.get_precision('ZeroDecimal'))
    available_qty = fields.Float(compute="_get_available_qty", string="Qty Available", digits=dp.get_precision('ZeroDecimal'))
    notes = fields.Text('Notes')
    
    @api.depends('product_id')
    def _get_available_qty(self):
        for res in self:
            if res.product_id:
                res.available_qty = res.product_id.qty_available

class PwkRpmLineDetail5(models.Model):    
    _name = "pwk.rpm.line.detail5"

    reference = fields.Many2one('pwk.rpm.line', string='Reference')
    product_id = fields.Many2one('product.product', string='Product')
    thick = fields.Float(string='Thick', digits=dp.get_precision('OneDecimal'))
    width = fields.Float(string='Width', digits=dp.get_precision('ZeroDecimal'))
    length = fields.Float(string='Length', digits=dp.get_precision('ZeroDecimal'))
    quantity = fields.Float(string='Quantity', digits=dp.get_precision('ZeroDecimal'))
    ply = fields.Float(string='Ply', digits=dp.get_precision('ZeroDecimal'))
    available_qty = fields.Float(compute="_get_available_qty", string="Qty Available", digits=dp.get_precision('ZeroDecimal'))
    notes = fields.Text('Notes')
    
    @api.depends('product_id')
    def _get_available_qty(self):
        for res in self:
            if res.product_id:
                res.available_qty = res.product_id.qty_available

class PwkRpmLineDate(models.Model):    
    _name = "pwk.rpm.line.date"

    reference = fields.Many2one('pwk.rpm.line', string='Reference')
    date = fields.Date('Date')
    quantity_p1 = fields.Integer('Quantity P1', digits=dp.get_precision('ZeroDecimal'))
    quantity_p2 = fields.Integer('Quantity P2', digits=dp.get_precision('ZeroDecimal'))

class PwkRpmLine(models.Model):    
    _name = "pwk.rpm.line"

    reference = fields.Many2one('pwk.rpm', string='Reference')
    container_no = fields.Char('Container')
    sale_id = fields.Many2one('sale.order', 'No. Order')
    sale_line_id = fields.Many2one('sale.order.line', 'No. Order Line')
    rpb_line_id = fields.Many2one('pwk.rpb.line', 'RPB Line')
    rpb_id = fields.Many2one('pwk.rpb', 'RPB')
    destination_id = fields.Many2one(compute="_get_sale_fields", comodel_name='pwk.destination', string='Destination')
    marking = fields.Char(compute="_get_sale_fields", string='Marking')
    po_number = fields.Char(compute="_get_sale_fields", string='PO No.')
    partner_id = fields.Many2one(compute="_get_sale_fields", comodel_name='res.partner', string='Buyer')
    product_id = fields.Many2one(compute="_get_sale_fields", comodel_name='product.product', string='Product')
    thick = fields.Float(compute="_get_sale_fields", string='Thick', digits=dp.get_precision('OneDecimal'))
    width = fields.Float(compute="_get_sale_fields", string='Width', digits=dp.get_precision('ZeroDecimal'))
    length = fields.Float(compute="_get_sale_fields", string='Length', digits=dp.get_precision('ZeroDecimal'))
    glue_id = fields.Many2one(compute="_get_sale_fields", comodel_name='pwk.glue', string='Glue')
    grade_id = fields.Many2one(compute="_get_sale_fields", comodel_name='pwk.grade', string='Grade')        
    spare_qty = fields.Float('Qty Spare (%)', digits=dp.get_precision('ZeroDecimal'))
    
    remaining_qty = fields.Float(string='Qty Remaining')
    remaining_volume = fields.Float(compute="_get_volume", string='Vol Remaining', digits=dp.get_precision('FourDecimal'))

    total_qty = fields.Float(string='Qty RPM', digits=dp.get_precision('ZeroDecimal'))
    total_qty_spare = fields.Float(compute="_get_total_qty_spare", string='Qty RPM (Spare)', digits=dp.get_precision('ZeroDecimal'))
    total_volume = fields.Float(compute="_get_volume", string='Vol RPM', digits=dp.get_precision('FourDecimal'))

    detail_ids_1 = fields.One2many('pwk.rpm.line.detail1', 'reference', string='Lines', ondelete="cascade")
    detail_ids_2 = fields.One2many('pwk.rpm.line.detail2', 'reference', string='Lines', ondelete="cascade")
    detail_ids_3 = fields.One2many('pwk.rpm.line.detail3', 'reference', string='Lines', ondelete="cascade")
    detail_ids_4 = fields.One2many('pwk.rpm.line.detail4', 'reference', string='Lines', ondelete="cascade")
    detail_ids_5 = fields.One2many('pwk.rpm.line.detail5', 'reference', string='Lines', ondelete="cascade")
    date_ids = fields.One2many('pwk.rpm.line.date', 'reference', string='Dates', ondelete='cascade')

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

    total_bom = fields.Integer(compute="_get_total_bom", string="Jumlah BoM", digits=dp.get_precision('ZeroDecimal'))
    total_tebal = fields.Integer(compute="_get_total_bom", string="Tebal BoM", digits=dp.get_precision('ZeroDecimal'))
    percent_tebal = fields.Integer(compute="_get_total_bom", string="RC / Barang Jadi", digits=dp.get_precision('ZeroDecimal'))

    notes = fields.Text('Notes')

    # Total Quantity P1 P2
    quantity_p1_total = fields.Integer(compute="_get_total", string='Total P1', digits=dp.get_precision('ZeroDecimal'))
    quantity_p1_remaining = fields.Integer(compute="_get_total", string="Sisa P1", digits=dp.get_precision('ZeroDecimal'))
    quantity_p2_total = fields.Integer(compute="_get_total", string='Total P2', digits=dp.get_precision('ZeroDecimal'))
    quantity_p2_remaining = fields.Integer(compute="_get_total", string='Sisa P2', digits=dp.get_precision('ZeroDecimal'))

    @api.depends('date_ids.quantity_p1', 'date_ids.quantity_p2', 'total_qty')
    def _get_total(self):
        for res in self:
            quantity_p1_total = 0
            quantity_p2_total = 0

            if res.date_ids:
                for date in res.date_ids:
                    quantity_p1_total += date.quantity_p1
                    quantity_p2_total += date.quantity_p2

            res.quantity_p1_total = quantity_p1_total
            res.quantity_p1_remaining = res.total_qty - quantity_p1_total
            res.quantity_p2_total = quantity_p2_total
            res.quantity_p2_remaining = res.total_qty - quantity_p2_total

    @api.depends('detail_ids_1', 'detail_ids_2', 'detail_ids_3', 'detail_ids_4', 'detail_ids_5',
        'is_selected_detail1', 'is_selected_detail2', 'is_selected_detail3', 'is_selected_detail4', 'is_selected_detail5',
        'is_detail1', 'is_detail2', 'is_detail3', 'is_detail4', 'is_detail5')
    def _get_total_bom(self):
        for res in self:
            total_bom = 0
            total_tebal = 0

            if res.is_selected_detail1:
                for bom in res.detail_ids_1:
                    total_bom += 1
                    total_tebal += bom.product_id.tebal

            elif res.is_selected_detail2:
                for bom in res.detail_ids_2:
                    total_bom += 1
                    total_tebal += bom.product_id.tebal

            elif res.is_selected_detail3:
                for bom in res.detail_ids_3:
                    total_bom += 1
                    total_tebal += bom.product_id.tebal

            elif res.is_selected_detail4:
                for bom in res.detail_ids_4:
                    total_bom += 1
                    total_tebal += bom.product_id.tebal

            elif res.is_selected_detail5:
                for bom in res.detail_ids_5:
                    total_bom += 1
                    total_tebal += bom.product_id.tebal

            res.total_bom = total_bom
            res.total_tebal = total_tebal
            res.percent_tebal = total_tebal / res.thick * 100


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
                res.po_number = res.sale_line_id.order_id.po_number
                res.destination_id = res.sale_line_id.order_id.destination_id
                res.marking = res.sale_line_id.marking

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

class PwkRpmBahanBaku(models.Model):    
    _name = "pwk.rpm.bahan.baku"
    _order = 'goods_type desc,jenis_kayu_id asc,grade_id asc,width desc,thick asc'

    reference = fields.Many2one('pwk.rpm', 'Reference')
    product_id = fields.Many2one('product.product', string='Product')
    
    quantity_available = fields.Float(string='All Stock', digits=dp.get_precision('ZeroDecimal'))
    quantity_needed = fields.Float(compute="_get_fields", string='+/- Quantity', digits=dp.get_precision('ZeroDecimal'))
    quantity_spare = fields.Float(compute="_get_fields", string='+/- Quantity Spare', digits=dp.get_precision('ZeroDecimal'))
    quantity = fields.Float('Quantity', digits=dp.get_precision('ZeroDecimal'))

    volume = fields.Float(compute="_get_volume", string='Volume', digits=dp.get_precision('FourDecimal'))
    volume_needed = fields.Float(compute="_get_volume", string='+/- Volume', digits=dp.get_precision('FourDecimal'))
    volume_spare = fields.Float(compute="_get_volume", string='+/- Volume Spare', digits=dp.get_precision('FourDecimal'))
    
    thick = fields.Float(compute="_get_fields", string='Thick', digits=dp.get_precision('OneDecimal'), store=True)
    width = fields.Float(compute="_get_fields", string='Width', digits=dp.get_precision('ZeroDecimal'), store=True)
    length = fields.Float(compute="_get_fields", string='Length', digits=dp.get_precision('ZeroDecimal'), store=True)
    glue_id = fields.Many2one(compute="_get_fields", comodel_name='pwk.glue', string='Glue', store=True)
    grade_id = fields.Many2one(compute="_get_fields", comodel_name='pwk.grade', string='Grade', store=True)
    jenis_kayu_id = fields.Many2one('pwk.jenis.kayu', related='product_id.jenis_kayu', string='Jenis Kayu', store=True)
    goods_type = fields.Selection(related='product_id.goods_type', string='Goods Type', store=True)

    notes = fields.Text('Notes')

    @api.depends('quantity')
    def _get_volume(self):
        for res in self:
            res.volume = res.quantity * res.thick * res.width * res.length / 1000000000
            res.volume_needed = res.quantity_needed * res.thick * res.width * res.length / 1000000000
            res.volume_spare = res.quantity_spare * res.thick * res.width * res.length / 1000000000

    @api.depends('product_id')
    def _get_fields(self):
        for res in self:
            if res.product_id:
                res.thick = res.product_id.tebal
                res.width = res.product_id.lebar
                res.length = res.product_id.panjang
                res.glue_id = res.product_id.glue.id
                res.grade_id = res.product_id.grade.id
                # res.quantity_available = res.product_id.qty_available
                res.quantity_needed = res.quantity_available - res.quantity
                res.quantity_spare = res.quantity_needed + (res.quantity_needed * 0.1)

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
    container_ids = fields.One2many('pwk.rpm.container', 'reference', string='Container', ondelete="cascade")
    bahan_baku_ids = fields.One2many('pwk.rpm.bahan.baku', 'reference', string='Bahan Baku', ondelete="cascade")

    # Footer
    working_days = fields.Float('Hari Kerja', digits=dp.get_precision('OneDecimal'))
    total_produksi = fields.Float(compute="_get_total_produksi", string='Total Produksi', digits=dp.get_precision('FourDecimal'))
    total_blockboard = fields.Float(compute="_get_total_produksi", string='Total Blockboard', digits=dp.get_precision('FourDecimal'))
    total_plywood = fields.Float(compute="_get_total_produksi", string='Total Plywood', digits=dp.get_precision('FourDecimal'))
    total_lvl = fields.Float(compute="_get_total_produksi", string='Total LVL', digits=dp.get_precision('FourDecimal'))
    total_blockboard_percent = fields.Float(compute="_get_total_produksi", string='Total Blockboard (%)', digits=dp.get_precision('ZeroDecimal'))
    total_plywood_percent = fields.Float(compute="_get_total_produksi", string='Total Plywood (%)', digits=dp.get_precision('ZeroDecimal'))
    total_lvl_percent = fields.Float(compute="_get_total_produksi", string='Total LVL (%)', digits=dp.get_precision('ZeroDecimal'))
    target_per_hari = fields.Float(compute="_get_total_produksi", string='Target / Hari', digits=dp.get_precision('FourDecimal'))

    @api.depends('working_days', 'line_ids.total_qty', 'line_ids.product_id')
    def _get_total_produksi(self):
        for res in self:
            total_blockboard = 0
            total_plywood = 0
            total_lvl = 0
            total_produksi = 0

            if res.line_ids:
                for line in res.line_ids:
                    if line.product_id.goods_type == "Blockboard":
                        total_blockboard += line.total_volume
                    elif line.product_id.goods_type == "Plywood":
                        total_plywood += line.total_volume
                    elif line.product_id.goods_type == "LVL":
                        total_lvl += line.total_volume

            res.total_blockboard = total_blockboard
            res.total_plywood = total_plywood
            res.total_lvl = total_lvl
            res.total_produksi = total_blockboard + total_plywood + total_lvl
            res.total_blockboard_percent = total_blockboard / res.total_produksi * 100
            res.total_plywood_percent = total_plywood / res.total_produksi * 100
            res.total_lvl_percent = total_lvl / res.total_produksi * 100
            res.target_per_hari = res.total_produksi / (res.working_days or 1)

    @api.multi
    def action_create_bahan_baku(self):
        for res in self:
            bom_list = ''

            if res.bahan_baku_ids:
                for bahanbaku in res.bahan_baku_ids:
                    bahanbaku.unlink()

            if res.line_ids:
                for line in res.line_ids:
                    if line.is_selected_detail1 and line.detail_ids_1:
                        bom_list = line.detail_ids_1
                    elif line.is_selected_detail2 and line.detail_ids_2:
                        bom_list = line.detail_ids_2
                    elif line.is_selected_detail3 and line.detail_ids_3:
                        bom_list = line.detail_ids_3
                    elif line.is_selected_detail4 and line.detail_ids_4:
                        bom_list = line.detail_ids_4
                    elif line.is_selected_detail5 and line.detail_ids_5:
                        bom_list = line.detail_ids_5

                    for bom in bom_list:
                        current_product_ids = self.env['pwk.rpm.bahan.baku'].search([
                            ('reference', '=', res.id),
                            ('product_id', '=', bom.product_id.id)
                        ])

                        if not current_product_ids:
                            self.env['pwk.rpm.bahan.baku'].create({
                                'reference': res.id,
                                'product_id': bom.product_id.id,
                                'quantity': bom.quantity,
                            })

                        elif current_product_ids:
                            current_product_ids[0].write({
                                'quantity': current_product_ids[0].quantity + bom.quantity
                            })

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
