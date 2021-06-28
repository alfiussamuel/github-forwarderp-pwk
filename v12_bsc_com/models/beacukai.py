from odoo import api, fields, models


class BeacukaiConfig(models.TransientModel):
    _inherit = "beacukai.config.location"

    location_wip2 = fields.Many2one('stock.location', 'WIP2', domain="[('usage','=','internal')]")

    @api.multi
    def set_beacukai_config(self):
        super(BeacukaiConfig, self).set_beacukai_config()
        self.env['ir.config_parameter'].set_param(
            'location_wip2', (self.location_wip2.id))

    def get_default_beacukai_config(self, fields):
        val = super(BeacukaiConfig, self).get_default_beacukai_config(fields)
        val['location_wip2'] = int(self.env['ir.config_parameter'].get_param('location_wip2'))
        return val

