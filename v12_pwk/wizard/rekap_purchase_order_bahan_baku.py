# coding: utf-8
from datetime import datetime
from openerp import models, api
import time
from dateutil.parser import parse
from odoo.exceptions import UserError
from odoo import models, fields, api

class RekapPurchaseOrderBahanBaku(models.AbstractModel):
    _name = 'report.v12_pwk.report_rekap_purchase_order_bahan_baku'
    _template = 'v12_pwk.report_rekap_purchase_order_bahan_baku'

    @api.model
    def _get_report_values(self, docids, data=None):        
        self.model = self.env.context.get('active_model')        
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        purchase_records = []        

        if docs.date_from and docs.date_to:
            record_ids = self.env['purchase.order.line'].search([
                ('order_id.date_order','>=',docs.date_from),
                ('order_id.date_order','<=',docs.date_to),
                ])            

            for record in record_ids:
                purchase_records = [].append({                    
                    'name': record.order_id.name
                    })
        else:
            raise UserError("Please enter duration")
        
        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'orders': purchase_records,
        }

class RekapPurchaseOrderBahanBakuWizard(models.TransientModel):
    _name = "rekap.purchase.order.bahan.baku.wizard"
    _description = "Rekap PO Bahan Baku Wizard"

    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date')    
    office = fields.Selection([('Temanggung','Temanggung'),('Jakarta','Jakarta')], string='Lokasi', default="Temanggung")    

    def print_report(self, data):
        self.ensure_one()
        [data] = self.read()
        purchase_line_ids = self.env['purchase.order.line'].browse([])
        datas = {
            'ids': [],
            'model': 'purchase.order.line',
            'form': data
        }
        
        return self.env.ref('v12_pwk.action_report_rekap_purchase_order_bahan_baku').with_context(from_transient_model=True).report_action(purchase_line_ids,data=datas)
