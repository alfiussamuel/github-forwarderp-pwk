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

class SaleMc(models.Model):    
    _name = "sale.mc"

    name = fields.Char('MC')

class SaleDiscrepancy(models.Model):    
    _name = "sale.discrepancy"

    name = fields.Char('Discrepancy')

class PwkPosition(models.Model):    
    _name = "pwk.position"

    name = fields.Char('Position')

class PwkPallet(models.Model):    
    _name = "pwk.pallet"

    name = fields.Char('Pallet')
    document_id = fields.Binary(attachment=True)
    document_id_name = fields.Char("Document Name")

class PwkStempel(models.Model):    
    _name = "pwk.stempel"

    name = fields.Char('Stempel')
    partner_id = fields.Many2one('res.partner', string="Customer", domain="[('customer','=',True)]")
    document_id = fields.Binary(attachment=True)
    document_id_name = fields.Char("Document Name")

class PwkSticker(models.Model):    
    _name = "pwk.sticker"

    name = fields.Char('Sticker')
    partner_id = fields.Many2one('res.partner', string="Customer", domain="[('customer','=',True)]")
    document_id = fields.Binary(attachment=True)
    document_id_name = fields.Char("Document Name")

class PwkMarking(models.Model):    
    _name = "pwk.marking"

    name = fields.Char('Marking')
    partner_id = fields.Many2one('res.partner', string="Customer", domain="[('customer','=',True)]")
    document_id = fields.Binary(attachment=True)
    document_id_name = fields.Char("Document Name")

class PwkStrapping(models.Model):    
    _name = "pwk.strapping"

    name = fields.Char('Name')
    strapping_type = fields.Char('Type')
    qty1 = fields.Char('Quantity 1')
    qty2 = fields.Char('Quantity 2')
    qty3 = fields.Char('Quantity 3')

class PwkPacking(models.Model):    
    _name = "pwk.packing"

    name = fields.Char('Name')

class SaleOrderLineContainer(models.Model):    
    _name = "sale.order.line.container"
    _order = 'id asc'

    reference = fields.Many2one('sale.order.line', 'Reference')
    position_id = fields.Many2one('pwk.position', 'Position')
    pallet_id = fields.Many2one('pwk.pallet', 'Pallet')
    strapping_id = fields.Many2one('pwk.strapping', 'Strapping')    
    total_crates = fields.Float('Total Crates', default=1)
    qty = fields.Float('Quantity / Crate')
    number = fields.Char('Number')    

class SaleOrderLine(models.Model):    
    _inherit = "sale.order.line"
    _order = 'width asc,length asc,thick asc'

    @api.depends('is_changed','product_uom_qty', 'discount', 'price_unit', 'tax_id', 'volume', 'order_id.formula_type')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            final_qty = line.product_uom_qty
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

            if line.order_id.formula_type == "Volume":
                final_qty = line.volume_qty

            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, final_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.multi
    def _get_default_name(self):
        # return "Apasih"
        return self.product_id.name
    
    is_changed = fields.Boolean('Changed', default=True)
    qty_rpb = fields.Float(string='RPB PCS', digits=dp.get_precision('ZeroDecimal'))
    volume_rpb = fields.Float(compute="_get_volume_qty", string='RPB M3', digits=dp.get_precision('FourDecimal'))
    container = fields.Integer('Jumlah Container')
    is_changed = fields.Boolean('Changed')
    is_qty_volume = fields.Boolean('Qty Volume')
    marking = fields.Char('No. Marking')
    marking_id = fields.Many2one('pwk.marking', 'Marking Image')
    actual_size = fields.Float('Actual Size')
    product_uom_qty = fields.Float(string='PCS', digits=dp.get_precision('ZeroDecimal'))
    thick = fields.Float(related="product_id.tebal", string='Thick', digits=dp.get_precision('OneDecimal'), store=True)
    width = fields.Float(related="product_id.lebar", string='Width', digits=dp.get_precision('ZeroDecimal'), store=True)
    length = fields.Float(related="product_id.panjang", string='Length', digits=dp.get_precision('ZeroDecimal'), store=True)
    volume_qty = fields.Float('Qty (Volume)', digits=dp.get_precision('FourDecimal'))
    container_ids = fields.One2many('sale.order.line.container', 'reference', 'Container')
    stempel_id = fields.Many2one('pwk.stempel', 'Stempel')
    sticker_id = fields.Many2one('pwk.sticker', 'Sticker')
    stempel_position = fields.Selection([('Edge','Edge'),('Back','Back'),('Edge and Back','Edge and Back')], string="Position", default="Edge")
    name = fields.Text(string='Description', required=True, default=_get_default_name)

    sale_destination_id = fields.Many2one(related='order_id.destination_id', comodel_name='pwk.destination', string='Destination')
    sale_po_number = fields.Char(related='order_id.po_number', string='PO Number')
    sale_date_order = fields.Date(related='order_id.date_order', string='Date Order')
    sale_partner_id = fields.Many2one(related='order_id.partner_id', comodel_name='res.partner', string='Customer')    
    outstanding_order_pcs = fields.Float(compute="_get_outstanding_order_pcs", string="Outstanding Order")
    total_crate_qty = fields.Float(compute="_get_total_crate_qty", string="Total Qty Crates")    

    crate_number = fields.Integer('Crate Number')
    crate_qty_each = fields.Integer('Crate Qty each')
    crate_qty_total = fields.Integer('Crate Total')
    crate_position_id = fields.Many2one('pwk.position', 'Crate Position')
    crate_pallet_id = fields.Many2one('pwk.pallet', 'Crate Pallet')
    crate_strapping_id = fields.Many2one('pwk.strapping', 'Crate Strapping')

    auto_volume = fields.Float(compute="_get_volume_qty", string='Volume', digits=dp.get_precision('FourDecimal'))
    volume = fields.Float(compute="_get_volume_qty", string='Volume', digits=dp.get_precision('FourDecimal'))

    @api.depends('thick','width','length','product_uom_qty','product_id','is_qty_volume', 'qty_rpb', 'is_changed')
    def _get_volume_qty(self):
        for res in self:                        
            res.volume = ((res.product_uom_qty * res.product_id.tebal * res.product_id.lebar * res.product_id.panjang)) / 1000000000
            res.auto_volume = res.volume
            res.volume_rpb = (res.qty_rpb * res.width * res.length * res.thick) / 1000000000

    @api.depends('container_ids.qty')
    def _get_total_crate_qty(self):
        for res in self:
            total_crate_qty = 0
            if res.container_ids:
                for container in res.container_ids:
                    total_crate_qty += container.qty

            res.total_crate_qty = total_crate_qty

    @api.depends('product_uom_qty', 'product_id')
    def _get_outstanding_order_pcs(self):
        for res in self:
            outstanding_order_pcs = res.product_uom_qty

            rpb_line_ids = self.env['pwk.rpb.line'].search([
                ('product_id', '=', res.product_id.id),
                ('sale_line_id', '=', res.id)
            ])

            if rpb_line_ids:
                for line in rpb_line_ids:
                    outstanding_order_pcs -= line.subtotal_qty

            res.outstanding_order_pcs = outstanding_order_pcs

    @api.depends('product_id')
    def _get_size(self):
        for res in self:            
            thick = 0
            width = 0 
            length = 0

            if res.product_id:
                thick = res.product_id.tebal
                width = res.product_id.lebar
                length = res.product_id.panjang

            res.thick = thick
            res.width = width
            res.length = length

    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product = self.product_id.with_context(
                warehouse=self.order_id.warehouse_id.id,
                lang=self.order_id.partner_id.lang or self.env.user.lang or 'en_US'
            )
            product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
            if float_compare(product.virtual_available, product_qty, precision_digits=precision) == -1:
                is_available = self._check_routing()
                if not is_available:
                    print("Nothing to do")
                    # message =  _('You plan to sell %s %s of %s but you only have %s %s available in %s warehouse.') % \
                    #         (self.product_uom_qty, self.product_uom.name, self.product_id.name, product.virtual_available, product.uom_id.name, self.order_id.warehouse_id.name)
                    # # We check if some products are available in other warehouses.
                    # if float_compare(product.virtual_available, self.product_id.virtual_available, precision_digits=precision) == -1:
                    #     message += _('\nThere are %s %s available across all warehouses.\n\n') % \
                    #             (self.product_id.virtual_available, product.uom_id.name)
                    #     for warehouse in self.env['stock.warehouse'].search([]):
                    #         quantity = self.product_id.with_context(warehouse=warehouse.id).virtual_available
                    #         if quantity > 0:
                    #             message += "%s: %s %s\n" % (warehouse.name, quantity, self.product_id.uom_id.name)
                    # warning_mess = {
                    #     'title': _('Not enough inventory!'),
                    #     'message' : message
                    # }
                    # return {'warning': warning_mess}
        return {}

    @api.onchange('product_id', 'product_uom_qty', 'product_uom')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        # remove the is_custom values that don't belong to this template
        # for pacv in self.product_custom_attribute_value_ids:
        #     if pacv.attribute_value_id not in self.product_id.product_tmpl_id._get_valid_product_attribute_values():
        #         self.product_custom_attribute_value_ids -= pacv

        # remove the no_variant attributes that don't belong to this template
        # for ptav in self.product_no_variant_attribute_value_ids:
        #     if ptav.product_attribute_value_id not in self.product_id.product_tmpl_id._get_valid_product_attribute_values():
        #         self.product_no_variant_attribute_value_ids -= ptav

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        result = {'domain': domain}

        # name = self.get_sale_order_line_multiline_description_sale(product)
        name = product.name
        vals.update(name=name)

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False

        return result

class SaleOrderStempel(models.Model):    
    _name = "sale.order.stempel"

    reference = fields.Many2one('sale.order', 'Reference')
    stempel_id = fields.Many2one('pwk.stempel', 'Stempel')
    position = fields.Selection([('Edge','Edge'),('Back','Back'),('Edge and Back','Edge and Back')], string="Position", default="Edge")

class SaleOrderSticker(models.Model):    
    _name = "sale.order.sticker"

    reference = fields.Many2one('sale.order', 'Reference')
    sticker_id = fields.Many2one('pwk.sticker', 'Sticker')    

class SaleOrderMarking(models.Model):    
    _name = "sale.order.marking"

    reference = fields.Many2one('sale.order', 'Reference')
    marking_id = fields.Many2one('pwk.marking', 'Marking')    

class SaleOrder(models.Model):    
    _inherit = "sale.order"

    port_loading = fields.Many2one('pwk.port','Port Of Loading')
    port_discharge = fields.Many2one('pwk.port','Port Of Discharge')
    destination_id = fields.Many2one('pwk.destination','Destination')
    method_payment_id = fields.Many2one('pwk.method.payment', 'Method of Payment')
    po_number = fields.Char('PO Buyer No.')
    quantity = fields.Char('Quantity')
    thickness = fields.Char('Thickness')
    nama_terang = fields.Selection([('Andreas Hermawan','Andreas Hermawan'),('Adi Widiawan','Adi Widiawan')], string='Nama Terang')
    beneficiary = fields.Text('Beneficiary')
    marking = fields.Char('Marking')
    packing = fields.Char('Packing')
    insurance = fields.Char('Insurance')
    delivery_date = fields.Date('Est. Delivery Date')
    journal_id = fields.Many2one('account.journal', string='Bank Account', domain="[('type','=','bank')]")
    incoterm_id = fields.Many2one('account.incoterms', string='Delivery Method')
    mc_id = fields.Many2one('sale.mc', string='Moisture Content')
    discrepancy_id = fields.Many2one('sale.discrepancy', string='Discrepancy')    
    date_order = fields.Date(string='Order Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Date.today())
    office_selection = fields.Selection([('Temanggung','Temanggung'),('Jakarta','Jakarta')], string="Lokasi", default="Temanggung", track_visibility="always")
    certificate_id = fields.Many2one('pwk.certificate', 'Certificate')
    packing_id = fields.Many2one('pwk.packing', 'Packing')
    is_logo = fields.Boolean('Show Legal Logo', default=True)
    contract_type = fields.Selection([('Lokal','Lokal'),('Export','Export'),('Waste Rotary','Waste Rotary'),('Waste Pabrik PPN','Waste Pabrik PPN'),('Waste Pabrik Non-PPN','Waste Pabrik Non-PPN')], string="Contract Type", default="Lokal")
    amount_total_terbilang = fields.Char(compute="_get_terbilang", string='Amount Total Terbilang')
    amount_total_terbilang_en = fields.Char(compute="_get_terbilang_english", string='Amount Total Terbilang English')
    attn = fields.Char('Attn')
    stempel_ids = fields.One2many('sale.order.stempel', 'reference', 'Stempel')
    marking_ids = fields.One2many('sale.order.marking', 'reference', 'Marking')
    sticker_ids = fields.One2many('sale.order.sticker', 'reference', 'Sticker')
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('Sales Contract', 'Sales Contract'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3, default='draft')
    total_volume = fields.Float(compute="_get_total", string="Total Volume", digits=dp.get_precision('FourDecimal'))
    total_volume_qty = fields.Float(compute="_get_total", string="Total Volume", digits=dp.get_precision('FourDecimal'))
    total_qty = fields.Float(compute="_get_total", string="Total Qty", digits=dp.get_precision('TwoDecimal'))
    formula_type = fields.Selection([('Volume','Volume'),('PCS','PCS')], string="Price Formula", default="PCS")
    number_contract = fields.Char(compute="_get_contract_no", string="Sales Contract No.")
    job_order_status = fields.Char(string='Job Order Status', default='Not Ready')
    is_changed = fields.Boolean('Changed')

    @api.multi
    def button_reload_crate(self):
        for res in self:
            for line in res.order_line:
                if line.container_ids:
                    for container in line.container_ids:
                        container.unlink()

                number = 1
                while number <= line.crate_number: 
                    self.env['sale.order.line.container'].create({
                        'reference': line.id,
                        'position_id': line.crate_position_id.id,
                        'pallet_id': line.crate_pallet_id.id,
                        'strapping_id': line.crate_strapping_id.id,
                        'qty': line.crate_qty_each,
                        'number': number
                    })

                    number += 1

    @api.multi
    def button_change(self):
        for res in self:
            if res.is_changed:
                for line in res.order_line:                    
                    line.write({'is_changed': False})
            else:
                for line in res.order_line:                    
                    line.write({'is_changed': True})
    
    def get_sequence(self, name=False, obj=False, pref=False, context=None):
        sequence_id = self.env['ir.sequence'].search([
            ('name', '=', name),
            ('code', '=', obj),
            ('suffix', '=', '/' + pref + '-PWK/%(month)s-%(year)s')
        ])
        if not sequence_id :
            sequence_id = self.env['ir.sequence'].sudo().create({
                'name': name,
                'code': obj,
                'implementation': 'no_gap',
                'suffix': '/' + pref + '-PWK/%(month)s-%(year)s',
                'padding': 3
            })
        return sequence_id.next_by_id()

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):            
            partner_code = self.env['res.partner'].browse(vals['partner_id']).code
            vals['name'] = self.get_sequence('Sales Order','sale.order','%s'%partner_code)

        # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
        if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            addr = partner.address_get(['delivery', 'invoice'])
            vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
            vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
            vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist and partner.property_product_pricelist.id)
        result = super(SaleOrder, self).create(vals)
        return result

    # @api.multi
    # def action_close_order(self):
    #     for res in self:
    #         if res.is_closed:
                

    def _get_contract_no(self):
        for res in self:
            number_contract = ''
            
            if res.name:                
                number_contract = res.name.replace('SO', 'SC')

            res.number_contract = res.name

    @api.depends('order_line.volume','order_line.product_uom_qty')
    def _get_total(self):
        for res in self:
            total_qty = 0
            total_volume = 0
            total_volume_qty = 0

            if res.order_line:                
                for line in res.order_line:                    
                    total_qty += line.product_uom_qty
                    total_volume += line.volume
                    total_volume_qty = line.volume_qty
            
            res.total_qty = total_qty
            res.total_volume = total_volume
            res.total_volume_qty = total_volume_qty
                    
    def terbilang(self, satuan):
        huruf = ["","Satu","Dua","Tiga","Empat","Lima","Enam","Tujuh","Delapan","Sembilan","Sepuluh","Sebelas"]
        # huruf = ["","One","Two","Three","Four","Five","Six","Seven","Eight","Nine","Ten","Eleven","Twelve"]
        hasil = ""; 
        if satuan < 12: 
            hasil = hasil + huruf[int(satuan)]; 
        elif satuan < 20: 
            hasil = hasil + self.terbilang(satuan-10)+" Belas"; 
        elif satuan < 100:
            hasil = hasil + self.terbilang(satuan/10)+" Puluh "+self.terbilang(satuan%10); 
        elif satuan < 200: 
            hasil=hasil+"Seratus "+self.terbilang(satuan-100); 
        elif satuan < 1000: 
            hasil=hasil+self.terbilang(satuan/100)+" Ratus "+self.terbilang(satuan%100); 
        elif satuan < 2000: 
            hasil=hasil+"Seribu "+self.terbilang(satuan-1000); 
        elif satuan < 1000000: 
            hasil=hasil+self.terbilang(satuan/1000)+" Ribu "+self.terbilang(satuan%1000); 
        elif satuan < 1000000000:
            hasil=hasil+self.terbilang(satuan/1000000)+" Juta "+self.terbilang(satuan%1000000);
        elif satuan < 1000000000000:
            hasil=hasil+self.terbilang(satuan/1000000000)+" Milyar "+self.terbilang(satuan%1000000000)
        elif satuan >= 1000000000000:
            hasil="Angka terlalu besar, harus kurang dari 1 Trilyun!"; 
        return hasil;

    @api.depends('amount_total')
    def _get_terbilang(self):
        for res in self:
            amount = res.terbilang(res.amount_total)
            res.amount_total_terbilang = amount + " Rupiah"

    @api.depends('amount_total')
    def _get_terbilang_english(self):
        for res in self:
        	new_amount = ''

        	amount = num2words(res.amount_total)
        	text_ids = amount.split(' ')
        	for text in text_ids:
        		if new_amount:
        			new_amount += (" " + text.capitalize())
        		else:
        			new_amount += (text.capitalize())

        	res.amount_total_terbilang_en = new_amount + " Dollars"

    @api.multi
    def print_sale_contract(self):                
        return self.env.ref('v12_pwk.sale_contract').report_action(self)

    @api.multi
    def print_lampiran_sale_order(self):                
        return self.env.ref('v12_pwk.lampiran_sale_order').report_action(self)

    @api.multi
    def print_sale_order(self):                
        return self.env.ref('v12_pwk.sale_order').report_action(self)

    @api.multi
    def button_contract(self):
    	for res in self:
    		res.write({'state':'Sales Contract'})