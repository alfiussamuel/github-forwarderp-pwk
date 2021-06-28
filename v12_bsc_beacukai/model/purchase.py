from odoo import api, fields, models


class Purchase(models.Model):
    _inherit = "purchase.order"

    is_bc = fields.Boolean('Beacukai?')
    bc_incoming = fields.One2many('beacukai.incoming', 'po_id', string="Dokumen Beacukai")

    # @api.constrains('submission_no')
    # def _check_submission_no(self):
    #     if not self.submission_no:
    #         return
    #     if ' ' == self.submission_no[-1:]:
    #         self.submission_no = self.submission_no.strip()
    #         return
    #
    #     valid = '0123456789'
    #     for c in self.submission_no:
    #         if c not in valid:
    #             raise UserError("Nomor Pengajuan hanya bisa berupa digit")


    @api.multi
    def _create_picking(self):
        if not self.is_bc:
            StockPicking = self.env['stock.picking']
            for order in self:
                if any([ptype in ['product', 'consu'] for ptype in order.order_line.mapped('product_id.type')]):
                    pickings = order.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                    if not pickings:
                        res = order._prepare_picking()
                        picking = StockPicking.create(res)
                    else:
                        picking = pickings[0]
                    moves = order.order_line._create_stock_moves(picking)
                    moves = moves.filtered(lambda x: x.state not in ('done', 'cancel')).action_confirm()
                    seq = 0
                    for move in sorted(moves, key=lambda move: move.date_expected):
                        seq += 5
                        move.sequence = seq
                    moves.force_assign()
                    picking.message_post_with_view('mail.message_origin_link',
                                                   values={'self': picking, 'origin': order},
                                                   subtype_id=self.env.ref('mail.mt_note').id)
        return True
