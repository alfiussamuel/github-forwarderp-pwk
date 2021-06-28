from odoo import api, _, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.constrains('name')
    def _check_name_unique(self):
        for rec in self:
            dups = self.search([('name', '=ilike', rec.name)])
            if len(dups) > 1:
                raise ValidationError(_("The Item Code of the product must be unique!"))
