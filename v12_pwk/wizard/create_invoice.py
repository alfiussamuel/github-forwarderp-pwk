# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class AccountInvoiceCreate(models.TransientModel):
    _name = "account.invoice.create"
    _description = "Create invoices from selected Packing List"

    @api.multi
    def invoice_create(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        print (active_ids)
        # invoice_id = self.env['account.invoice'].create({
        #     'partner_id': 
        # })

        # for record in self.env['pwk.packing.list'].browse(active_ids):
        #     # if record.state != 'draft':
        #     #     raise UserError(_("Selected invoice(s) cannot be confirmed as they are not in 'Draft' state."))
        #     record.action_invoice_open()
        return {'type': 'ir.actions.act_window_close'}
