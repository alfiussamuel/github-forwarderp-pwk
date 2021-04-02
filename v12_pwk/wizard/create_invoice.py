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
        packing_list_id = self.env['pwk.packing.list'].browse(active_ids)[0]
        journal_id = self.env['account.journal'].search([('type', '=', 'sale')])

        invoice_id = self.env['account.invoice'].create({
            'partner_id': packing_list_id.partner_id.id,
            'journal_id': journal_id.id,
            'account_id': packing_list_id.partner_id.property_account_receivable_id.id
        })

        form_view_id = self.env.ref("account.invoice_form").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer Invoices',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'res_id': invoice_id.id,
            'views': [(form_view_id, 'form')],
            'target': 'current',
        }

        # return {'type': 'ir.actions.act_window_close'}
