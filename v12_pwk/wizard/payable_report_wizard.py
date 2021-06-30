# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api


class PayableReport(models.TransientModel):
    _name = "wizard.payable.report"
    _description = "Laporan Payable"

    @api.multi
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'wizard.payable.report'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('v12_pwk.payable_xlsx').report_action(self, data=datas)
