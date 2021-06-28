from odoo import api, fields, models
from odoo.addons import decimal_precision as dp

class StockPicking(models.Model):
    _inherit = "stock.picking"

    pr_no = fields.Char('PR No. Ref', compute='_get_pr_no')

    @api.one
    def _get_pr_no(self):
        po_rec = self.env['purchase.order'].search([('name', '=', self.origin)], limit=1)
        self.pr_no = po_rec.pr_no or ''

class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    product_qty = fields.Float('To Do', digits=dp.get_precision('Product Unit of Measure'), required=True)
