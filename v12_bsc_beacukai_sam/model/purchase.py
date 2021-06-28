from odoo import api, models, fields


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        if not self.product_id:
            return

        # seller = self.product_id._select_seller(
        #     partner_id=self.partner_id,
        #     quantity=self.product_qty,
        #     date=self.order_id.date_order and self.order_id.date_order[:10],
        #     uom_id=self.product_uom)

        # if seller or not self.date_planned:
        #     self.date_planned = self._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        # if not seller:
        #     return

        # price_unit = self.env['account.tax']._fix_tax_included_price_company(seller.price, self.product_id.supplier_taxes_id, self.taxes_id, self.company_id) if seller else 0.0
        # if price_unit and seller and self.order_id.currency_id and seller.currency_id != self.order_id.currency_id:
        #     price_unit = seller.currency_id.compute(price_unit, self.order_id.currency_id)

        # if seller and self.product_uom and seller.product_uom != self.product_uom:
        #     price_unit = seller.product_uom._compute_price(price_unit, self.product_uom)

        # self.price_unit = price_unit

class Purchase(models.Model):
    _inherit = "purchase.order"

    bc_ref_type = fields.Selection([
        ('beacukai.incoming', 'BC IN'),
        ('beacukai.incoming.23', 'BC IN 23'),
        ('beacukai.incoming.27', 'BC IN 27'),
        ('beacukai.incoming.40', 'BC IN 40'),
        ('beacukai.incoming.262', 'BC IN 262'),
        ('beacukai.outgoing', 'BC OUT'),
        ('beacukai.outgoing.25', 'BC OUT 25'),
        ('beacukai.outgoing.27', 'BC OUT 27'),
        ('beacukai.outgoing.30', 'BC OUT 30'),
        ('beacukai.outgoing.41', 'BC OUT 41'),
        ('beacukai.outgoing.261', 'BC OUT 261'),
    ], string='Beacukai Ref Type')
    bc_ref_id = fields.Integer('Referenced Dokumen ID')

class BeacukaiIncoming23(models.Model):
    _inherit = "beacukai.incoming.23"

    purchase_id = fields.Many2one("purchase.order", string="Purchase Order")    

    @api.multi
    def button_po(self):        
        # for res in self:
        #     if res.purchase_id and res.purchase_id.order_line:
        #         for line in res.purchase_id.order_line:
        #             self.env['beacukai.incoming.line.23'].create({
        #                 'reference' : res.id,
        #                 'product_id' : line.product_id.id,
        #                 'purchase_id' : res.purchase_id.id,
        #                 'purchase_line_id' : line.id,
        #                 })

        #     res.purchase_id = False
        purchase_list = []
        if self.purchase_id.order_line:
            for line in self.purchase_id.order_line:
                purchase_list.append(line.id)
                
        return {
                'type': 'ir.actions.act_window',
                'res_model': 'beacukai.add.purchase.wizard',
                'active_ids': self.id,
                'view_mode': 'form',
                'view_type': 'form',
                'views': [(False, 'form')],
                'context': {
                            'default_purchase_id': self.purchase_id.id,
                            'default_beacukai_id': self.id,
                            'default_purchase_line_ids': purchase_list,
                            },
                'target': 'new',
                 }  
