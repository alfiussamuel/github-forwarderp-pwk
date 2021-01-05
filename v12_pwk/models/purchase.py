from odoo import api,fields,models,_
import time
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning
from datetime import datetime, date
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
from dateutil.relativedelta import *
from odoo.tools.safe_eval import safe_eval
import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_compare, float_round
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils
import math
import re

class PurchaseOrderLine(models.Model):    
    _inherit = "purchase.order.line"   

    request_id = fields.Many2one('pwk.purchase.request', 'Purchase Request')
    spp = fields.Char("No. SPP")
    is_changed = fields.Boolean('Changed', default=False)
    qty_surat_jalan = fields.Float('Qty Surat Jalan')
    volume_surat_jalan = fields.Float(compute="_get_volume_ukur", string='Volume Surat Jalan', digits=dp.get_precision('FourDecimal'))
    qty_afkir = fields.Float('Qty Afkir')
    volume_afkir = fields.Float(compute="_get_volume_ukur", string='Volume Afkir', digits=dp.get_precision('FourDecimal'))
    volume_real = fields.Float(compute="_get_volume_ukur", string='Volume', digits=dp.get_precision('FourDecimal'))
    diameter = fields.Float('Diameter')
    panjang = fields.Float('Panjang')
    actual_size = fields.Float('Actual Size')
    actual_thick = fields.Float('Actual T', digits=dp.get_precision('OneDecimal'))
    actual_width = fields.Float('Actual W', digits=dp.get_precision('TwoDecimal'))
    actual_length = fields.Float('Actual L', digits=dp.get_precision('TwoDecimal'))
    invoice_thick = fields.Float('Invoice T', digits=dp.get_precision('OneDecimal'))
    invoice_width = fields.Float('Invoice W', digits=dp.get_precision('TwoDecimal'))
    invoice_length = fields.Float('Invoice L', digits=dp.get_precision('TwoDecimal'))
    note = fields.Char('Notes')
    volume = fields.Float(compute="_get_volume", string='Volume', digits=dp.get_precision('FourDecimal'))

    @api.depends('diameter','qty_surat_jalan','product_qty','qty_afkir','order_id.panjang')
    def _get_volume_ukur(self):
        for res in self:
            if res.diameter > 0:
                res.volume_real = res.product_qty * res.diameter * res.diameter * res.order_id.panjang * 0.785 / 1000000
            else:
                print("masukkk")
                res.volume_real = res.product_qty * res.product_id.panjang * res.product_id.lebar * res.product_id.tebal / 1000000000
                print(res.volume_real)

            res.volume_surat_jalan = res.qty_surat_jalan * res.diameter * res.diameter * res.order_id.panjang * 0.785 / 1000000
            res.volume_afkir = res.qty_afkir * res.diameter * res.diameter * res.order_id.panjang * 0.785 / 1000000    

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'order_id.purchase_type', 'order_id.is_changed')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner'])
            line.update({
                'price_tax': math.ceil(sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    def _prepare_compute_all_values(self):
        # Hook method to returns the different argument values for the
        # compute_all method, due to the fact that discounts mechanism
        # is not implemented yet on the purchase orders.
        # This method should disappear as soon as this feature is
        # also introduced like in the sales module.
        self.ensure_one()
        if self.order_id.purchase_type == "Bahan Penolong" or self.order_id.purchase_type == "Jasa":
            return {
                'price_unit': self.price_unit,
                'currency_id': self.order_id.currency_id,
                'product_qty': self.product_qty,
                'product': self.product_id,
                'partner': self.order_id.partner_id,
            }
        else:
            return {
                'price_unit': self.price_unit,
                'currency_id': self.order_id.currency_id,
                'product_qty': self.volume_real,
                'product': self.product_id,
                'partner': self.order_id.partner_id,
            }

    # @api.onchange('invoice_width','invoice_length','invoice_thick','order_id.formula_type','diameter','panjang','order_id.purchase_type')
    # def _onchange_volume(self):
    #     if self.order_id.purchase_type == "Rotary":
    #         self.volume = self.diameter * self.diameter * self.product_qty *  self.panjang * 0.785 / 1000000
    #     elif self.order_id.formula_type == "PCS":
    #         self.volume = 0
    #     elif self.order_id.formula_type == "Volume":
    #         self.volume = ((self.invoice_width * self.invoice_length * self.invoice_thick)) / 1000000000

    @api.depends('invoice_width','invoice_length','invoice_thick','order_id.formula_type','diameter','panjang','order_id.purchase_type','product_qty')
    def _get_volume(self):
        for res in self:
            if res.order_id.purchase_type == "Rotary":
                res.volume = res.diameter * res.diameter * res.product_qty *  res.panjang * 0.785 / 1000000
            elif res.order_id.formula_type == "PCS":
                res.volume = 0
            elif res.order_id.formula_type == "Volume":
                res.volume = ((res.invoice_width * res.invoice_length * res.invoice_thick)) / 1000000000

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        # Reset date, price and quantity since _onchange_quantity will provide default values
        self.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.price_unit = self.product_qty = 0.0
        self.invoice_thick = self.product_id.tebal
        self.invoice_width = self.product_id.lebar
        self.invoice_length = self.product_id.panjang
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        product_lang = self.product_id.with_context(
            lang=self.partner_id.lang,
            partner_id=self.partner_id.id,
        )
        self.name = product_lang.display_name
        if product_lang.description_purchase:
            self.name += '\n' + product_lang.description_purchase

        self._compute_tax_id()

        self._suggest_quantity()
        self._onchange_quantity()

        return result    

class PurchaseOrderAfkir(models.Model):    
    _name = "purchase.order.afkir"

    reference = fields.Many2one('purchase.order', 'Reference')
    product_id = fields.Many2one('product.product', 'Product')
    diameter = fields.Float('Diameter')
    qty = fields.Float('Quantity')

class PurchaseOrderProduct(models.Model):    
    _name = "purchase.order.product"

    reference = fields.Many2one('purchase.order', 'Reference')    
    diameter = fields.Char('Diameter')
    qty = fields.Float('Quantity')
    price = fields.Float('Unit Price')
    volume = fields.Float('Volume')
    subtotal = fields.Float('Total')

class PurchaseOrder(models.Model):    
    _inherit = "purchase.order"

    is_paid = fields.Boolean('Paid')
    panjang = fields.Float("Panjang")
    kode = fields.Char("Kode")
    no_kendaraan = fields.Char("No. Kendaraan")
    jenis_kayu_id = fields.Many2one('pwk.jenis.kayu', 'Jenis Kayu')
    certificate_id = fields.Many2one('pwk.certificate', 'Certificate')
    is_logo = fields.Boolean('Show Legal Logo', default=True)
    is_hidden = fields.Boolean('SVLK')
    attn = fields.Char("Attn")
    teknis_pembayaran = fields.Text("Teknis Pembayaran")
    payment_to = fields.Text("Pembayaran Ke")    
    office_selection = fields.Selection([('Temanggung','Temanggung'),('Jakarta','Jakarta')], string="Lokasi", default="Temanggung", track_visibility="always")
    export_local = fields.Selection([('Indonesia','Indonesia'),('English','English')], string="Language", default="Indonesia")
    purchase_type = fields.Selection([('Bahan Baku','Bahan Baku'),('Bahan Penolong','Bahan Penolong'),('Jasa','Jasa'),('Rotary','Rotary')], string="Purchase Type", default="Bahan Baku")
    formula_type = fields.Selection([('Volume','Volume'),('PCS','PCS')], string="Price Formula", default="PCS")
    total_qty_surat_jalan = fields.Float(compute="_get_total", string="Total Qty Surat Jalan")
    total_volume_surat_jalan = fields.Float(compute="_get_total", string="Total Vol Surat Jalan")
    total_qty_afkir = fields.Float(compute="_get_total", string="Total Qty Afkir")
    total_volume_afkir = fields.Float(compute="_get_total", string="Total Volume Afkir")
    total_qty = fields.Float(compute="_get_total", string="Total Qty")
    total_volume = fields.Float(compute="_get_total", string="Total Volume")
    selisih = fields.Float(compute="_get_selisih", string="Selisih")
    selisih_kubikasi = fields.Float(compute="_get_selisih", string="Selisih Kubikasi")
    move_id = fields.Many2one('account.move', 'Journal Entries')
    afkir_ids = fields.One2many('purchase.order.afkir', 'reference', string="Detail Afkir")
    product_ids = fields.One2many('purchase.order.product', 'reference', string="Range Diameter")
    request_id = fields.Many2one('pwk.purchase.request', 'Purchase Request', domain="[('state','=','Purchasing Approved')]")
    is_changed = fields.Boolean('Changed', default=False)

    @api.multi
    def button_change(self):
        for res in self:
            if res.is_changed:
                for line in res.order_line:                    
                    line.write({'is_changed': False})
            else:
                for line in res.order_line:                    
                    line.write({'is_changed': True})

    @api.multi
    def button_reload_pr(self):
        for res in self:
            if res.request_id:
                for line in res.request_id.line_ids:
                    self.env['purchase.order.line'].create({
                        'order_id': self.id,
                        'product_id': line.product_id.id,
                        'name': line.product_id.name,
                        'product_qty': line.quantity,
                        'request_line_id': line.id,
                        'request_id': line.reference.id,
                        'date_planned': fields.Date.today(),
                        'price_unit': 1,
                        'product_uom': line.product_id.uom_po_id.id
                    })

    @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step'\
                    or (order.company_id.po_double_validation == 'two_step'\
                        and order.amount_total < self.env.user.company_id.currency_id._convert(
                            order.company_id.po_double_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()))\
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()            

            # Create Journal Hutang Rotary
            journal_ids = self.env['account.journal'].search([
                ('name','=','Vendor Bills')
                ])

            move_id = ''
            if order.purchase_type == "Rotary":
                moveline_ids = []
                debit_line = (0, 0, {
                    'name': order.name,
                    'account_id': order.partner_id.property_account_payable_id.id,
                    'journal_id': journal_ids[0].id,
                    'date': order.date_order.date(),
                    'debit': order.amount_total,
                    'credit': 0,
                })
                moveline_ids.append(debit_line)

                credit_line = (0, 0, {
                    'name': order.name,
                    'account_id': order.partner_id.property_account_payable_id.id,
                    'journal_id': journal_ids[0].id,
                    'date': order.date_order.date(),
                    'credit': order.amount_total,
                    'debit': 0,
                })
                moveline_ids.append(credit_line)

                # Create Journal                
                move_id = self.env['account.move'].create({
                    'narration': order.name,
                    'ref': order.name,
                    'journal_id': journal_ids[0].id,
                    'date': order.date_order.date(),
                    'line_ids': moveline_ids
                    })

                move_id.action_post()

                # Create List Afkir            
                for afkir in order.afkir_ids:
                    afkir.unlink()
                    
                for line in order.order_line:
                    if line.qty_afkir > 0:
                        self.env['purchase.order.afkir'].create({
                            'reference' : order.id,
                            'product_id' : line.product_id.id,
                            'diameter' : line.diameter,
                            'qty' : line.qty_afkir,
                            })

                # Create List Product         
                for product in order.product_ids:
                    product.unlink()

                total_qty1 = total_qty2 = total_qty3 = 0
                price1 = price2 = price3 = 0
                subtotal1 = subtotal2 = subtotal3 = 0
                volume1 = volume2 = volume3 = 0

                for line in order.order_line:
                    if line.diameter == 17 or line.diameter == 18:
                        total_qty1 += line.product_qty
                        price1 = line.price_unit                        
                        volume1 += line.volume_real
                        subtotal1 += line.price_subtotal
                    elif line.diameter > 18 and line.diameter < 25:
                        total_qty2 += line.product_qty
                        price2 = line.price_unit                        
                        volume2 += line.volume_real
                        subtotal2 += line.price_subtotal
                    else:
                        total_qty3 += line.product_qty
                        price3 = line.price_unit                        
                        volume3 += line.volume_real
                        subtotal3 += line.price_subtotal

                if total_qty1 > 1:
                    self.env['purchase.order.product'].create({
                        'reference' : order.id,
                        'diameter' : '17-18',
                        'qty' : total_qty1,
                        'price' : price1,
                        'volume' : volume1,
                        'subtotal' : subtotal1
                        })
                if total_qty2 > 1:
                    self.env['purchase.order.product'].create({
                        'reference' : order.id,
                        'diameter' : '19-24',
                        'qty' : total_qty2,
                        'price' : price2,
                        'volume' : volume2,
                        'subtotal' : subtotal2
                        })

                if total_qty3 > 1:
                    self.env['purchase.order.product'].create({
                        'reference' : order.id,
                        'diameter' : '>25',
                        'qty' : total_qty3,
                        'price' : price3,
                        'volume' : volume3,
                        'subtotal' : subtotal3
                        })

            if move_id:
                order.write({
                    'state': 'to approve',
                    'move_id': move_id.id
                    })

            # Confirm Receipt
            receipt_ids = self.env['stock.picking'].search([
                ('origin', '=', order.name)
            ])

            if receipt_ids:
                for receipt in receipt_ids:
                    receipt.action_confirm()

        return True

    @api.depends('order_line.product_qty','order_line.volume_real','order_line.qty_surat_jalan','order_line.volume_surat_jalan','order_line.qty_afkir','order_line.volume_afkir')
    def _get_selisih(self):
        for res in self:
            res.selisih = res.total_volume_surat_jalan - res.total_volume_afkir
            res.selisih_kubikasi = res.total_volume - res.total_volume_surat_jalan - res.total_volume_afkir

    @api.depends('order_line.product_qty','order_line.volume_real','order_line.qty_surat_jalan','order_line.volume_surat_jalan','order_line.qty_afkir','order_line.volume_afkir')
    def _get_total(self):
        for res in self:
            total_qty = total_volume = total_qty_afkir = total_volume_afkir = total_qty_surat_jalan = total_volume_surat_jalan = 0
            if res.order_line:
                for line in res.order_line:
                    total_qty += line.product_qty
                    total_volume += line.volume_real
                    total_qty_surat_jalan += line.qty_surat_jalan
                    total_volume_surat_jalan += line.volume_surat_jalan
                    total_qty_afkir += line.qty_afkir
                    total_volume_afkir += line.volume_afkir

            res.total_qty = total_qty
            res.total_volume = total_volume
            res.total_qty_afkir = total_qty_afkir
            res.total_volume_afkir = total_volume_afkir
            res.total_qty_surat_jalan = total_qty_surat_jalan
            res.total_volume_surat_jalan = total_volume_surat_jalan

    @api.multi
    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        for order in self:
            if any([ptype in ['product', 'consu'] for ptype in order.order_line.mapped('product_id.type')]):
                pickings = order.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                if not pickings:
                    res = order._prepare_picking()
                    picking = StockPicking.create(res)
                else:
                    picking = pickings[0]
                moves = order.order_line._create_stock_moves(picking)
                # moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                seq = 0
                for move in sorted(moves, key=lambda move: move.date_expected):
                    seq += 5
                    move.sequence = seq
                # moves._action_assign()
                picking.message_post_with_view('mail.message_origin_link',
                    values={'self': picking, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return True
                
    @api.multi
    def print_purchase_order_jasa(self):                
        return self.env.ref('v12_pwk.purchase_order_jasa').report_action(self)    

    @api.multi
    def print_purchase_order_bahan_baku(self):                
        return self.env.ref('v12_pwk.purchase_order_bahan_baku').report_action(self)    

    @api.multi
    def print_purchase_order_bahan_penolong(self):                
        return self.env.ref('v12_pwk.purchase_order_bahan_penolong').report_action(self)    

    @api.multi
    def print_purchase_order_rotary(self):                
        return self.env.ref('v12_pwk.purchase_order_rotary').report_action(self)    

    @api.multi
    def print_nota_pembelian_jenis_kayu(self):                
        return self.env.ref('v12_pwk.nota_pembelian_jenis_kayu').report_action(self)    

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            if vals.get('purchase_type') == "Jasa":
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.order.jasa') or '/'
            elif vals.get('purchase_type') == "Bahan Baku":
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.order.bahan.baku') or '/'
            elif vals.get('purchase_type') == "Bahan Penolong":
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.order.bahan.penolong') or '/'
            elif vals.get('purchase_type') == "Rotary":
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.order.rotary') or '/'
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.order') or '/'
        return super(PurchaseOrder, self).create(vals)
        