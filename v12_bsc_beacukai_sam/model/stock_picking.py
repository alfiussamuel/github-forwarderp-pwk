from odoo import api, fields, models


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.multi
    def _create_returns(self):
        # TDE FIXME: store it in the wizard, stupid
        picking = self.env['stock.picking'].browse(self.env.context['active_id'])

        return_moves = self.product_return_moves.mapped('move_id')
        unreserve_moves = self.env['stock.move']
        for move in return_moves:
            to_check_moves = self.env['stock.move'] | move.move_dest_id
            while to_check_moves:
                current_move = to_check_moves[-1]
                to_check_moves = to_check_moves[:-1]
                if current_move.state not in ('done', 'cancel') and current_move.reserved_quant_ids:
                    unreserve_moves |= current_move
                split_move_ids = self.env['stock.move'].search([('split_from', '=', current_move.id)])
                to_check_moves |= split_move_ids

        if unreserve_moves:
            unreserve_moves.do_unreserve()
            # break the link between moves in order to be able to fix them later if needed
            unreserve_moves.write({'move_orig_ids': False})

        # create new picking for returned products
        picking_type_id = picking.picking_type_id.return_picking_type_id.id or picking.picking_type_id.id
        new_picking = picking.copy({
            'move_lines': [],
            'picking_type_id': picking_type_id,
            'state': 'draft',
            'origin': picking.name,
            'location_id': picking.location_dest_id.id,
            'location_dest_id': self.location_id.id})
        new_picking.message_post_with_view('mail.message_origin_link',
            values={'self': new_picking, 'origin': picking},
            subtype_id=self.env.ref('mail.mt_note').id)

        returned_lines = 0
        for return_line in self.product_return_moves:
            if not return_line.move_id:
                raise UserError(_("You have manually created product lines, please delete them to proceed"))
            new_qty = return_line.quantity
            if new_qty:
                # The return of a return should be linked with the original's destination move if it was not cancelled
                if return_line.move_id.origin_returned_move_id.move_dest_id.id and return_line.move_id.origin_returned_move_id.move_dest_id.state != 'cancel':
                    move_dest_id = return_line.move_id.origin_returned_move_id.move_dest_id.id
                else:
                    move_dest_id = False

                returned_lines += 1
                return_line.move_id.copy({
                    'product_id': return_line.product_id.id,
                    'product_uom_qty': new_qty,
                    'picking_id': new_picking.id,
                    'state': 'draft',
                    'location_id': return_line.move_id.location_dest_id.id,
                    'location_dest_id': self.location_id.id or return_line.move_id.location_id.id,
                    'picking_type_id': picking_type_id,
                    'warehouse_id': picking.picking_type_id.warehouse_id.id,
                    'origin_returned_move_id': return_line.move_id.id,
                    'procure_method': 'make_to_stock',
                    'move_dest_id': move_dest_id,
                })

        if not returned_lines:
            raise UserError(_("Please specify at least one non-zero quantity."))

        # new_picking.action_confirm()
        # new_picking.action_assign()
        return new_picking.id, picking_type_id

class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    bc_ref_type = fields.Selection([
        ('beacukai.incoming', 'BC IN'),
        ('beacukai.incoming.23', 'BC IN 23'),
        ('beacukai.incoming.27', 'BC IN 27'),
        ('beacukai.incoming.40', 'BC IN 40'),
        ('beacukai.incoming.262', 'BC IN 262'),
        ('beacukai.outgoing', 'BC OUT'),
        ('beacukai.outgoing.25', 'BC OUT 25'),
        ('beacukai.outgoing.27', 'BC OUT 27'),
        ('beacukai.outgoing.30', 'BC OUT 30'),
        ('beacukai.outgoing.41', 'BC OUT 41'),
        ('beacukai.outgoing.261', 'BC OUT 261'),
    ], string='Beacukai Ref Type')
    bc_ref_id = fields.Integer('Referenced Dokumen ID')

    @api.multi
    def get_dokumen(self):
        self.ensure_one()
        dok_model = self.bc_ref_type
        dok = False
        if dok_model in self.env:
            dok = self.env[dok_model].search([('submission_no', '=', self.submission_no)], limit=1)

        return dok if dok else self.beacukai_incoming_23_id or False

    @api.multi
    def bc_action_view_document(self):
        dok = self.get_dokumen()
        action = False
        if dok:
            action = {
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': dok.id,
                'res_model': dok._name,
                'type': 'ir.actions.act_window',
                'target': 'current',
            }
        return action
