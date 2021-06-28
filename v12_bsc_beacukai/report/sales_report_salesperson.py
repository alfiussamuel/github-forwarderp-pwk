# -*- coding: utf-8 -*-

import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError


class ReportSalesperson(models.AbstractModel):
    _name = 'report.v12_bsc_beacukai.report_salesperson'

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        bc_type = self.env['ir.config_parameter'].get_param('bc_type')
        docs.bc_type = ""
        if bc_type == 0:
            docs.bc_type = "Kawasan Berikat"
        else:
            docs.bc_type = "Gudang Berikat"
        sales_records = []
        orders = self.env['beacukai.incoming.line'].search([])
        if docs.date_from and docs.date_to:
            for order in orders:
                if docs.date_from <= order.date and docs.date_to >= order.date:
                    sales_records.append(order)
        else:
            raise UserError("Please enter duration")

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'orders': sales_records,
            'header': self.env['beacukai.apiu'].search([], limit=1)
        }
        return self.env['report'].render('v12_bsc_beacukai.report_salesperson', docargs)


class ReportBc23(models.AbstractModel):
    _name = 'report.v12_bsc_beacukai.report_bc23'

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        bc_type = self.env['ir.config_parameter'].get_param('bc_type')
        docs.bc_type = ""
        if bc_type == 0:
            docs.bc_type = "Kawasan Berikat"
        else:
            docs.bc_type = "Gudang Berikat"
        sales_records = []
        orders_23 = self.env['beacukai.incoming.line.23'].search([])
        orders_262 = self.env['beacukai.incoming.line.262'].search([])
        orders_27 = self.env['beacukai.incoming.line.27'].search([])
        orders_40 = self.env['beacukai.incoming.line.40'].search([])
        orders_30 = self.env['beacukai.incoming.line.30'].search([])

        if docs.date_from and docs.date_to:
            for order_23 in orders_23:
                if docs.date_from <= order_23.date_aju_line and docs.date_to >= order_23.date_aju_line:
                    sales_records.append(order_23)
            for order_262 in orders_262:
                if docs.date_from <= order_262.date_aju_line and docs.date_to >= order_262.date_aju_line:
                    sales_records.append(order_262)
            for order_27 in orders_27:
                if docs.date_from <= order_27.date_aju_line and docs.date_to >= order_27.date_aju_line:
                    sales_records.append(order_27)
            for order_40 in orders_40:
                if docs.date_from <= order_40.date_aju_line and docs.date_to >= order_40.date_aju_line:
                    sales_records.append(order_40)
            for order_30 in orders_30:
                if docs.date_from <= order_30.date_aju_line and docs.date_to >= order_30.date_aju_line:
                    sales_records.append(order_30)
        else:
            raise UserError("Please enter duration")

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'orders': sales_records,
            'header': self.env['beacukai.apiu'].search([], limit=1)
        }
        return self.env['report'].render('v12_bsc_beacukai.report_bc23', docargs)


class ReportBcOutgoing(models.AbstractModel):
    _name = 'report.v12_bsc_beacukai.bc_report_outgoing'

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        bc_type = self.env['ir.config_parameter'].get_param('bc_type')
        docs.bc_type = ""
        if bc_type == 0:
            docs.bc_type = "Kawasan Berikat"
        else:
            docs.bc_type = "Gudang Berikat"

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'orders': data['orders'],
            'header': self.env['beacukai.apiu'].search([], limit=1)
        }
        return self.env['report'].render('v12_bsc_beacukai.bc_report_outgoing', docargs)

class ReportBcIncoming(models.AbstractModel):
    _name = 'report.v12_bsc_beacukai.bc_report_incoming'

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        bc_type = self.env['ir.config_parameter'].get_param('bc_type')
        docs.bc_type = ""
        if bc_type == 0:
            docs.bc_type = "Kawasan Berikat"
        else:
            docs.bc_type = "Gudang Berikat"

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'orders': data['orders'],
            'header': self.env['beacukai.apiu'].search([], limit=1)
        }

        return self.env['report'].render('v12_bsc_beacukai.bc_report_incoming', docargs)


class ReportBcWip(models.AbstractModel):
    _name = 'report.v12_bsc_beacukai.bc_report_wip'

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        bc_type = self.env['ir.config_parameter'].get_param('bc_type')
        docs.bc_type = ""
        if bc_type == 0:
            docs.bc_type = "Kawasan Berikat"
        else:
            docs.bc_type = "Gudang Berikat"

        loc = self.env['ir.config_parameter'].sudo().get_param('location_wip')
        move_line_ids = self.env['stock.move'].search([
            ('date', '>=', docs.date_from),
            ('date', '<=', docs.date_to),
            ('state', '=', 'done'),
            ('location_dest_id', '=', int(loc))
        ])


        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'moves': move_line_ids,
            'header': self.env['beacukai.apiu'].search([], limit=1)
        }
        return self.env['report'].render('v12_bsc_beacukai.bc_report_wip', docargs)


class ReportBcPosisi(models.AbstractModel):
    _name = 'report.v12_bsc_beacukai.bc_report_posisi'

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        sales_records = []
        orders = self.env['product.template'].search(
            [('categ_id.name', '=', docs.category)])
        # if docs.date_from and docs.date_to:
        #     for order in orders:
        #         if docs.date_from <= order.date and docs.date_to >= order.date:
        #             sales_records.append(order);
        # else:
        #     raise UserError("Please enter duration")

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'orders': orders,
            'header': self.env['beacukai.apiu'].search([], limit=1)
        }
        return self.env['report'].render('v12_bsc_beacukai.bc_report_posisi', docargs)
