# coding: utf-8
from datetime import datetime
from openerp import models, api
import time
from dateutil.parser import parse
from odoo.exceptions import UserError
from odoo import models, fields, api

class ReceiptReport(models.AbstractModel):
    _name = 'report.v12_pwk.report_receipt_report'
    _template = 'v12_pwk.report_receipt_report'

    @api.model
    def _get_report_values(self, docids, data=None):        
        self.model = self.env.context.get('active_model')        
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        receipt_records = []
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
                receipt_ids = self.env['account.payment'].search([
                    ('payment_date','>=', docs.date_from),
                    ('payment_date','<=', docs.date_to),
                    ('partner_id', 'in', partner_ids),
                    ('journal_id', 'in', journal_ids),
                    ('partner_id.customer', '=', True),
                    ], order="payment_date asc")

            elif not journal_ids:    
                receipt_ids = self.env['account.payment'].search([
                    ('payment_date','>=', docs.date_from),
                    ('payment_date','<=', docs.date_to),
                    ('partner_id', 'in', partner_ids),
                    ('partner_id.customer', '=', True),
                    ], order="payment_date asc")

        elif not partner_ids:
            if journal_ids:
                receipt_ids = self.env['account.payment'].search([
                    ('payment_date','>=', docs.date_from),
                    ('payment_date','<=', docs.date_to),                    
                    ('journal_id', 'in', journal_ids),
                    ('partner_id.customer', '=', True),
                    ], order="payment_date asc")
            else:
                receipt_ids = self.env['account.payment'].search([
                    ('payment_date','>=', docs.date_from),
                    ('payment_date','<=', docs.date_to),
                    ('partner_id.customer', '=', True),
                    ], order="payment_date asc")


        if docs.date_from and docs.date_to:
            total_amount = 0
            supplier_name = ''
            description = ''
            invoice_list = ''

            for receipt in receipt_ids:
                # supplier_name = str(receipt.partner_id.name)
                if receipt.communication:
                    description = (receipt.communication)

                if receipt.partner_id:                    
                    supplier_name = str(receipt.partner_id.name)
                
                invoice_list = receipt.invoice_list.replace('False, ','')
                invoice_list = invoice_list.replace('False','')

                receipt_records.append({
                    'date': receipt.payment_date.strftime('%d-%B-%Y'),                    
                    'voucher_no': receipt.name,
                    'invoice_no': invoice_list,
                    'supplier': supplier_name,
                    'description': receipt.new_description,
                    'bank': receipt.journal_id.name,
                    'credit': 0,
                    'debit': receipt.amount,                    
                    })      
                total_amount += receipt.amount
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
            'orders': receipt_records,
            'total': total_records,
        }

class ReceiptReportWizard(models.TransientModel):
    _name = "receipt.report.wizard"
    _description = "Receipt Report Wizard"

    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date')    
    office = fields.Selection([('Temanggung','Temanggung'),('Jakarta','Jakarta')], string='Lokasi', default="Temanggung")
    partner_ids = fields.Many2many('res.partner', string='Partner', domain="[('customer','=',True)]")
    journal_ids = fields.Many2many('account.journal', string="Journal Bank")

    def print_report(self, data):
        self.ensure_one()
        [data] = self.read()
        receipt_ids = self.env['account.payment'].browse([])
        datas = {
            'ids': [],
            'model': 'account.payment',
            'form': data
        }
        
        return self.env.ref('v12_pwk.action_report_receipt_report').with_context(from_transient_model=True).report_action(receipt_ids,data=datas)
