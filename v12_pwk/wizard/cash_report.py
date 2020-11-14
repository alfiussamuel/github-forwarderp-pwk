# coding: utf-8
from datetime import datetime
from openerp import models, api
import time
from dateutil.parser import parse
from odoo.exceptions import UserError
from odoo import models, fields, api

class CashReport(models.AbstractModel):
    _name = 'report.v12_pwk.report_cash_report'
    _template = 'v12_pwk.report_cash_report'

    @api.model
    def _get_report_values(self, docids, data=None):        
        self.model = self.env.context.get('active_model')        
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        payment_records = []
        partner_records = []
        total_records = []                
        partner_ids = []
        journal_ids = []        
        balance = 0
        saldo_awal = 0

        if docs.account_id:
            move_ids = self.env['account.move.line'].search([
                ('move_id.date','<', docs.date_from),
                ('move_id.state','<', 'posted'),
                ('account_id', '=', docs.account_id.id),
                ])

            if move_ids:
                for move in move_ids:
                    balance = balance + move.debit - move.credit

            payment_ids = self.env['account.move.line'].search([                
                ('move_id.date','>=', docs.date_from),
                ('move_id.date','<=', docs.date_to),
                ('account_id', '=', docs.account_id.id),                
                ], order="date asc")            

        saldo_awal = balance
        # elif not docs.journal_id:            
        #     payment_ids = self.env['account.payment'].search([                
        #         ('payment_date','=', docs.date_from),
        #         ], order="payment_date asc")
            
        if docs.date_from and docs.account_id:
            subtotal_debit = 0
            subtotal_credit = 0
            subtotal_saldo = 0
            description = ''

            for payment in payment_ids:
                origin_ids = self.env['account.payment'].search([
                    ('move_name','=',payment.move_id.name)
                    ])

                if origin_ids:
                    description = origin_ids[0].new_description

                balance = balance + payment.debit - payment.credit
                payment_records.append({
                    'date': payment.date.strftime('%d-%B-%Y'),
                    'description': description,
                    'debit': payment.debit,
                    'credit': payment.credit,
                    'bank': payment.account_id.name,
                    'saldo': balance,
                    'name': payment.move_id.name,
                    })      

                subtotal_debit += payment.debit
                subtotal_credit += payment.credit

            total_records.append({
                'bank': docs.account_id.name,
                'date_from': docs.date_from.strftime('%d-%B-%Y'),
                'date_to': docs.date_to.strftime('%d-%B-%Y'),
                'total_credit': subtotal_debit,
                'total_debit': subtotal_credit,
                'total_saldo': balance,
                'saldo_awal': saldo_awal,
                'office': docs.office,
                'dibuat_oleh': docs.dibuat_oleh,
                'print_date': fields.Date.today().strftime('%d-%B-%Y'),
                })

        else:
            raise UserError("Please enter duration")        

        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'orders': payment_records,
            'total': total_records,
        }

class CashReportWizard(models.TransientModel):
    _name = "cash.report.wizard"
    _description = "Cash Report Wizard"

    account_id = fields.Many2one('account.account', string='Bank / Cash')
    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date')    
    dibuat_oleh = fields.Char(string='Dibuat')
    office = fields.Selection([('Temanggung','Temanggung'),('Jakarta','Jakarta')], string='Lokasi', default="Temanggung")
    partner_ids = fields.Many2many('res.partner', string='Partner', domain="[('supplier','=',True)]")
    journal_ids = fields.Many2many('account.journal', string="Journal Bank")

    def print_report(self, data):
        self.ensure_one()
        [data] = self.read()
        cash_ids = self.env['account.move'].browse([])
        datas = {
            'ids': [],
            'model': 'account.move',
            'form': data
        }
        
        return self.env.ref('v12_pwk.action_report_cash_report').with_context(from_transient_model=True).report_action(cash_ids,data=datas)
