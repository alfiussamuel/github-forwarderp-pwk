# -*- coding: utf-8 -*-

from odoo import api, models


class ReportPurchaseOrder(models.AbstractModel):
    _name = 'report.v10_bsc_com.report_purchaseorder'

    @api.model
    def render_html(self, docids, data=None):
        orders = self.env['purchase.order'].browse(docids)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': "purchase.order",
            'docs': orders,
            'company': self.env.user.company_id
        }

        return self.env['report'].render('v10_bsc_com.report_purchaseorder', docargs)
