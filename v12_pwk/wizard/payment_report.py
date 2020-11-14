# coding: utf-8
from datetime import datetime
from openerp import models, api
import time
from dateutil.parser import parse
from odoo.exceptions import UserError
from odoo import models, fields, api

class PaymentReport(models.AbstractModel):
    _name = 'report.v12_pwk.report_payment_report'
    _template = 'v12_pwk.report_payment_report'

    @api.model
    def _get_report_values(self, docids, data=None):        
        self.model = self.env.context.get('active_model')        
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        payment_records = []
        partner_records = []
        total_records = []                
        partner_ids = []
        journal_ids = []

        if docs.partner_ids:
            for partner in docs.partner_ids:
                partner_ids.append(partner.id)                

        if docs.journal_ids:
            for journal in docs.journal_ids:
                journal_ids.append(journal.id)

        if partner_ids:
            if journal_ids:
                payment_ids = self.env['account.payment'].search([
                    ('payment_date','>=', docs.date_from),
                    ('payment_date','<=', docs.date_to),
                    ('partner_id', 'in', partner_ids),
                    ('journal_id', 'in', journal_ids),
                    ('partner_id.supplier', '=', True),
                    ], order="payment_date asc")

            elif not journal_ids:    
                payment_ids = self.env['account.payment'].search([
                    ('payment_date','>=', docs.date_from),
                    ('payment_date','<=', docs.date_to),
                    ('partner_id', 'in', partner_ids),
                    ('partner_id.supplier', '=', True),
                    ], order="payment_date asc")

        elif not partner_ids:
            if journal_ids:
                payment_ids = self.env['account.payment'].search([
                    ('payment_date','>=', docs.date_from),
                    ('payment_date','<=', docs.date_to),                    
                    ('journal_id', 'in', journal_ids),
                    ('partner_id.supplier', '=', True),
                    ], order="payment_date asc")
            else:
                payment_ids = self.env['account.payment'].search([
                    ('payment_date','>=', docs.date_from),
                    ('payment_date','<=', docs.date_to),
                    ('partner_id.supplier', '=', True),
                    ], order="payment_date asc")


        if docs.date_from and docs.date_to:
            total_amount = 0
            supplier_name = ''
            description = ''
            invoice_list = ''

            for payment in payment_ids:
                # supplier_name = str(payment.partner_id.name)
                if payment.communication:
                    description = (payment.communication)

                if payment.partner_id:                    
                    supplier_name = str(payment.partner_id.name)
                    
                invoice_list = payment.invoice_list.replace('False, ','')
                invoice_list = invoice_list.replace('False','')

                payment_records.append({
                    'date': payment.payment_date.strftime('%d-%B-%Y'),                    
                    'voucher_no': payment.name,
                    'invoice_no': invoice_list,
                    'supplier': supplier_name,
                    'description': payment.new_description,
                    'bank': payment.journal_id.name,
                    'credit': 0,
                    'debit': payment.amount,                    
                    })      
                total_amount += payment.amount
        else:
            raise UserError("Please enter duration")

        total_records.append({
            'total_credit': 0,
            'total_debit': total_amount,
            'office': docs.office,
            'print_date': fields.Date.today().strftime('%d-%B-%Y'),
            })

        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'orders': payment_records,
            'total': total_records,
        }

class PaymentReportWizard(models.TransientModel):
    _name = "payment.report.wizard"
    _description = "Payment Report Wizard"

    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date')    
    office = fields.Selection([('Temanggung','Temanggung'),('Jakarta','Jakarta')], string='Lokasi', default="Temanggung")
    partner_ids = fields.Many2many('res.partner', string='Partner', domain="[('supplier','=',True)]")
    journal_ids = fields.Many2many('account.journal', string="Journal Bank")

    def print_report(self, data):
        self.ensure_one()
        [data] = self.read()
        payment_ids = self.env['account.payment'].browse([])
        datas = {
            'ids': [],
            'model': 'account.payment',
            'form': data
        }
        
        return self.env.ref('v12_pwk.action_report_payment_report').with_context(from_transient_model=True).report_action(payment_ids,data=datas)
