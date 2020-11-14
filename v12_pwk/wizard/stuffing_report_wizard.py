# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api


class StuffingReport(models.TransientModel):
    _name = "wizard.stuffing.report"
    _description = "Laporan Stuffing"
    
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    report_type = fields.Selection([('Export','Export'),('Local','Local')], string="Report Type", default="Export")

    @api.multi
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'wizard.stuffing.report'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('v12_pwk.stuffing_xlsx').report_action(self, data=datas)
