from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from num2words import num2words


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    currency_option = fields.Selection([('IDR','IDR'),('USD','USD')], string="Currency", default="IDR")
    bank_account_id = fields.Many2one('res.partner.bank','Partner Bank Acc')
    method_type = fields.Char(compute="_get_amount_bank", string="Cash/Bank")
    check_no = fields.Char('Check No / Ref No.')
    from_text = fields.Char('FROM')
    to_text = fields.Char('TO')
    new_description = fields.Text('Description')
    office_selection = fields.Selection([('Temanggung','Temanggung'),('Jakarta','Jakarta')], string="Lokasi", default="Temanggung")
    invoice_lines = fields.One2many('payment.invoice.line', 'payment_id', string="Invoice Line")
    is_charge = fields.Boolean('Bank Charges')
    bank_charges = fields.Float('Charges Amount')    
    bank_charges_account_id = fields.Many2one('account.account','Charge Account')
    invoice_list = fields.Char(compute="_get_invoice_list", string="Invoices")
    amount_bank_terbilang = fields.Char(compute="_get_amount_bank_terbilang", string="Amount Bank Terbilang")
    document_id = fields.Binary(attachment=True)
    document_id_name = fields.Char("Document Name")
    kode_pajak = fields.Char('Kode Pajak')
    currency_rate = fields.Float('Currency Rate')

    def terbilang_english(self, satuan):
        new_amount = ''

        amount = num2words(satuan)
        text_ids = amount.split(' ')
        for text in text_ids:
            if new_amount:
                new_amount += (" " + text.capitalize())
            else:
                new_amount += (text.capitalize())

        hasil = new_amount + " Dollars"
        return hasil
        
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

    @api.depends('amount','currency_option')
    def _get_amount_bank_terbilang(self):
        for res in self:
            amount = ''
            if res.currency_option == "IDR":
                amount = res.terbilang(res.amount) + " Rupiah"
            elif res.currency_option == "USD":
                amount = str(res.terbilang_english(res.amount))

            res.amount_bank_terbilang = amount

    @api.depends('journal_id')
    def _get_amount_bank(self):
        for res in self:            
            method_type = ""            
            if res.journal_id:            
                if res.journal_id.default_debit_account_id.liquidity_type == "Cash":
                    method_type = "Cash"
                if res.journal_id.default_debit_account_id.liquidity_type == "Bank":
                    method_type = "Transfer"            
            res.method_type = method_type

    @api.depends('invoice_lines.invoice_id')
    def _get_invoice_list(self):
        for res in self:
            invoice_list = ''
            if res.reconciled_invoice_ids:
                for invoice in res.reconciled_invoice_ids:
                    if invoice_list:
                        invoice_list = str(invoice_list) + ", " + str(invoice.number)
                    elif not invoice_list:
                        invoice_list = str(invoice.number)
            res.invoice_list = invoice_list
   
    @api.multi
    def update_invoice_lines(self):
        for inv in self.invoice_lines:
            inv.open_amount = inv.invoice_id.residual 
        self.onchange_partner_id()
        
    @api.onchange('partner_type')
    def _onchange_partner_type(self):
        # Set partner_id domain
        if self.partner_type:
            if not self.env.context.get('default_invoice_ids'):
                self.partner_id = False
            return {'domain': {'partner_id': [(self.partner_type, '=', True)]}}

    @api.onchange('partner_id', 'currency_id')
    def onchange_partner_id(self):
        if self.partner_id and self.payment_type != 'transfer':
            vals = {}
            line = [(6, 0, [])]
            invoice_ids = []
            if self.payment_type == 'outbound' and self.partner_type == 'supplier':
                invoice_ids = self.env['account.invoice'].search([('partner_id', 'in', [self.partner_id.id]),
                                                                  ('state', '=','open'),
                                                                  ('type','=', 'in_invoice'),
                                                                  ('currency_id', '=', self.currency_id.id)])
            if self.payment_type == 'inbound' and self.partner_type == 'supplier':
                invoice_ids = self.env['account.invoice'].search([('partner_id', 'in', [self.partner_id.id]),
                                                                  ('state', '=','open'),
                                                                  ('type','=', 'in_refund'),
                                                                  ('currency_id', '=', self.currency_id.id)])
            if self.payment_type == 'inbound' and self.partner_type == 'customer':
                invoice_ids = self.env['account.invoice'].search([('partner_id', 'in', [self.partner_id.id]),
                                                                  ('state', '=','open'),
                                                                  ('type','=', 'out_invoice'),
                                                                  ('currency_id', '=', self.currency_id.id)])
            if self.payment_type == 'outbound' and self.partner_type == 'customer':
                invoice_ids = self.env['account.invoice'].search([('partner_id', 'in', [self.partner_id.id]),
                                                                  ('state', '=','open'),
                                                                  ('type','=', 'out_refund'),
                                                                  ('currency_id', '=', self.currency_id.id)])

            for inv in invoice_ids[::-1]:
                vals = {
                       'invoice_id': inv.id,
                       }
                line.append((0, 0, vals))

            self.bank_account_id = self.partner_id.bank_account_id
            self.invoice_lines = line
            self.onchnage_amount() 
        
    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        if self.payment_type == 'transfer':
            self.invoice_lines = [(6, 0, [])]
            
        if not self.invoice_ids:
            # Set default partner type for the payment type
            if self.payment_type == 'inbound':
                self.partner_type = 'customer'
            elif self.payment_type == 'outbound':
                self.partner_type = 'supplier'
        # Set payment method domain
        res = self._onchange_journal()
        if not res.get('domain', {}):
            res['domain'] = {}
        res['domain']['journal_id'] = self.payment_type == 'inbound' and [('at_least_one_inbound', '=', True)] or [('at_least_one_outbound', '=', True)]
        res['domain']['journal_id'].append(('type', 'in', ('bank', 'cash')))
        return res
    
    @api.onchange('amount')
    def onchnage_amount(self):
        total = 0.0
        remain = self.amount
        for line in self.invoice_lines:
            if line.open_amount <= remain:
                line.allocation = line.open_amount
                remain -= line.allocation
            else:
                line.allocation = remain
                remain -= line.allocation
            total += line.allocation

    @api.multi
    def post(self):
        """"Override to process multiple invoice using single payment."""
        for rec in self:
            amt = 0            

            if not rec.name:
                # Use the right sequence to set the name
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'
                rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            rec.name = rec.journal_id.code + "/" + rec.currency_option + "/" + rec.name
            if rec.invoice_lines:
                 
                for line in rec.invoice_lines:
                    amt += line.allocation
                if rec.amount < amt:
                    raise ValidationError(("Payment amount must be greater then or equal to '%s'") %(amt))
                if rec.amount > amt:
                    for line in rec.invoice_lines:
                        line.allocation = line.allocation + (rec.amount - amt)
                        break

        result = super(AccountPayment,self).post()
        if result:
            debit_line_vals = []
            credit_line_vals = []
            data_final = []

            destination_move_line_id = self.env['account.move.line'].search([
                ('name', '=', self.name),
                ('move_id.journal_id','=',self.journal_id.id)
            ])

            print ("Destination Move Id ", destination_move_line_id.move_id.name)
            if destination_move_line_id:
                move_id = destination_move_line_id.move_id
                # move_id.button_cancel()
            
            for line in move_id.line_ids:
                line.remove_move_reconcile()

                if line.debit > 0:
                    debit_line_vals = (0,0,{
                        'name': line.name,
                        'journal_id': line.journal_id.id,
                        'date': line.date,
                        'credit': 0,
                        'debit': line.debit * self.currency_rate,
                        'partner_id': line.partner_id.id,
                        'account_id': line.account_id.id
                        })
                    data_final.append(debit_line_vals)

                elif line.credit > 0:
                    credit_line_vals = (0,0,{
                        'name': line.name,
                        'journal_id': line.journal_id.id,
                        'date': line.date,
                        'debit': 0,
                        'credit': line.credit * self.currency_rate,
                        'partner_id': line.partner_id.id,
                        'account_id': line.account_id.id
                        })
                    data_final.append(credit_line_vals)

            print ("Move Lines ", move_id.line_ids)
            print ("Move Lines New ", data_final)
            move_id.button_cancel()
            move_id.unlink()
            # move_id.update({'line_ids': data_final})
    
    def _create_transfer_entry(self, amount):
        move = super(AccountPayment,self)._create_transfer_entry(amount)
        print ("Transfer Entry ", move.name)
        return move

    @api.multi
    def _create_payment_entry(self, amount):
        """ Create a journal entry related to a payment"""
        # If group data
        if self.invoice_ids and self.invoice_lines:
            aml_obj = self.env['account.move.line'].\
                with_context(check_move_validity=False)
            invoice_currency = False
            if self.invoice_ids and\
                    all([x.currency_id == self.invoice_ids[0].currency_id
                         for x in self.invoice_ids]):
                # If all the invoices selected share the same currency,
                # record the paiement in that currency too
                invoice_currency = self.invoice_ids[0].currency_id
            move = self.env['account.move'].create(self._get_move_vals())
            p_id = str(self.partner_id.id)
            for inv in self.invoice_ids:
                amt = 0
                if self.partner_type == 'customer':
                    for line in self.invoice_lines:
                        if line.invoice_id.id == inv.id:
                            if inv.type == 'out_invoice':
                                amt = -(line.allocation)
                            else:
                                amt = line.allocation
                else:
                    for line in self.invoice_lines:
                        if line.invoice_id.id == inv.id:
                            if inv.type == 'in_invoice':
                                amt = line.allocation
                            else:
                                amt = -(line.allocation)

                debit, credit, amount_currency, currency_id =\
                    aml_obj.with_context(date=self.payment_date).\
                    _compute_amount_fields(amt, self.currency_id,
                                          self.company_id.currency_id,
                                          )

                # Write line corresponding to invoice payment
                counterpart_aml_dict =\
                    self._get_shared_move_line_vals(debit,credit, amount_currency,move.id, False)                

                counterpart_aml_dict.update(self._get_counterpart_move_line_vals(inv))
                counterpart_aml_dict.update({'currency_id': currency_id})                
                counterpart_aml = aml_obj.create(counterpart_aml_dict)

                # Reconcile with the invoices and write off
                if self.partner_type == 'customer':
                    handling = 'open'
                    for line in self.invoice_lines:
                        if line.invoice_id.id == inv.id:
                            payment_difference = line.open_amount - line.allocation
                    writeoff_account_id = self.journal_id and self.journal_id.id or False
                    if handling == 'reconcile' and\
                            payment_difference:
                        writeoff_line =\
                            self._get_shared_move_line_vals(0, 0, 0, move.id,
                                                            False)
                        debit_wo, credit_wo, amount_currency_wo, currency_id =\
                            aml_obj.with_context(date=self.payment_date).\
                            _compute_amount_fields(
                                payment_difference,
                                self.currency_id,
                                self.company_id.currency_id,
                                )
                        writeoff_line['name'] = _('Counterpart')
                        writeoff_line['account_id'] = writeoff_account_id
                        writeoff_line['debit'] = debit_wo
                        writeoff_line['credit'] = credit_wo
                        writeoff_line['amount_currency'] = amount_currency_wo
                        writeoff_line['currency_id'] = currency_id
                        writeoff_line = aml_obj.create(writeoff_line)

                        if counterpart_aml['debit']:
                            counterpart_aml['debit'] += credit_wo - debit_wo
                        if counterpart_aml['credit']:
                            counterpart_aml['credit'] += debit_wo - credit_wo
                        counterpart_aml['amount_currency'] -=\
                            amount_currency_wo

                inv.register_payment(counterpart_aml)

            # Write counterpart lines
            if not self.currency_id != self.company_id.currency_id:
                amount_currency = 0

            # Get Final amount after bank charges deduction
            paid_amount_with_charges = self.amount - self.bank_charges

            # Get Liquid Line
            liquidity_aml_dict = self._get_shared_move_line_vals((paid_amount_with_charges), 0, -amount_currency, move.id, False)

            # Update Liquid Lines with additional Information
            liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-(paid_amount_with_charges)))
            # print ("Liquidity aml ", liquidity_aml_dict)

            # Create Account Move Line for Liquid
            aml_obj.create(liquidity_aml_dict)
                
            # Get Dictionary for Bank Charges Line
            counterpart_aml_dict_bank = self._get_shared_move_line_vals(self.bank_charges, 0, self.bank_charges, move.id, False)
            counterpart_aml_dict_bank.update({
                'account_id': self.bank_charges_account_id.id,
                'currency_id': self.currency_id.id,
                'amount_currency': self.bank_charges,
                'name': 'Bank Charges'
            })
            
            # Create Account Move Line for Bank Charges
            aml_obj.create(counterpart_aml_dict_bank)

            # Post Journal Entries
            move.post()
            return move

        created_moves = super(AccountPayment, self)._create_payment_entry(amount)
        print ("Created Moves ", created_moves.name)
        return created_moves
    
    @api.model
    def create(self,vals):
        res = super(AccountPayment,self).create(vals)
        if vals.get('invoice_lines'):
            res.invoice_ids = res.invoice_lines.mapped('invoice_id')
        return res
    
    @api.multi
    def write(self,vals):
        res = super(AccountPayment,self).write(vals)
        if vals.get('invoice_lines'):
            self.invoice_ids = self.invoice_lines.mapped('invoice_id')
        
        return res

class PaymentInvoiceLine(models.Model):
    _name = 'payment.invoice.line'
    
    payment_id = fields.Many2one('account.payment', string="Payment")
    invoice_id = fields.Many2one('account.invoice', string="Invoice")
    invoice = fields.Char(related='invoice_id.number', string="Invoice Number")
    account_id = fields.Many2one(related="invoice_id.account_id", string="Account")
    date = fields.Date(string='Invoice Date', compute='_get_invoice_data', store=True)
    due_date = fields.Date(string='Due Date', compute='_get_invoice_data', store=True)
    total_amount = fields.Float(string='Total Amount', compute='_get_invoice_data', store=True)
    open_amount = fields.Float(string='Due Amount', compute='_get_invoice_data', store=True)
    allocation = fields.Float(string='Allocation Amount')
    
    @api.multi
    @api.depends('invoice_id')
    def _get_invoice_data(self):
        for data in self:
            invoice_id = data.invoice_id
            data.date = invoice_id.date_invoice
            data.due_date = invoice_id.date_due
            data.total_amount = invoice_id.amount_total 
            data.open_amount = invoice_id.residual
