from odoo import fields, models


class Purchase(models.Model):
    _inherit = "purchase.order"

    pr_no = fields.Char('PR Number')

class Partner(models.Model):
    _inherit = "res.partner"

    _sql_constraints = [
        ('name_unique', 'unique (name)', 'The Name of Vendor/Customer should be Unique !')
    ]

