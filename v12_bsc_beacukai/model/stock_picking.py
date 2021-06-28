import time
import re
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, except_orm, Warning, RedirectWarning, ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_compare, float_round, float_is_zero

class StockQuant(models.Model):
    _inherit = "stock.quant"

    bc_23_id = fields.Many2one(comodel_name='beacukai.incoming.23', string='Document BC 23')
    submission_no = fields.Char(string='Nomor Pengajuan')

    def _account_entry_move(self, move):
        # print "Account Entry Move"
        """ Accounting Valuation Entries """
        if move.product_id.type != 'product' or move.product_id.valuation != 'real_time':
            # no stock valuation for consumable products
            return False
        if any(quant.owner_id or quant.qty <= 0 for quant in self):
            # if the quant isn't owned by the company, we don't make any valuation en
            # we don't make any stock valuation for negative quants because the valuation is already made for the counterpart.
            # At that time the valuation will be made at the product cost price and afterward there will be new accounting entries
            # to make the adjustments when we know the real cost price.
            return False

        location_from = move.location_id
        location_to = self[0].location_id  # TDE FIXME: as the accounting is based on this value, should probably check all location_to to be the same
        company_from = location_from.usage == 'internal' and location_from.company_id or False
        company_to = location_to and (location_to.usage == 'internal') and location_to.company_id or False

        # Create Journal Entry for products arriving in the company; in case of routes making the link between several
        # warehouse of the same company, the transit location belongs to this company, so we don't need to create accounting entries
        if company_to and (move.location_id.usage not in ('internal', 'transit') and move.location_dest_id.usage == 'internal' or company_from != company_to):
            journal_id, acc_src, acc_dest, acc_valuation = move._get_accounting_data_for_valuation()
            if location_from and location_from.usage == 'customer':  # goods returned from customer
                self.with_context(force_company=company_to.id)._create_account_move_line(move, acc_dest, acc_valuation, journal_id)
            else:
                self.with_context(force_company=company_to.id)._create_account_move_line(move, acc_src, acc_valuation, journal_id)

        # Create Journal Entry for products leaving the company
        if company_from and (move.location_id.usage == 'internal' and move.location_dest_id.usage not in ('internal', 'transit') or company_from != company_to):
            journal_id, acc_src, acc_dest, acc_valuation = move._get_accounting_data_for_valuation()
            if location_to and location_to.usage == 'supplier':  # goods returned to supplier
                self.with_context(force_company=company_from.id)._create_account_move_line(move, acc_valuation, acc_src, journal_id)
            else:
                self.with_context(force_company=company_from.id)._create_account_move_line(move, acc_valuation, acc_dest, journal_id)

        if move.company_id.anglo_saxon_accounting:
            # Creates an account entry from stock_input to stock_output on a dropship move. https://github.com/odoo/odoo/issues/12687
            journal_id, acc_src, acc_dest, acc_valuation = move._get_accounting_data_for_valuation()
            if move.location_id.usage == 'supplier' and move.location_dest_id.usage == 'customer':
                self.with_context(force_company=move.company_id.id)._create_account_move_line(move, acc_src, acc_dest, journal_id)
            if move.location_id.usage == 'customer' and move.location_dest_id.usage == 'supplier':
                self.with_context(force_company=move.company_id.id)._create_account_move_line(move, acc_dest, acc_src, journal_id)

    @api.model
    def _quant_create_from_move(self, qty, move, lot_id=False, owner_id=False,
                                src_package_id=False, dest_package_id=False,
                                force_location_from=False, force_location_to=False):
        '''Create a quant in the destination location and create a negative
        quant in the source location if it's an internal location. '''
        # print "Masuk quant create from move"
        price_unit = move.get_price_unit()
        location = force_location_to or move.location_dest_id
        rounding = move.product_id.uom_id.rounding
        # print "Moveeeeeeeeeeeeeeeeeeeee ", move
        vals = {
            'product_id': move.product_id.id,
            'bc_23_id': move.bc_23_id.id,
            'submission_no': move.submission_no,
            'location_id': location.id,
            'qty': float_round(qty, precision_rounding=rounding),
            'cost': price_unit,
            'history_ids': [(4, move.id)],
            'in_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'company_id': move.company_id.id,
            'lot_id': lot_id,
            'owner_id': owner_id,
            'package_id': dest_package_id,
        }
        if move.location_id.usage == 'internal':
            # if we were trying to move something from an internal location and reach here (quant creation),
            # it means that a negative quant has to be created as well.
            negative_vals = vals.copy()
            negative_vals['location_id'] = force_location_from and force_location_from.id or move.location_id.id
            negative_vals['qty'] = float_round(-qty, precision_rounding=rounding)
            negative_vals['cost'] = price_unit
            negative_vals['negative_move_id'] = move.id
            negative_vals['package_id'] = src_package_id
            negative_quant_id = self.sudo().create(negative_vals)
            vals.update({'propagated_from_id': negative_quant_id.id})

        picking_type = move.picking_id and move.picking_id.picking_type_id or False
        if lot_id and move.product_id.tracking == 'serial' and (not picking_type or (picking_type.use_create_lots or picking_type.use_existing_lots)):
            if qty != 1.0:
                raise UserError(_('You should only receive by the piece with the same serial number'))

        # create the quant as superuser, because we want to restrict the creation of quant manually: we should always use this method to create quants
        quant = self.sudo().create(vals)
        # print "Quant ", quant_id
        # print "Quant BC 23 ID ", quant_id.bc_23_id
        # print "Quant Submission No ", quant_id.submission_no

        quant._account_entry_move(move)
        if move.product_id.valuation == 'real_time':
            # If the precision required for the variable quant cost is larger than the accounting
            # precision, inconsistencies between the stock valuation and the accounting entries
            # may arise.
            # For example, a box of 13 units is bought 15.00. If the products leave the
            # stock one unit at a time, the amount related to the cost will correspond to
            # round(15/13, 2)*13 = 14.95. To avoid this case, we split the quant in 12 + 1, then
            # record the difference on the new quant.
            # We need to make sure to able to extract at least one unit of the product. There is
            # an arbitrary minimum quantity set to 2.0 from which we consider we can extract a
            # unit and adapt the cost.
            curr_rounding = move.company_id.currency_id.rounding
            cost_rounded = float_round(quant.cost, precision_rounding=curr_rounding)
            cost_correct = cost_rounded
            if float_compare(quant.product_id.uom_id.rounding, 1.0, precision_digits=1) == 0\
                    and float_compare(quant.qty * quant.cost, quant.qty * cost_rounded, precision_rounding=curr_rounding) != 0\
                    and float_compare(quant.qty, 2.0, precision_rounding=quant.product_id.uom_id.rounding) >= 0:
                quant_correct = quant._quant_split(quant.qty - 1.0)
                cost_correct += (quant.qty * quant.cost) - (quant.qty * cost_rounded)
                quant.sudo().write({'cost': cost_rounded})
                quant_correct.sudo().write({'cost': cost_correct})

        return quant

    # def _quant_create_from_move(self, qty, move, lot_id=False, owner_id=False, src_package_id=False, dest_package_id=False, force_location_from=False, force_location_to=False):
    #     print "Masukkkkkkkkk quant create from move"
    #     quant = super(StockQuant, self)._quant_create_from_move(qty, move, lot_id=lot_id, owner_id=owner_id, src_package_id=src_package_id, dest_package_id=dest_package_id, force_location_from=force_location_from, force_location_to=force_location_to)
    #     quant._account_entry_move(move)
    #     if move.product_id.valuation == 'real_time':
    #         # If the precision required for the variable quant cost is larger than the accounting
    #         # precision, inconsistencies between the stock valuation and the accounting entries
    #         # may arise.
    #         # For example, a box of 13 units is bought 15.00. If the products leave the
    #         # stock one unit at a time, the amount related to the cost will correspond to
    #         # round(15/13, 2)*13 = 14.95. To avoid this case, we split the quant in 12 + 1, then
    #         # record the difference on the new quant.
    #         # We need to make sure to able to extract at least one unit of the product. There is
    #         # an arbitrary minimum quantity set to 2.0 from which we consider we can extract a
    #         # unit and adapt the cost.
    #         curr_rounding = move.company_id.currency_id.rounding
    #         cost_rounded = float_round(quant.cost, precision_rounding=curr_rounding)
    #         cost_correct = cost_rounded
    #         if float_compare(quant.product_id.uom_id.rounding, 1.0, precision_digits=1) == 0\
    #                 and float_compare(quant.qty * quant.cost, quant.qty * cost_rounded, precision_rounding=curr_rounding) != 0\
    #                 and float_compare(quant.qty, 2.0, precision_rounding=quant.product_id.uom_id.rounding) >= 0:
    #             quant_correct = quant._quant_split(quant.qty - 1.0)
    #             cost_correct += (quant.qty * quant.cost) - (quant.qty * cost_rounded)
    #             quant.sudo().write({'cost': cost_rounded})
    #             quant_correct.sudo().write({'cost': cost_correct})
    #     return quant

    def _quant_update_from_move(self, move, location_dest_id, dest_package_id, lot_id=False, entire_pack=False):
        # print "Masukkkkkkkkk quant update from move"
        res = super(StockQuant, self)._quant_update_from_move(move, location_dest_id, dest_package_id, lot_id=lot_id, entire_pack=entire_pack)
        self._account_entry_move(move)
        return res

    @api.model
    def quants_move(self, quants, move, location_to, location_from=False, lot_id=False, owner_id=False, src_package_id=False, dest_package_id=False, entire_pack=False):
        # print "Masukk quants move"
        """Moves all given stock.quant in the given destination location.  Unreserve from current move.
        :param quants: list of tuple(browse record(stock.quant) or None, quantity to move)
        :param move: browse record (stock.move)
        :param location_to: browse record (stock.location) depicting where the quants have to be moved
        :param location_from: optional browse record (stock.location) explaining where the quant has to be taken
                              (may differ from the move source location in case a removal strategy applied).
                              This parameter is only used to pass to _quant_create_from_move if a negative quant must be created
        :param lot_id: ID of the lot that must be set on the quants to move
        :param owner_id: ID of the partner that must own the quants to move
        :param src_package_id: ID of the package that contains the quants to move
        :param dest_package_id: ID of the package that must be set on the moved quant
        """
        # TDE CLEANME: use ids + quantities dict
        if location_to.usage == 'view':
            raise UserError(_('You cannot move to a location of type view %s.') % (location_to.name))

        quants_reconcile_sudo = self.env['stock.quant'].sudo()
        quants_move_sudo = self.env['stock.quant'].sudo()
        check_lot = False
        for quant, qty in quants:
            # print "AAAAAAAAAAAAAAAA"
            if not quant:
                # print "BBBBBBBBBBBBBBBB"
                #If quant is None, we will create a quant to move (and potentially a negative counterpart too)
                quant = self._quant_create_from_move(
                    qty, move, lot_id=lot_id, owner_id=owner_id, src_package_id=src_package_id, dest_package_id=dest_package_id, force_location_from=location_from, force_location_to=location_to)
                check_lot = True
            else:
                # print "CCCCCCCCCCCCCCCCCCCC"
                quant._quant_split(qty)
                quants_move_sudo |= quant
            quants_reconcile_sudo |= quant

        if quants_move_sudo:
            # print "DDDDDDDDDDDDDDDDDD"
            moves_recompute = quants_move_sudo.filtered(lambda self: self.reservation_id != move).mapped('reservation_id')
            quants_move_sudo._quant_update_from_move(move, location_to, dest_package_id, lot_id=lot_id, entire_pack=entire_pack)
            moves_recompute.recalculate_move_state()

        if location_to.usage == 'internal':
            # Do manual search for quant to avoid full table scan (order by id)
            self._cr.execute("""
                SELECT 0 FROM stock_quant, stock_location WHERE product_id = %s AND stock_location.id = stock_quant.location_id AND
                ((stock_location.parent_left >= %s AND stock_location.parent_left < %s) OR stock_location.id = %s) AND qty < 0.0 LIMIT 1
            """, (move.product_id.id, location_to.parent_left, location_to.parent_right, location_to.id))
            if self._cr.fetchone():
                quants_reconcile_sudo._quant_reconcile_negative(move)

        # In case of serial tracking, check if the product does not exist somewhere internally already
        # Checking that a positive quant already exists in an internal location is too restrictive.
        # Indeed, if a warehouse is configured with several steps (e.g. "Pick + Pack + Ship") and
        # one step is forced (creates a quant of qty = -1.0), it is not possible afterwards to
        # correct the inventory unless the product leaves the stock.
        picking_type = move.picking_id and move.picking_id.picking_type_id or False
        if check_lot and lot_id and move.product_id.tracking == 'serial' and (not picking_type or (picking_type.use_create_lots or picking_type.use_existing_lots)):
            other_quants = self.search([('product_id', '=', move.product_id.id), ('lot_id', '=', lot_id),
                                        ('qty', '>', 0.0), ('location_id.usage', '=', 'internal')])
            if other_quants:
                # We raise an error if:
                # - the total quantity is strictly larger than 1.0
                # - there are more than one negative quant, to avoid situations where the user would
                #   force the quantity at several steps of the process
                if sum(other_quants.mapped('qty')) > 1.0 or len([q for q in other_quants.mapped('qty') if q < 0]) > 1:
                    lot_name = self.env['stock.production.lot'].browse(lot_id).name
                    raise UserError(_('The serial number %s is already in stock.') % lot_name + _("Otherwise make sure the right stock/owner is set."))

class StockPicking(models.Model):
    _inherit = "stock.picking"

    location_id = fields.Many2one(
        'stock.location', "Source Location Zone",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_src_id,
        readonly=False, required=True,
        states={'draft': [('readonly', False)]})
    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location Zone",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_dest_id,
        readonly=False, required=True,
        states={'draft': [('readonly', False)]})
    min_date = fields.Datetime(
        'Scheduled Date', 
        required = False, 
        compute='_compute_dates', 
        inverse='_set_min_date', 
        store=True, 
        index=True,
        copy=True,
        track_visibility='onchange',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Scheduled time for the first part of the shipment to be processed. Setting manually a value here would set it as expected date for all the stock moves.")

    is_beacukai_incoming = fields.Boolean('BC Incoming')
    is_beacukai_outgoing = fields.Boolean('BC Outgoing')
    beacukai_incoming_id = fields.Many2one(
        'beacukai.incoming', 'BC Incoming Doc')
    beacukai_outgoing_id = fields.Many2one(
        'beacukai.outgoing', 'BC Outgoing Doc')

    is_beacukai_incoming_23 = fields.Boolean('BC Incoming 23')
    beacukai_incoming_23_id = fields.Many2one(
        'beacukai.incoming.23', 'BC Incoming 23 Doc')
    mrp_production_id = fields.Many2one(
        'mrp.production', string='MO Document', help="Manufacturing Order Document")
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Picking Type',
        required=True, readonly=False,
        default=lambda self: self.env.user.default_picking_type.id,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    submission_no = fields.Char('No Aju', readonly=True)

    @api.one
    @api.depends('move_lines.date_expected')
    def _compute_dates(self):
        self.min_date = min(self.move_lines.mapped('date_expected') or [False])
        self.max_date = max(self.move_lines.mapped('date_expected') or [False])

    @api.one
    def _set_min_date(self):
        self.move_lines.write({'date_expected': self.min_date})

    def is_authorized(self, picking_type_id):
        if self.env.user.has_group('stock.group_stock_manager'):
            return True
        elif not self.env.user.default_picking_type:
            return False
        else:
            default_picking_type_id = self.env.user.default_picking_type.id
            return default_picking_type_id == picking_type_id

    @api.multi
    def write(self, vals):
        res = super(StockPicking, self).write(vals)
        for rec in self:
            if not rec.is_authorized(rec.picking_type_id.id) and rec.state == 'draft':
                group_stock_manager = self.env.ref('stock.group_stock_manager')
                recipient_ids = [x.email for x in group_stock_manager.users]
                template = self.env.ref('v10_bsc_beacukai.email_template_warehouse')
                template.send_mail(rec.id, force_send=True,
                                   email_values={'email_to': ','.join(recipient_ids)})

        return res

    @api.model
    def create(self, values):
        get_mrp_production = values.get('mrp_production_id')
        get_min_date = values.get('min_date')
        mrp_product = self.env['mrp.production'].browse(get_mrp_production)
        if mrp_product:
            values['move_lines'] = []

            for move in mrp_product.move_raw_ids:
                value = {
                    'product_id': move.product_id.id,
                    'product_uom_qty': move.product_uom_qty,
                    'state': 'draft',
                    'product_uom': move.product_uom.id,
                    'name': move.product_id.name,
                    'date_expected': get_min_date
                }
                values['move_lines'].append((0, 0, value))

        res = super(StockPicking, self).create(values)
        if not self.is_authorized(res.picking_type_id.id) and self.state == 'draft':
            template = self.env.ref('v10_bsc_beacukai.email_template_warehouse')
            template.send_mail(res.id, force_send=True)

        return res

    @api.onchange('mrp_production_id')
    def onchange_mrp_production_id(self):
        # for res in self:
        #     if res.mrp_production_id.move_raw_ids:
                
        res = self.search([('mrp_production_id', '=', self.mrp_production_id.id),
                           ('mrp_production_id', '!=', False),
                           ('id', '!=', self._origin.id)])
        if res:
            names = [x.name for x in res]
            raise Warning(
                'Transfer for %s\'s components already created in the following: \n%s'
                % (self.mrp_production_id.name, ',\n'.join(names)))

    @api.multi
    def button_bc_incoming(self):
        ir_model_data = self.env['ir.model.data']
        compose_form_id = ir_model_data.get_object_reference(
            'v10_bsc_beacukai', 'create_bc_incoming_wizard')[1]
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'create.bc.incoming.wizard',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': {
                    'default_picking_id': self.id,
            }
        }

    @api.onchange('beacukai_incoming_id')
    def onchange_beacukai_incoming_id(self):
        detail_lines = [(5, 0, 0)]

        for each in self.beacukai_incoming_id.line_ids:
            pick_id = self.search([('name', '=', self.name)])
            vals = {
                'picking_id': pick_id.id,
                'product_id': each.product_id.id,
                'product_uom_qty': each.product_qty,
                'product_uom': each.product_uom_id.id,
                'uom_id': each.product_uom_id.id,
                'state': 'draft',
                'name': each.product_id.name,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'date_expected': self.min_date,
                'picking_type_id': self.picking_type_id.id,
            }
            move_id = self.env['stock.move'].create(vals)
        #     detail_lines.append((0,0,vals))
        # print ">>>>>>>>>>><<<<<<<<", detail_lines
        # self.move_lines = detail_lines

    @api.onchange('beacukai_incoming_23_id')
    def onchange_beacukai_incoming_23_id(self):
        detail_lines = [(5, 0, 0)]

        for each in self.beacukai_incoming_23_id.line_ids:
            pick_id = self.search([('name', '=', self.name)])
            vals = {
                'picking_id': pick_id.id,
                'product_id': each.product_id.id,
                'product_uom_qty': each.product_qty,
                'product_uom': each.product_uom_id.id,
                'uom_id': each.product_uom_id.id,
                'state': 'draft',
                'name': each.product_id.name,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'date_expected': self.min_date,
                'picking_type_id': self.picking_type_id.id,
            }
            move_id = self.env['stock.move'].create(vals)

    @api.onchange('beacukai_outgoing_id')
    def onchange_beacukai_outgoing_id(self):
        detail_lines = [(5, 0, 0)]

        for each in self.beacukai_outgoing_id.line_ids:
            pick_id = self.search([('name', '=', self.name)])
            vals = {
                'picking_id': pick_id.id,
                'product_id': each.product_id.id,
                'product_uom_qty': each.product_qty,
                'product_uom': each.product_uom_id.id,
                'uom_id': each.product_uom_id.id,
                'state': 'draft',
                'name': each.product_id.name,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'date_expected': self.min_date,
                'picking_type_id': self.picking_type_id.id,
            }
            move_id = self.env['stock.move'].create(vals)

    @api.multi
    def do_new_transfer(self):
        for rec in self:
            if self.is_authorized(rec.picking_type_id.id):
                return super(StockPicking, self).do_new_transfer()
            else:
                raise ValidationError(
                    'Only inventory manager are allowed create transfer outside of user\'s default inventory type')

    @api.multi
    def bc_action_view_document(self):
        dok = self.env['beacukai.incoming.40'].search([('submission_no', '=', self.submission_no)], limit=1)
        action = {
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': dok.id,
            'res_model': 'beacukai.incoming.40',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
        return action if dok else False


class StockMove(models.Model):
    _inherit = 'stock.move'

    uom_id = fields.Many2one('product.uom', 'UoM', related="product_id.uom_id")

    bc_incoming_line_id = fields.Many2one('beacukai.incoming.line',
                                          'Bea Cukai Incoming Line', ondelete='set null', index=True, readonly=True)
    bc_incoming_line_23_id = fields.Many2one('beacukai.incoming.line.23',
                                             'Bea Cukai Incoming Line 23', ondelete='set null', index=True, readonly=True)

    laporan_posisi_wip_id = fields.Many2one('laporan.posisi.wip',
                                            'Laporan Posisi WIP', ondelete='set null', index=True, readonly=True, compute="_get_laporan_posisi_wip_id")

    bc_outgoing_line_id = fields.Many2one('beacukai.outgoing.line',
                                          'Bea Cukai Outgoing Line', ondelete='set null', index=True, readonly=True)

    product_code = fields.Char('Kode Barang', related="product_id.name")
    hs_code = fields.Char('HS Code', related="product_id.hs_code")
    product_amount = fields.Float(
        'Harga', related="bc_outgoing_line_id.product_amount")

    document_type_id = fields.Many2one(
        'beacukai.document.type', 'Tipe Dokumen', related="picking_id.beacukai_incoming_id.document_type_id")
    submission_no = fields.Char('No Aju')
    submission_no_mrp = fields.Char(compute="_get_submission_no_mrp", string='No Aju MRP')
    register_number = fields.Char(
        'No.Pendaftaran', related="picking_id.beacukai_incoming_id.register_number")
    register_date = fields.Date(
        'Tanggal Pendaftaran', related="picking_id.beacukai_incoming_id.register_date")

    document_type_23_id = fields.Many2one(
        'beacukai.document.type', 'Tipe Dokumen', related="picking_id.beacukai_incoming_23_id.document_type_id")
    submission_no_23 = fields.Char(
        'No Aju', related="picking_id.beacukai_incoming_23_id.submission_no")
    register_number_23 = fields.Char(
        'No.Pendaftaran', related="picking_id.beacukai_incoming_23_id.register_number")
    register_date_23 = fields.Date(
        'Tanggal Pendaftaran', related="picking_id.beacukai_incoming_23_id.register_date")

    document_type_id_outgoing = fields.Many2one(
        'beacukai.document.type', 'Tipe Dokumen', related="picking_id.beacukai_outgoing_id.document_type_id")
    submission_no_outgoing = fields.Char(
        'No Aju', related="picking_id.beacukai_outgoing_id.submission_no")
    register_number_outgoing = fields.Char(
        'No.Pendaftaran', related="picking_id.beacukai_outgoing_id.register_number")
    register_date_outgoing = fields.Date(
        'Tanggal Pendaftaran', related="picking_id.beacukai_outgoing_id.register_date")

    company_npwp = fields.Char(
        'NPWP', default=lambda self: self.env.user.company_id.vat, readonly=True)
    company_name = fields.Char(
        'Nama Perusahaan', default=lambda self: self.env.user.company_id.name, readonly=True)
    company_address = fields.Text(
        'Alamat Perusahaan', default=lambda self: self.env.user.company_id.street, readonly=True)
    company_permission_no = fields.Char(
        'Nomor Surat Izin TPB', readonly=True, default=lambda self: self.env['ir.config_parameter'].get_param('no_tpb'))
    company_permission_date = fields.Date(
        'Tanggal Surat Izin TPB', readonly=True, default=lambda self: self.env['ir.config_parameter'].get_param('tgl_tpb'))

    subcontract_company_npwp = fields.Char('NPWP Subkontrak')
    subcontract_company_name = fields.Char('Nama Perusahaan Subkontrak')
    subcontract_company_address = fields.Text('Alamat Perusahaan Subkontrak')

    contract_number = fields.Char('Nomor Kontrak')

    hs_code = fields.Char(
        'HS Code', related="product_id.product_tmpl_id.hs_code")
    product_qty = fields.Float('Qty')

    is_change = fields.Boolean('Changed')

    @api.depends('quant_ids','is_change')
    def _get_submission_no_mrp(self):        
        for res in self:
            submission_nos = []
            if res.quant_ids:
                for quant in res.quant_ids:
                    if quant.submission_no and quant.submission_no not in submission_nos:
                        submission_nos.append(quant.submission_no)
            res.submission_no_mrp = ','.join(submission_nos)

    @api.multi
    def _get_laporan_posisi_wip_id(self):
        for res in self:
            lap_posisi_wip_id = self.env['laporan.posisi.wip'].search([
                ('reference', '=', res.picking_id.beacukai_incoming_id.id),
                ('product_id', '=',res.product_id.id),
                ('picking_id', '=', res.picking_id.id)])

            for each in lap_posisi_wip_id:
                res.laporan_posisi_wip_id = each.id

    @api.multi
    def action_done(self):
        # print "Masuk action done"
        
        # Additional
        self.product_price_update_before_done()

        """ Process completely the moves given and if all moves are done, it will finish the picking. """
        self.filtered(lambda move: move.state == 'draft').action_confirm()

        Uom = self.env['product.uom']
        Quant = self.env['stock.quant']

        pickings = self.env['stock.picking']
        procurements = self.env['procurement.order']
        operations = self.env['stock.move']

        remaining_move_qty = {}

        for move in self:
            if move.picking_id:
                pickings |= move.picking_id
            remaining_move_qty[move.id] = move.product_qty
            for link in move.linked_move_operation_ids:
                operations |= link.operation_id
                pickings |= link.operation_id.picking_id

        # Sort operations according to entire packages first, then package + lot, package only, lot only
        operations = operations.sorted(key=lambda x: ((x.package_id and not x.product_id) and -4 or 0) + (x.package_id and -2 or 0) + (x.pack_lot_ids and -1 or 0))

        for operation in operations:

            # product given: result put immediately in the result package (if False: without package)
            # but if pack moved entirely, quants should not be written anything for the destination package
            quant_dest_package_id = operation.product_id and operation.result_package_id.id or False
            entire_pack = not operation.product_id and True or False

            # compute quantities for each lot + check quantities match
            lot_quantities = dict((pack_lot.lot_id.id, operation.product_uom_id._compute_quantity(pack_lot.qty, operation.product_id.uom_id)
            ) for pack_lot in operation.pack_lot_ids)

            qty = operation.product_qty
            if operation.product_uom_id and operation.product_uom_id != operation.product_id.uom_id:
                qty = operation.product_uom_id._compute_quantity(qty, operation.product_id.uom_id)
            if operation.pack_lot_ids and float_compare(sum(lot_quantities.values()), qty, precision_rounding=operation.product_id.uom_id.rounding) != 0.0:
                raise UserError(_('You have a difference between the quantity on the operation and the quantities specified for the lots. '))

            quants_taken = []
            false_quants = []
            lot_move_qty = {}

            prout_move_qty = {}
            for link in operation.linked_move_operation_ids:
                prout_move_qty[link.move_id] = prout_move_qty.get(link.move_id, 0.0) + link.qty

            # Process every move only once for every pack operation
            for move in prout_move_qty.keys():
                # TDE FIXME: do in batch ?
                move.check_tracking(operation)

                # TDE FIXME: I bet the message error is wrong
                if not remaining_move_qty.get(move.id):
                    raise UserError(_("The roundings of your unit of measure %s on the move vs. %s on the product don't allow to do these operations or you are not transferring the picking at once. ") % (move.product_uom.name, move.product_id.uom_id.name))

                if not operation.pack_lot_ids:
                    # print "Masuk if not operation pack lot ids"
                    preferred_domain_list = [[('reservation_id', '=', move.id)], [('reservation_id', '=', False)], ['&', ('reservation_id', '!=', move.id), ('reservation_id', '!=', False)]]
                    quants = Quant.quants_get_preferred_domain(
                        prout_move_qty[move], move, ops=operation, domain=[('qty', '>', 0)],
                        preferred_domain_list=preferred_domain_list)
                    Quant.quants_move(quants, move, operation.location_dest_id, location_from=operation.location_id,
                                      lot_id=False, owner_id=operation.owner_id.id, src_package_id=operation.package_id.id,
                                      dest_package_id=quant_dest_package_id, entire_pack=entire_pack)
                else:
                    # Check what you can do with reserved quants already
                    qty_on_link = prout_move_qty[move]
                    rounding = operation.product_id.uom_id.rounding
                    for reserved_quant in move.reserved_quant_ids:
                        if (reserved_quant.owner_id.id != operation.owner_id.id) or (reserved_quant.location_id.id != operation.location_id.id) or \
                                (reserved_quant.package_id.id != operation.package_id.id):
                            continue
                        if not reserved_quant.lot_id:
                            false_quants += [reserved_quant]
                        elif float_compare(lot_quantities.get(reserved_quant.lot_id.id, 0), 0, precision_rounding=rounding) > 0:
                            if float_compare(lot_quantities[reserved_quant.lot_id.id], reserved_quant.qty, precision_rounding=rounding) >= 0:
                                qty_taken = min(reserved_quant.qty, qty_on_link)
                                lot_quantities[reserved_quant.lot_id.id] -= qty_taken
                                quants_taken += [(reserved_quant, qty_taken)]
                                qty_on_link -= qty_taken
                            else:
                                qty_taken = min(qty_on_link, lot_quantities[reserved_quant.lot_id.id])
                                quants_taken += [(reserved_quant, qty_taken)]
                                lot_quantities[reserved_quant.lot_id.id] -= qty_taken
                                qty_on_link -= qty_taken
                    lot_move_qty[move.id] = qty_on_link

                remaining_move_qty[move.id] -= prout_move_qty[move]

            # Handle lots separately
            if operation.pack_lot_ids:
                # TDE FIXME: fix call to move_quants_by_lot to ease understanding
                self._move_quants_by_lot(operation, lot_quantities, quants_taken, false_quants, lot_move_qty, quant_dest_package_id)

            # Handle pack in pack
            if not operation.product_id and operation.package_id and operation.result_package_id.id != operation.package_id.parent_id.id:
                operation.package_id.sudo().write({'parent_id': operation.result_package_id.id})

        # Check for remaining qtys and unreserve/check move_dest_id in
        move_dest_ids = set()
        for move in self:
            if float_compare(remaining_move_qty[move.id], 0, precision_rounding=move.product_id.uom_id.rounding) > 0:  # In case no pack operations in picking
                move.check_tracking(False)  # TDE: do in batch ? redone ? check this

                preferred_domain_list = [[('reservation_id', '=', move.id)], [('reservation_id', '=', False)], ['&', ('reservation_id', '!=', move.id), ('reservation_id', '!=', False)]]
                quants = Quant.quants_get_preferred_domain(
                    remaining_move_qty[move.id], move, domain=[('qty', '>', 0)],
                    preferred_domain_list=preferred_domain_list)
                Quant.quants_move(
                    quants, move, move.location_dest_id,
                    lot_id=move.restrict_lot_id.id, owner_id=move.restrict_partner_id.id)

            # If the move has a destination, add it to the list to reserve
            if move.move_dest_id and move.move_dest_id.state in ('waiting', 'confirmed'):
                move_dest_ids.add(move.move_dest_id.id)

            if move.procurement_id:
                procurements |= move.procurement_id

            # unreserve the quants and make them available for other operations/moves
            move.quants_unreserve()

        # Check the packages have been placed in the correct locations
        self.mapped('quant_ids').filtered(lambda quant: quant.package_id and quant.qty > 0).mapped('package_id')._check_location_constraint()

        # set the move as done
        self.write({'state': 'done', 'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        procurements.check()
        # assign destination moves
        if move_dest_ids:
            # TDE FIXME: record setise me
            self.browse(list(move_dest_ids)).action_assign()

        pickings.filtered(lambda picking: picking.state == 'done' and not picking.date_done).write({'date_done': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})

        # Additional
        self.product_price_update_after_done()

        return True