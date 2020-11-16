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

class SaleOrderLineContainer(models.Model):    
    _name = "sale.order.line.container"
    _order = 'number asc'

    reference = fields.Many2one('sale.order.line', 'Reference')
    position_id = fields.Many2one('pwk.position', 'Position')
    pallet_id = fields.Many2one('pwk.pallet', 'Pallet')
    strapping_id = fields.Many2one('pwk.strapping', 'Strapping')    
    qty = fields.Float('Quantity')
    number = fields.Char('Number')

class SaleOrderLine(models.Model):    
    _inherit = "sale.order.line"

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'volume', 'order_id.formula_type')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            final_qty = line.product_uom_qty
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

            if line.order_id.formula_type == "Volume":
                final_qty = line.product_uom_qty * line.volume            

            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, final_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    marking = fields.Char('Marking')
    actual_size = fields.Float('Actual Size')
    thick = fields.Float(compute="_get_size", string='Thick', digits=dp.get_precision('OneDecimal'))
    width = fields.Float(compute="_get_size", string='Width', digits=dp.get_precision('TwoDecimal'))
    length = fields.Float(compute="_get_size", string='Length', digits=dp.get_precision('TwoDecimal'))
    volume = fields.Float(compute="_get_volume", string='Volume', digits=dp.get_precision('FourDecimal'))    
    container_ids = fields.One2many('sale.order.line.container', 'reference', 'Container')
    stempel_id = fields.Many2one('pwk.stempel', 'Stempel')
    sticker_id = fields.Many2one('pwk.sticker', 'Sticker')
    stempel_position = fields.Selection([('Edge','Edge'),('Back','Back'),('Edge and Back','Edge and Back')], string="Position", default="Edge")

    @api.depends('product_id')
    def _get_size(self):
        for res in self:            
            thick = 0
            width = 0 
            length = 0

            if res.product_id:
                thick = res.product_id.tebal_id
                width = res.product_id.lebar_id
                length = res.product_id.panjang_id

            res.thick = thick
            res.width = width
            res.length = length

    @api.depends('width','length','thick')
    def _get_volume(self):
        for res in self:                        
            res.volume = ((res.width * res.length * res.thick)) / 1000000000

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
    mc_id = fields.Many2one('sale.mc', string='Meas. Content')
    discrepancy_id = fields.Many2one('sale.discrepancy', string='Discrepancy')    
    date_order = fields.Date(string='Order Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Date.today())
    office_selection = fields.Selection([('Temanggung','Temanggung'),('Jakarta','Jakarta')], string="Lokasi", default="Temanggung", track_visibility="always")
    certificate_id = fields.Many2one('pwk.certificate', 'Certificate')
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
    total_qty = fields.Float(compute="_get_total", string="Total Qty", digits=dp.get_precision('TwoDecimal'))
    formula_type = fields.Selection([('Volume','Volume'),('PCS','PCS')], string="Price Formula", default="PCS")
    number_contract = fields.Char(compute="_get_contract_no", string="Sales Contract No.")
    job_order_status = fields.Char(string='Job Order Status', default='Not Ready')
    
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

            if res.order_line:                
                for line in res.order_line:                    
                    total_qty += line.product_uom_qty
                    total_volume += line.volume
            
            res.total_qty = total_qty
            res.total_volume = total_volume
                    
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

        	res.amount_total_terbilang_en = new_amount + " Rupiah"

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