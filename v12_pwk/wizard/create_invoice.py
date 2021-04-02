# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
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
            'date_invoice': fields.Date.today(),
            'formula_type': packing_list_id.line_ids[0].sale_id.formula_type,
            'payment_term_id': packing_list_id.line_ids[0].sale_id.payment_term_id.id,
            'currency_id': packing_list_id.line_ids[0].sale_id.pricelist_id.currency_id.id,
            'account_id': packing_list_id.partner_id.property_account_receivable_id.id,
            'port_loading': packing_list_id.line_ids[0].sale_id.port_loading.id,
            'port_discharge': packing_list_id.line_ids[0].sale_id.port_discharge.id,
            'destination_id': packing_list_id.line_ids[0].sale_id.destination_id.id,
            'method_payment_id': packing_list_id.line_ids[0].sale_id.method_payment_id.id,
            'sale_order_no': packing_list_id.line_ids[0].sale_id.name,
            'packing_list_no': packing_list_id.name,
            'do_number': packing_list_id.picking_id.name,
            'do_date': packing_list_id.picking_id.scheduled_date.date(),
            'po_number': packing_list_id.line_ids[0].sale_id.po_number,
            'contract_no': packing_list_id.line_ids[0].sale_id.number_contract,
            'certificate_id': packing_list_id.line_ids[0].sale_id.certificate_id.id,
            'seal_no': packing_list_id.picking_id.seal_no,
            'container_no': packing_list_id.picking_id.container_no
        })

        # Create invoice lines
        for record in self.env['pwk.packing.list'].browse(active_ids):
            for line in record.line_ids:
                self.env['account.invoice.line'].create({
                    'invoice_id': invoice_id.id,
                    'product_id': line.product_id.id,
                    'thick': line.product_id.tebal,
                    'width': line.product_id.lebar,
                    'length': line.product_id.panjang,
                    'name': line.product_id.name,
                    'account_id': line.product_id.categ_id.property_account_income_categ_id.id,
                    'sheet': line.quantity,
                    'quantity': line.volume,
                    'uom_id': line.product_id.uom_id.id,
                    'marking': line.marking,
                    'price_unit': line.sale_line_id.price_unit
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
