import time
import re
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError, except_orm, Warning, RedirectWarning, ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import odoo.addons.decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    submission_no = fields.Char(compute="_get_submission_no", string="Submission No")

    @api.depends('origin')
    def _get_submission_no(self):
    	for res in self:
    		submission_no = ''
    		if res.origin:
    			picking_ids = self.env['stock.picking'].search([('origin','=',res.origin)])
    			if picking_ids:
    				submission_no = picking_ids[0].submission_no
    		res.submission_no = submission_no


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    beacukai_outgoing_line_id = fields.Many2one('beacukai.outgoing.line', 'Outgoing Line')
    beacukai_reference = fields.Char('Nomor Aju')

