from odoo import models, api, fields

class BeacukaiAddPurchaseWizard(models.TransientModel):
    _name = 'beacukai.add.purchase.wizard'
    
    beacukai_id = fields.Many2one("beacukai.incoming.23", string="Document No.")
    purchase_id = fields.Many2one("purchase.order", string="Purchase Order")
    purchase_line_ids = fields.Many2many('purchase.order.line', string="PO Lines")

    # @api.onchange('purchase_id')
    # def _onchange_purchase_id(self):
    #     if self.purchase_id:
    #         purchase_line_list = []
    #         purchase_line_ids = self.env['purchase.order.line'].search([('order_id','=',self.purchase_id.id)])
    #         if purchase_line_ids:
    #             for line in purchase_line_ids:
    #                 purchase_line_list.append(line.id)
    #                 self.write({
    #                             'purchase_line_ids' : (0, 0, {
    #                                 'order_id': line.order_id.id,
    #                                 'product_id': line.product_id.id, 
    #                                 'product_uom': line.product_uom.id,
    #                                 'price_unit': line.price_unit,
    #                                 'product_qty': line.product_qty,
    #                                 'name': line.name,
    #                                 'date_planned': line.date_planned
    #                                 })
    #                             })

    #         print purchase_line_list            

    def button_confirm(self):     
        print "BC ID ", self.beacukai_id.name
        print "Purchase ID ", self.purchase_id.name
        print "Purchase Line IDS ", self.purchase_line_ids   

        if self.purchase_line_ids:
            for line in self.purchase_line_ids:
                beacukai_line_id = self.env['beacukai.incoming.line.23'].create({
                                    'reference' : self.beacukai_id.id,
                                    'product_id' : line.product_id.id,
                                    'purchase_id' : self.purchase_id.id,
                                    'purchase_line_id' : line.id,
                                    })

                print "ID BC Line ", beacukai_line_id
                print "No. BC Doc ", beacukai_line_id.reference.name
                print "Product name ", beacukai_line_id.product_id.name
                print "No. PO ", beacukai_line_id.purchase_id.name            

            return {'type': 'ir.actions.act_window_close'}