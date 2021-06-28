from odoo import models, fields, api, _
import time
from odoo.addons import decimal_precision as dp
from  odoo.exceptions import UserError


class bcResPartner(models.Model):
    _inherit = "res.partner"

    local_customer = fields.Boolean(string='Customer Lokal',default=True)