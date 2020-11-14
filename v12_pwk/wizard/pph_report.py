# coding: utf-8
from datetime import datetime
from openerp import models, api
import time
from dateutil.parser import parse
from odoo.exceptions import UserError
from odoo import models, fields, api

class PphReport(models.AbstractModel):
    _name = 'report.v12_pwk.report_pph_report'
    _template = 'v12_pwk.report_pph_report'

    @api.model
    def _get_report_values(self, docids, data=None):        
        self.model = self.env.context.get('active_model')        
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        tax_records = []
        total_records = []
        total_amount = 0
        tax_rate = ""

        if docs.account_id:
            record_ids = self.env['account.move.line'].search([
                ('account_id','=', docs.account_id.id),
                ('move_id.state','=', 'posted'),
                ('move_id.date','>=',docs.date_from),
                ('move_id.date','<=',docs.date_to),
                ])

            tax_ids = self.env['account.tax'].search([
                    ('account_id','=',docs.account_id.id),                    
                    ])

            if tax_ids:
                tax_rate = str(tax_ids[0].amount) + "%"

        if docs.date_from and docs.date_to:
            total_amount = 0
            bukti_potong = ''
            jenis_penghasilan = ''
            nama_wajib_pajak = ''
            alamat_wp = ''
            npwp_wp = ''
            invoice_no = ''
            invoice_amount = 0
            penghasilan_bruto = 0
            tarif = 0
            tax_dipotong = 0
            tax_ditanggung = 0
            total_invoice_amount = 0
            total_penghasilan_bruto = 0
            total_tarif = "0"
            total_tax_amount = 0
            total_tax_dipotong = 0
            total_tax_ditanggung = 0
            keterangan = ''
            invoice_id = ''

            for record in record_ids:
                invoice_ids = self.env['account.invoice'].search([
                    ('number','=',record.move_id.name),                    
                    ])                

                if invoice_ids:
                    invoice_id = invoice_ids[0]
                    bukti_potong = invoice_id.bukti_potong
                    jenis_penghasilan = invoice_id.objek_penghasilan
                    nama_wajib_pajak = invoice_id.partner_id.nama_wajib_pajak
                    alamat_wp = invoice_id.partner_id.alamat_lengkap_text
                    npwp_wp = invoice_id.partner_id.npwp
                    invoice_no = invoice_id.number
                    invoice_amount = invoice_id.amount_untaxed                
                    penghasilan_bruto = invoice_id.dpp_amount
                    tarif = tax_rate
                    tax_amount = invoice_id.amount_tax
                    tax_dipotong = invoice_id.amount_tax
                    tax_ditanggung = 0                
                    keterangan = ''

                tax_records.append({                    
                    'tanggal_pembayaran': record.date.strftime('%d-%b-%Y'),
                    'bukti_potong': bukti_potong,
                    'jenis_penghasilan': jenis_penghasilan,
                    'nama_wajib_pajak': nama_wajib_pajak,
                    'alamat_wp': alamat_wp,
                    'npwp_wp': npwp_wp,
                    'invoice_no': invoice_no,
                    'invoice_amount': invoice_amount,
                    'penghasilan_bruto': penghasilan_bruto,
                    'tarif': tarif,
                    'tax_amount': tax_amount,
                    'tax_dipotong': tax_dipotong,
                    'tax_ditanggung': tax_ditanggung,
                    'keterangan': keterangan,
                    })

                total_invoice_amount += invoice_amount
                total_penghasilan_bruto += penghasilan_bruto
                total_tarif = tarif
                total_tax_amount += tax_amount
                total_tax_dipotong += tax_dipotong
                total_tax_ditanggung += tax_ditanggung

            total_records.append({                
                'period_start': docs.date_from.strftime('%d-%b-%Y'),
                'period_end': docs.date_to.strftime('%d-%b-%Y'),
                'account_name': docs.account_id.short_name,
                'total_invoice_amount': total_invoice_amount,
                'total_penghasilan_bruto': total_penghasilan_bruto,
                'total_tarif': total_tarif,
                'total_tax_amount': total_tax_amount,
                'total_tax_dipotong': total_tax_dipotong,
                'total_tax_ditanggung': total_tax_ditanggung,
                'office': docs.office,
                'print_date': fields.Date.today().strftime('%d-%B-%Y'),
                })

        else:
            raise UserError("Please enter duration")
        
        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'orders': tax_records,
            'total': total_records,
        }

class PphReportWizard(models.TransientModel):
    _name = "pph.report.wizard"
    _description = "PPH Report Wizard"

    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date')    
    office = fields.Selection([('Temanggung','Temanggung'),('Jakarta','Jakarta')], string='Lokasi', default="Temanggung")
    account_id = fields.Many2one('account.account', string='Account')

    def print_report(self, data):
        self.ensure_one()
        [data] = self.read()
        tax_ids = self.env['account.move.line'].browse([])
        datas = {
            'ids': [],
            'model': 'account.move.line',
            'form': data
        }
        
        return self.env.ref('v12_pwk.action_report_pph_report').with_context(from_transient_model=True).report_action(tax_ids,data=datas)
