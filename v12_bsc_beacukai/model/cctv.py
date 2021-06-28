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
import logging

_logger = logging.getLogger(__name__)


class BeacukaiCctv(models.Model):
    _name = "beacukai.cctv"

    name = fields.Char('Nama')
    desc = fields.Char('Deskripsi')
    url = fields.Char('URL')