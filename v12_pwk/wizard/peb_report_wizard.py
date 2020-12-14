# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api


class PebReport(models.TransientModel):
    _name = "wizard.peb.report"
    _description = "Laporan PEB"
    
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')    
    currency_id = fields.Many2one('res.currency', 'Currency')
    rate_bi = fields.Float('Rate Kurs BI')

    @api.multi
    def export_xls(self):
        print ('context 1 ', self._context)
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'wizard.peb.report'
        datas['form'] = self.read()[0]
        print('context 2', context)
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('v12_pwk.peb_xlsx').report_action(self, data=datas)
