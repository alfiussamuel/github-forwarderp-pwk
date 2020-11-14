from odoo import api,fields,models,_
import time
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning
from datetime import datetime, date
from datetime import datetime, timedelta
from dateutil.relativedelta import *
from odoo.tools.safe_eval import safe_eval
import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_compare, float_round
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils
import math
import re    

# import mysql.connector
# from mysql.connector import Error

class ResCompany(models.Model):    
    _inherit = "res.company"

    date_from = fields.Datetime('From')
    date_to = fields.Datetime('To')

    def sql_push_booking(self):
        from_hour = 0
        from_minute = 0
        from_int = 0
        to_hour = 0
        to_minute = 0
        to_int = 0
        start_value = 1597276800

        conn = mysql.connector.connect(host='localhost',
                                       database='mrbs',
                                       user='root',
                                       password='almon011113')
        if conn.is_connected():
            if self.date_from:
                from_int = int(self.date_from.timestamp())            

            if self.date_to:
                to_int = int(self.date_to.timestamp())

            start_time = from_int
            end_time = to_int
            room_id = 3
            name = "Test Lagi"

            query = "INSERT INTO mrbs_entry(start_time,end_time,room_id,name) " \
                "VALUES(%s,%s,%s,%s)"
            args = (start_time, end_time, room_id, name)

            cursor = conn.cursor()
            cursor.execute(query, args)
            conn.commit()

    def sql_push_room(self):    
        conn = mysql.connector.connect(host='localhost',
                                       database='mrbs',
                                       user='root',
                                       password='almon011113')
        if conn.is_connected():
            room_id = 
            area_id = from_int
            room_name = to_int
            sort_key =
            capacity =           

            query = "INSERT INTO mrbs_room(id,area_id,room_name,sort_key,capacity) " \
                "VALUES(%s,%s,%s,%s,%s)"
            args = (room_id, area_id, room_name, sort_key, capacity)

            cursor = conn.cursor()
            cursor.execute(query, args)
            conn.commit()

    def sql_push_area(self):    
        conn = mysql.connector.connect(host='localhost',
                                       database='mrbs',
                                       user='root',
                                       password='almon011113')
        if conn.is_connected():
            area_name = 
            sort_key =
            timezone = "Asia/Jakarta"
            resolution = 1800
            default_duration = 3600
            morningstarts = 7
            morningstarts_minutes = 0
            eveningends = 18
            eveningends_minutes = 30
            max_per_day = 1
            max_per_week = 5
            max_per_month = 10
            max_per_year = 50            

            query = "INSERT INTO mrbs_room(area_name,sort_key,timezone,resolution,default_duration,morningstarts,morningstarts_minutes,eveningends,eveningends_minutes,max_per_day,max_per_week,max_per_month,max_per_year) " \
                "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            args = (area_name,sort_key,timezone,resolution,default_duration,morningstarts,morningstarts_minutes,eveningends,eveningends_minutes,max_per_day,max_per_week,max_per_month,max_per_year)

            cursor = conn.cursor()
            cursor.execute(query, args)
            conn.commit()