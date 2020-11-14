# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api


class LogReport(models.TransientModel):
    _name = "wizard.log.report"
    _description = "Laporan Stock Log"
    
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')

    @api.multi
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'wizard.log.report'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('v12_pwk.log_xlsx').report_action(self, data=datas)
