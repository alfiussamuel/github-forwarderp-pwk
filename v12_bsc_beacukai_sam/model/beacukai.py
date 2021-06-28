from odoo import api, fields, models
from odoo.exceptions import UserError


class BcOutgoingRegisterNumber(models.TransientModel):
    _inherit = 'bc.outgoing.register.number'

    document_id = fields.Integer('Referenced Document ID')
    ref_model = fields.Char('Referenced Model')
    po_id = fields.Many2one('purchase.order', 'Purchase Order', domain="[('state','=','purchase')]")
    so_id = fields.Many2one('sale.order', 'Sale Order', domain="[('state','=','sale')]")

    @api.multi
    def input_registrasi(self):
        # Override v10_bsc_beacukai.bc.outgoing.register.number input_registrasi
        is_incoming = self.env.context.get('is_incoming', False)
        is_outgoing = self.env.context.get('is_outgoing', False)
        val = {
            'register_number': self.register_number,
            'register_date': self.register_date,
            'state': 'registrasi',
            'po_id': self.po_id.id,
            'line_ids': []
        }
        dokumen = None
        order = False
        linked_dok = False

        if is_incoming:
            order = self.po_id
            val['is_from_po'] = True if order else False
        elif is_outgoing:
            order = self.so_id
            val['is_from_so'] = True if order else False

        if self.outgoing_id:
            dokumen = self.outgoing_id
        elif self.document_id and self.ref_model in self.env:
            dokumen = self.env[self.ref_model].search([('id', '=', self.document_id)])

        if order:
            dokumen.line_ids.unlink()

            # if order.bc_ref_type in self.env:
            #     linked_dok = self.env[order.bc_ref_type].search([('id', '=', order.bc_ref_id)])
            #     if linked_dok:
            #         dok_name = dict(order._fields['bc_ref_type'].selection).get(order.bc_ref_type)
            #         raise UserError("%s telah digunakan untuk %s , silakan pilih dokumen lain" % (order.name, dok_name, ))

            order.bc_ref_type = self.ref_model
            order.bc_ref_id = dokumen.id

            for picking_id in order.picking_ids:
                picking_id.submission_no = dokumen.submission_no
                picking_id.bc_ref_type = self.ref_model
                picking_id.bc_ref_id = dokumen.id

            for order_line in order.order_line:
                if is_incoming:
                    val['line_ids'].append((0,0, {
                        'product_id': order_line.product_id.id,
                        'product_categ_id': order_line.product_id.categ_id.id,
                        'product_qty': order_line.product_qty,
                        'product_incost': order_line.price_unit,
                        'product_uom_id': order_line.product_uom.id,
                        'product_netto': order_line.price_unit,
                        'order_id': order.id,
                        'order_line_id': order_line.id
                    }))
                elif is_outgoing:
                    val['line_ids'].append((0,0, {
                        'product_id': order_line.product_id.id,
                        'product_categ_id': order_line.product_id.categ_id.id,
                        'product_qty': order_line.product_uom_qty,
                        'product_incost': order_line.price_unit,
                        'product_uom_id': order_line.product_uom.id,
                        'product_netto': order_line.price_unit,
                        'order_id': order.id,
                        'order_line_id': order_line.id
                    }))

            val['so_id'] = order.id

        dokumen.write(val)
        return True


class BeacukaiIncomingLine23(models.Model):
    _inherit = "beacukai.incoming.line.23"

    product_type = fields.Char('Tipe', related='product_id.product_type', readonly=True)
    product_size = fields.Char('Ukuran', related='product_id.product_size', readonly=True)
    product_spec = fields.Char('Spesifikasi Lain', related='product_id.product_spec', readonly=True)
    product_brand = fields.Char('Merk', related='product_id.product_brand', readonly=True)
    product_uom_id = fields.Many2one('product.uom', 'Jenis Satuan', related='product_id.uom_id')

