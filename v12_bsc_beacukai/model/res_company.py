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

class ResCompany(models.Model):
	_inherit = "res.company"

	company_npwp = fields.Char('NPWP')
	company_permission_no  = fields.Char('Nomor Surat Izin TPB')
	company_permission_date = fields.Date('Tanggal Surat Izin TPB')
	vat = fields.Char(related='partner_id.vat', string="NPWP")