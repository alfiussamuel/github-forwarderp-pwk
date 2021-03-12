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


class PwkRpbContainerLine(models.Model):    
    _name = "pwk.rpb.container.line"

    reference = fields.Many2one('pwk.rpb.container', string='Reference')
    sale_id = fields.Many2one('sale.order', 'No. Order')
    sale_line_id = fields.Many2one('sale.order.line', 'No. Order Line')
    partner_id = fields.Many2one(compute="_get_sale_fields", comodel_name='res.partner', string='Buyer')
    product_id = fields.Many2one(compute="_get_sale_fields", comodel_name='product.product', string='Product')
    thick = fields.Float(compute="_get_sale_fields", string='Thick')
    width = fields.Float(compute="_get_sale_fields", string='Width')
    length = fields.Float(compute="_get_sale_fields", string='Length')
    glue_id = fields.Many2one(compute="_get_sale_fields", comodel_name='pwk.glue', string='Glue')
    grade_id = fields.Many2one(compute="_get_sale_fields", comodel_name='pwk.grade', string='Grade')        
    total_volume = fields.Float(compute="_get_sale_fields", string='Total Volume', digits=dp.get_precision('FourDecimal'))
    job_order_status = fields.Char(compute="_get_sale_fields", string='Job Order Status')
    total_qty = fields.Float(string='Ordered Qty', digits=dp.get_precision('TwoDecimal'))
    remaining_qty = fields.Float(string='Qty Remaining', digits=dp.get_precision('TwoDecimal'))
    remaining_volume = fields.Float(compute="_get_container_vol", string='Vol Remaining')
    container_qty = fields.Float('Cont Pcs', digits=dp.get_precision('TwoDecimal'))
    container_vol = fields.Float(compute="_get_container_vol", string='Cont Vol')

    @api.depends('container_qty', 'remaining_qty')
    def _get_container_vol(self):
        for res in self:
            if res.container_qty:
                res.container_vol = res.container_qty * res.thick * res.width * res.length / 1000000000

            if res.container_qty:
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
                res.total_qty = res.sale_line_id.product_uom_qty
                res.total_volume = res.sale_line_id.volume
                res.job_order_status = res.sale_line_id.order_id.job_order_status

class PwkRpbContainer(models.Model):    
    _name = "pwk.rpb.container"

    reference = fields.Many2one('pwk.rpb', string='Reference')
    name = fields.Char('Container No.')
    no_container = fields.Char('Container No.')
    jumlah_container = fields.Integer('Jumlah Container')
    line_ids = fields.One2many('pwk.rpb.container.line', 'reference', string='Lines', ondelete="cascade")
    total_product = fields.Float(compute="_get_qty", string='Jumlah Product', digits=dp.get_precision('TwoDecimal'))
    total_product_qty = fields.Float(compute="_get_qty", string='Jumlah Qty Product', digits=dp.get_precision('TwoDecimal'))

    @api.depends('line_ids')
    def _get_qty(self):
        for res in self:
            total_qty = 0
            total_product = 0
            total_product_qty = 0

            if res.line_ids:
                for line in res.line_ids:
                    total_product += 1
                    total_product_qty + line.container_qty

            res.total_product = total_product
            res.total_product_qty = total_product_qty

class PwkRpbLineDetail1(models.Model):    
    _name = "pwk.rpb.line.detail1"

    reference = fields.Many2one('pwk.rpb.line', string='Reference')
    product_id = fields.Many2one('product.product', string='Product')
    thick = fields.Float(string='Thick')
    width = fields.Float(string='Width')
    length = fields.Float(string='Length')
    ply = fields.Float(string='Ply')
    quantity = fields.Float(string='Quantity')
    available_qty = fields.Float(compute="_get_available_qty", string="Qty Available")
    
    @api.depends('product_id')
    def _get_available_qty(self):
        for res in self:
            if res.product_id:
                res.available_qty = res.product_id.qty_available

class PwkRpbLineDetail2(models.Model):    
    _name = "pwk.rpb.line.detail2"

    reference = fields.Many2one('pwk.rpb.line', string='Reference')
    product_id = fields.Many2one('product.product', string='Product')
    thick = fields.Float(string='Thick')
    width = fields.Float(string='Width')
    length = fields.Float(string='Length')
    ply = fields.Float(string='Ply')
    quantity = fields.Float(string='Quantity')
    available_qty = fields.Float(compute="_get_available_qty", string="Qty Available")
    
    @api.depends('product_id')
    def _get_available_qty(self):
        for res in self:
            if res.product_id:
                res.available_qty = res.product_id.qty_available

class PwkRpbLineDetail3(models.Model):    
    _name = "pwk.rpb.line.detail3"

    reference = fields.Many2one('pwk.rpb.line', string='Reference')
    product_id = fields.Many2one('product.product', string='Product')
    thick = fields.Float(string='Thick')
    width = fields.Float(string='Width')
    length = fields.Float(string='Length')
    ply = fields.Float(string='Ply')
    quantity = fields.Float(string='Quantity')
    available_qty = fields.Float(compute="_get_available_qty", string="Qty Available")
    
    @api.depends('product_id')
    def _get_available_qty(self):
        for res in self:
            if res.product_id:
                res.available_qty = res.product_id.qty_available

class PwkRpbLineDetail4(models.Model):    
    _name = "pwk.rpb.line.detail4"

    reference = fields.Many2one('pwk.rpb.line', string='Reference')
    product_id = fields.Many2one('product.product', string='Product')
    thick = fields.Float(string='Thick')
    width = fields.Float(string='Width')
    length = fields.Float(string='Length')
    ply = fields.Float(string='Ply')
    quantity = fields.Float(string='Quantity')
    available_qty = fields.Float(compute="_get_available_qty", string="Qty Available")
    
    @api.depends('product_id')
    def _get_available_qty(self):
        for res in self:
            if res.product_id:
                res.available_qty = res.product_id.qty_available

class PwkRpbLineDetail5(models.Model):    
    _name = "pwk.rpb.line.detail5"

    reference = fields.Many2one('pwk.rpb.line', string='Reference')
    product_id = fields.Many2one('product.product', string='Product')
    thick = fields.Float(string='Thick')
    width = fields.Float(string='Width')
    length = fields.Float(string='Length')
    ply = fields.Float(string='Ply')
    quantity = fields.Float(string='Quantity')
    available_qty = fields.Float(compute="_get_available_qty", string="Qty Available")
    
    @api.depends('product_id')
    def _get_available_qty(self):
        for res in self:
            if res.product_id:
                res.available_qty = res.product_id.qty_available

class PwkRpbLine(models.Model):    
    _name = "pwk.rpb.line"
    _order = 'container_id,width asc,length desc,thick asc'

    reference = fields.Many2one('pwk.rpb', string='Reference')
    is_changed = fields.Boolean('Changed', default=True)
    container_id = fields.Many2one('pwk.rpb.container', string='Container')
    jumlah_container = fields.Integer('Jml Container')
    sale_id = fields.Many2one('sale.order', 'No. Order')
    sale_line_id = fields.Many2one('sale.order.line', 'No. Order Line')
    partner_id = fields.Many2one(compute="_get_sale_fields", comodel_name='res.partner', string='Buyer')
    product_id = fields.Many2one(compute="_get_sale_fields", comodel_name='product.product', string='Product')
    po_number = fields.Char(compute="_get_sale_fields", string='PO No.')
    marking = fields.Char(compute="_get_sale_fields", string='Marking')
    thick = fields.Float(compute="_get_sale_fields", string='Thick', store=True)
    width = fields.Float(compute="_get_sale_fields", string='Width', store=True)
    length = fields.Float(compute="_get_sale_fields", string='Length', store=True)
    glue_id = fields.Many2one(compute="_get_sale_fields", comodel_name='pwk.glue', string='Glue')
    grade_id = fields.Many2one(compute="_get_sale_fields", comodel_name='pwk.grade', string='Grade')        
    total_volume = fields.Float(compute="_get_sale_fields", string='Total Volume', digits=dp.get_precision('FourDecimal'))
    job_order_status = fields.Char(compute="_get_sale_fields", string='Job Order Status')

    total_qty = fields.Float(string='Order PCS', digits=dp.get_precision('TwoDecimal'))
    spare_qty = fields.Float('Qty Spare (%)', digits=dp.get_precision('ZeroDecimal'))  
    total_qty_spare = fields.Float(compute="_get_total_qty_spare", string='Qty Spare')
    total_vol = fields.Float(compute="_get_volume", string='Order M3', digits=dp.get_precision('FourDecimal'))

    container_qty = fields.Float('Cont Pcs', digits=dp.get_precision('TwoDecimal'), store=True)
    container_vol = fields.Float(compute="_get_volume", string='Cont M3', digits=dp.get_precision('FourDecimal'), store=True)
    
    subtotal_qty = fields.Float(compute="_get_subtotal_qty", string='Total RPB PCS', digits=dp.get_precision('TwoDecimal'), store=True)
    subtotal_vol = fields.Float(compute="_get_volume", string='Total RPB M3', digits=dp.get_precision('FourDecimal'), store=True)
    
    outstanding_rpb_pcs = fields.Float(compute="_get_outstanding_rpb", string='Sisa RPB PCS', digits=dp.get_precision('TwoDecimal'), store=True)
    outstanding_rpb_vol = fields.Float(compute="_get_volume", string='Sisa RPB M3', digits=dp.get_precision('FourDecimal'), store=True)
    
    outstanding_order_pcs = fields.Float(string='Sisa Order PCS', digits=dp.get_precision('TwoDecimal'), store=True)
    outstanding_order_vol = fields.Float(compute="_get_volume", string='Sisa Order M3', digits=dp.get_precision('FourDecimal'), store=True)

    detail_ids_1 = fields.One2many('pwk.rpb.line.detail1', 'reference', string='Lines', ondelete="cascade")
    detail_ids_2 = fields.One2many('pwk.rpb.line.detail2', 'reference', string='Lines', ondelete="cascade")
    detail_ids_3 = fields.One2many('pwk.rpb.line.detail3', 'reference', string='Lines', ondelete="cascade")
    detail_ids_4 = fields.One2many('pwk.rpb.line.detail4', 'reference', string='Lines', ondelete="cascade")
    detail_ids_5 = fields.One2many('pwk.rpb.line.detail5', 'reference', string='Lines', ondelete="cascade")

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

    bom_status = fields.Char(compute="_get_bom_status", string='BoM Status', store=True)

    @api.depends('is_selected_detail1','is_selected_detail2','is_selected_detail3','is_selected_detail4','is_selected_detail5')
    def _get_bom_status(self):
        for res in self:
            if res.is_selected_detail1 or res.is_selected_detail2 or res.is_selected_detail3 or res.is_selected_detail4 or res.is_selected_detail5:
                res.bom_status = "Ready"
            else:
                res.bom_status = "Not Ready"

    @api.depends('container_qty', 'spare_qty')
    def _get_total_qty_spare(self):
        for res in self:
            if res.spare_qty == 0:
                res.total_qty_spare = res.container_qty
            else:
                res.total_qty_spare = res.container_qty + round((res.container_qty * res.spare_qty / 100))

    @api.depends('container_qty', 'jumlah_container')
    def _get_subtotal_qty(self):
        for res in self:
            res.subtotal_qty = res.container_qty * res.jumlah_container

    @api.depends('subtotal_qty')
    def _get_outstanding_rpb(self):
        for res in self:
            outstanding_rpb_pcs = res.subtotal_qty

            rpm_line_ids = self.env['pwk.rpm.line'].search([
                ('reference.rpb_id', '=', res.reference.id)
            ])
            
            if rpm_line_ids:
                for line in rpm_line_ids:
                    if line.sale_line_id == res.sale_line_id:
                        outstanding_rpb_pcs -= line.total_qty

            res.outstanding_rpb_pcs = outstanding_rpb_pcs

    @api.depends('container_qty', 'subtotal_qty', 'outstanding_rpb_pcs', 'outstanding_order_pcs', 'total_qty')
    def _get_volume(self):
        for res in self:
            res.container_vol = res.container_qty * res.thick * res.width * res.length / 1000000000
            res.subtotal_vol = res.subtotal_qty * res.thick * res.width * res.length / 1000000000
            res.outstanding_rpb_vol = res.outstanding_rpb_pcs * res.thick * res.width * res.length / 1000000000
            res.outstanding_order_vol = res.outstanding_order_pcs * res.thick * res.width * res.length / 1000000000
            res.total_vol = res.total_qty * res.thick * res.width * res.length / 1000000000

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
                res.po_number = res.sale_line_id.order_id.po_number
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
                        self.env['pwk.rpb.line.detail1'].create({
                            'reference': line.id,
                            'product_id': bom_line.product_id.id,
                            'thick': bom_line.product_id.tebal,
                            'width': bom_line.product_id.lebar,
                            'length': bom_line.product_id.panjang,
                            'ply': bom_line.product_qty,
                            'quantity': bom_line.product_qty * line.total_qty_spare
                        })

                if len(bom_ids) >= 2:
                    line.write({'is_detail2': True})
                    for bom_line in bom_ids[1].bom_line_ids:
                        self.env['pwk.rpb.line.detail2'].create({
                            'reference': line.id,
                            'product_id': bom_line.product_id.id,
                            'thick': bom_line.product_id.tebal,
                            'width': bom_line.product_id.lebar,
                            'length': bom_line.product_id.panjang,
                            'ply': bom_line.product_qty,
                            'quantity': bom_line.product_qty * line.total_qty_spare
                        })
                    
                if len(bom_ids) >= 3:
                    line.write({'is_detail3': True})                    
                    for bom_line in bom_ids[2].bom_line_ids:
                        self.env['pwk.rpb.line.detail3'].create({
                            'reference': line.id,
                            'product_id': bom_line.product_id.id,
                            'thick': bom_line.product_id.tebal,
                            'width': bom_line.product_id.lebar,
                            'length': bom_line.product_id.panjang,
                            'ply': bom_line.product_qty,
                            'quantity': bom_line.product_qty * line.total_qty_spare
                        })

                if len(bom_ids) >= 4:
                    line.write({'is_detail4': True})                    
                    for bom_line in bom_ids[3].bom_line_ids:
                        self.env['pwk.rpb.line.detail4'].create({
                            'reference': line.id,
                            'product_id': bom_line.product_id.id,
                            'thick': bom_line.product_id.tebal,
                            'width': bom_line.product_id.lebar,
                            'length': bom_line.product_id.panjang,
                            'ply': bom_line.product_qty,
                            'quantity': bom_line.product_qty * line.total_qty_spare
                        })

                if len(bom_ids) >= 5:
                    line.write({'is_detail5': True})                    
                    for bom_line in bom_ids[4].bom_line_ids:
                        self.env['pwk.rpb.line.detail5'].create({
                            'reference': line.id,
                            'product_id': bom_line.product_id.id,
                            'thick': bom_line.product_id.tebal,
                            'width': bom_line.product_id.lebar,
                            'length': bom_line.product_id.panjang,
                            'ply': bom_line.product_qty,
                            'quantity': bom_line.product_qty * line.total_qty_spare
                        })

                if len(bom_ids) == 1:
                    line.write({'is_selected_detail1': True})

class PwkRpb(models.Model):    
    _name = "pwk.rpb"

    name = fields.Char('Nomor RPB')

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

    working_days = fields.Float('Hari Kerja', digits=dp.get_precision('OneDecimal'))
    date_start = fields.Date('Periode')
    date_end = fields.Date('Periode')
    state = fields.Selection([('Draft','Draft'),('Purchase Request','Purchase Request')], string="Status", default="Draft")
    line_ids = fields.One2many('pwk.rpb.line', 'reference', string='Lines', ondelete="cascade")
    container_ids = fields.One2many('pwk.rpb.container', 'reference', string='Container', ondelete="cascade")
    total_container = fields.Integer(compute="_get_total_container", string='Total Container')
    rpm_ids = fields.One2many('pwk.rpm', 'rpb_id', string='RPM', ondelete="cascade")
    target = fields.Float('Target ( M3 )', digits=dp.get_precision('FourDecimal'))    
    actual = fields.Float(compute="_get_actual", string='Aktual ( M3 )', digits=dp.get_precision('FourDecimal'))
    is_pr = fields.Boolean('Purchase Request')
    pr_veneer_id = fields.Many2one('pwk.purchase.request', string='PR Veneer Core')
    pr_barecore_id = fields.Many2one('pwk.purchase.request', string='PR Barecore')
    pr_faceback_id = fields.Many2one('pwk.purchase.request', string='PR Veneer FB')
    pr_mdf_id = fields.Many2one('pwk.purchase.request', string='PR MDF')
    rpb_line_count = fields.Integer(string='# of Lines', compute='_get_count')

    @api.multi
    def action_change(self):
        for res in self:
            for line in res.line_ids:
                if line.is_changed:
                    line.write({'is_changed': False})
                else:
                    line.write({'is_changed': True})

    @api.depends('line_ids')
    def _get_total_container(self):
        for res in self:
            total = 0
            if res.line_ids:
                for line in res.line_ids:
                    total += 1
            res.total_container = total

    @api.multi
    def action_view_lines(self):
        action = self.env.ref('v12_pwk.action_pwk_rpb_line').read()[0]
        ids = []
        for res in self:
            if res.line_ids:
                for line in res.line_ids:
                    ids.append(line.id)

        print("IDS ", ids)
        action['domain'] = [('id', 'in', ids)]
        return action

    @api.multi
    def _get_count(self):
        for res in self:
            if res.line_ids:
                res.rpb_line_count = len(res.line_ids)

    @api.multi
    def button_reload_all_bom(self):
        for res in self:
            if res.line_ids:
                for line in res.line_ids:
                    line.button_reload_bom()

            # if res.volume_ids:                
            #     for vol in res.volume_ids:
            #         vol.button_reload_bom()

    @api.multi
    def action_cancel(self):
        for res in self:
            res.pr_veneer_id.button_draft()
            res.pr_barecore_id.button_draft()
            res.pr_faceback_id.button_draft()
            res.pr_mdf_id.button_draft()

            res.pr_veneer_id.unlink()
            res.pr_barecore_id.unlink()
            res.pr_faceback_id.unlink()
            res.pr_mdf_id.unlink()

            res.write({
                'is_pr': False,
                'state': 'Draft',
            })

    @api.multi
    def action_create_pr(self):
        for res in self:
            product_list = []

            if res.line_ids:

                # PR Veneer
                product_list = []
                request_veneer = self.env['pwk.purchase.request'].create({
                    'date': fields.Date.today(),
                    'pr_type': 'Bahan Baku',
                    'formula_type': 'M3',
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
                        if not bom.product_id.goods_type and bom.product_id.jenis_kayu.name != "MDF":
                            if bom.quantity > bom.available_qty:
                                if bom.product_id.id not in product_list:
                                    product_list.append(bom.product_id.id)
                                
                                    self.env['pwk.purchase.request.volume'].create({
                                        'reference': request_veneer.id,
                                        'product_id': bom.product_id.id,
                                        'product_uom_id': bom.product_id.uom_po_id.id,
                                        'volume': 1.1 * ((bom.quantity - bom.available_qty) * line.thick * line.width * line.length / 1000000000)
                                    })

                                else:                                
                                    current_line_ids = self.env['pwk.purchase.request.volume'].search([
                                        ('reference', '=', request_veneer.id),
                                        ('product_id', '=', bom.product_id.id),
                                    ])

                                    if current_line_ids:
                                        current_line_ids[0].write({
                                            'quantity': current_line_ids[0].quantity + (1.1 * ((bom.quantity - bom.available_qty)))
                                        })

                # PR Barecore
                product_list = []
                request_barecore = self.env['pwk.purchase.request'].create({
                    'date': fields.Date.today(),
                    'pr_type': 'Bahan Baku',
                    'formula_type': 'PCS',
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
                        if bom.product_id.goods_type == "Barecore":
                            if bom.quantity > bom.available_qty:
                                if bom.product_id.id not in product_list:
                                    product_list.append(bom.product_id.id)

                                    self.env['pwk.purchase.request.line'].create({
                                        'reference': request_barecore.id,
                                        'product_id': bom.product_id.id,
                                        'product_uom_id': bom.product_id.uom_po_id.id,
                                        'quantity': 1.05 * (bom.quantity - bom.available_qty)
                                    })                            
                                else:
                                    current_line_ids = self.env['pwk.purchase.request.line'].search([
                                        ('reference', '=', request_barecore.id),
                                        ('product_id', '=', bom.product_id.id),
                                    ])

                                    if current_line_ids:
                                        current_line_ids[0].write({
                                            'quantity': current_line_ids[0].quantity + (1.05 * ((bom.quantity - bom.available_qty)))
                                        })


                # PR Faceback
                product_list = []
                request_faceback = self.env['pwk.purchase.request'].create({
                    'date': fields.Date.today(),
                    'pr_type': 'Bahan Baku',
                    'formula_type': 'M3',
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
                        if bom.product_id.goods_type == "Faceback":
                            if bom.quantity > bom.available_qty:
                                if bom.product_id.id not in product_list:
                                    product_list.append(bom.product_id.id)
                                
                                    self.env['pwk.purchase.request.volume'].create({
                                        'reference': request_faceback.id,
                                        'product_id': bom.product_id.id,
                                        'product_uom_id': bom.product_id.uom_po_id.id,
                                        'volume': 1.05 * ((bom.quantity - bom.available_qty) * line.thick * line.width * line.length / 1000000000)
                                    })

                                else:                                
                                    current_line_ids = self.env['pwk.purchase.request.volume'].search([
                                        ('reference', '=', request_faceback.id),
                                        ('product_id', '=', bom.product_id.id),
                                    ])

                                    if current_line_ids:
                                        current_line_ids[0].write({
                                            'quantity': current_line_ids[0].quantity + (1.05 * ((bom.quantity - bom.available_qty)))
                                        })

                # PR MDF
                product_list = []
                request_mdf = self.env['pwk.purchase.request'].create({
                    'date': fields.Date.today(),
                    'pr_type': 'Bahan Baku',
                    'formula_type': 'PCS',
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
                        if bom.product_id.jenis_kayu.name == "MDF":
                            print ("Masuk MDF")
                            if bom.quantity > bom.available_qty:
                                if bom.product_id.id not in product_list:
                                    product_list.append(bom.product_id.id)

                                    self.env['pwk.purchase.request.line'].create({
                                        'reference': request_mdf.id,
                                        'product_id': bom.product_id.id,
                                        'product_uom_id': bom.product_id.uom_po_id.id,
                                        'quantity': 1.05 * (bom.quantity - bom.available_qty)
                                    })                            
                                else:
                                    current_line_ids = self.env['pwk.purchase.request.line'].search([
                                        ('reference', '=', request_mdf.id),
                                        ('product_id', '=', bom.product_id.id),
                                    ])

                                    if current_line_ids:
                                        current_line_ids[0].write({
                                            'quantity': current_line_ids[0].quantity + (1.05 * ((bom.quantity - bom.available_qty)))
                                        })


                res.write({
                    'pr_veneer_id': request_veneer.id,                    
                    'pr_barecore_id': request_barecore.id,
                    'pr_faceback_id': request_faceback.id,
                    'pr_mdf_id': request_mdf.id,
                    'is_pr': True,
                    'state': 'Purchase Request'
                })

        return True

    @api.depends('line_ids.total_volume')
    def _get_actual(self):
        for res in self:
            actual = 0
            if res.line_ids:
                for line in res.line_ids:
                    actual += line.subtotal_vol
            res.actual = actual

    @api.multi
    def button_progress(self):
        for res in self:
            res.state = "Progress"

    @api.multi
    def button_done(self):
        for res in self:
            res.state = "Done"

    def get_sequence(self, name=False, obj=False, year_month=False, context=None):
        sequence_id = self.env['ir.sequence'].search([
            ('name', '=', name),
            ('code', '=', obj),
            ('suffix', '=', '.' + year_month + '.RPB.PWK')
        ])
        if not sequence_id :
            sequence_id = self.env['ir.sequence'].sudo().create({
                'name': name,
                'code': obj,
                'implementation': 'no_gap',
                'suffix': '.' + year_month + '.RPB.PWK',
                'padding': 3
            })
        return sequence_id.next_by_id()

    @api.model
    def create(self, vals):
        month_name = ''
        # month = vals['date_start'].month
        # year = vals['date_start'].year        

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

        year_month = str('Jan') + '-' + str('2021')
        
        vals['name'] = self.get_sequence('Rencana Produksi Bulanan', 'pwk.rpb', '%s' % year_month)
        return super(PwkRpb, self).create(vals)
