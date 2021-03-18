from odoo import models, api, _
from odoo.exceptions import UserError


class TriggerOnchangeSale(models.TransientModel):
    _name = "trigger.onchange.sale"
    _description = "Trigger Onchange"

    @api.multi
    def button_trigger(self):
        context = dict(self._context or {})
        lines = self.env['sale.order.line'].browse(context.get('active_ids'))        
        for line in lines:
            if not line.is_change:
                line.write({'is_change': True})
            elif line.is_change:
                line.write({'is_change': False})
        return {'type': 'ir.actions.act_window_close'}