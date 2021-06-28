from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class ProductTemplate(models.Model):
    _inherit = "product.template"

    hs_code = fields.Char('HS Code')
    category_product = fields.Selection([('lokal', 'Lokal'),
                                         ('import', 'Import'),
                                         ('ekspor', 'Ekspor'),
                                         ('mesin', 'Mesin')], 'Category', default="lokal")
    waste = fields.Float(string='Waste (%)')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'The Item Code of the product must be unique !')
    ]

    @api.one
    def get_qty(self):
        for res in self:
            print (">>>>>>>>>>><<<<<<<<<", res.qty_available)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if "[" in name and "]" in name:
            code = name[name.find("[") + 1:name.find("]")]
            name = name[name.find("]")+2:]
            args.append(('default_code', '=', code))

        return super(ProductTemplate, self).name_search(name=name, args=args, operator=operator, limit=limit)


class ProductProduct(models.Model):
    _inherit = "product.product"

    category_product = fields.Selection([('lokal', 'Lokal'),
                                         ('import', 'Import'),
                                         ('ekspor', 'Ekspor'),
                                         ('mesin', 'Mesin')], 'Category', default="lokal")
    waste = fields.Float(string='Waste (%)',related='product_tmpl_id.waste')

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if "[" in name and "]" in name:
            code = name[name.find("[") + 1:name.find("]")]
            name = name[name.find("]") + 2:]
            args.append(('default_code', '=', code))

        return super(ProductProduct, self).name_search(name=name, args=args, operator=operator, limit=limit)

    @api.multi
    def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
        domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc
        dates_in_the_past = False
        if to_date and to_date < fields.Datetime.now(): #Only to_date as to_date will correspond to qty_available
            dates_in_the_past = True

        domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
        domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
        if lot_id:
            domain_quant += [('lot_id', '=', lot_id)]
        if owner_id:
            domain_quant += [('owner_id', '=', owner_id)]
            domain_move_in += [('restrict_partner_id', '=', owner_id)]
            domain_move_out += [('restrict_partner_id', '=', owner_id)]
        if package_id:
            domain_quant += [('package_id', '=', package_id)]
        if dates_in_the_past:
            domain_move_in_done = list(domain_move_in)
            domain_move_out_done = list(domain_move_out)
        if from_date:
            domain_move_in += [('date', '>=', from_date)]
            domain_move_out += [('date', '>=', from_date)]
        if to_date:
            domain_move_in += [('date', '<=', to_date)]
            domain_move_out += [('date', '<=', to_date)]

        Move = self.env['stock.move']
        Quant = self.env['stock.quant']
        domain_move_in_todo = [('state', 'not in', ('done', 'cancel', 'draft'))] + domain_move_in
        domain_move_out_todo = [('state', 'not in', ('done', 'cancel', 'draft'))] + domain_move_out
        moves_in_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
        moves_out_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
        quants_res = dict((item['product_id'][0], item['qty']) for item in Quant.read_group(domain_quant, ['product_id', 'qty'], ['product_id'], orderby='id'))
        if dates_in_the_past:
            # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
            domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
            domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
            moves_in_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
            moves_out_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))

        res = dict()
        for product in self.with_context(prefetch_fields=False):
            res[product.id] = {}
            if dates_in_the_past:
                qty_available = quants_res.get(product.id, 0.0) - moves_in_res_past.get(product.id, 0.0) + moves_out_res_past.get(product.id, 0.0)
            else:
                qty_available = quants_res.get(product.id, 0.0)
            res[product.id]['qty_available'] = float_round(qty_available, precision_rounding=product.uom_id.rounding)
            res[product.id]['incoming_qty'] = moves_in_res.get(product.id, 0.0)
            res[product.id]['outgoing_qty'] = moves_out_res.get(product.id, 0.0)
            res[product.id]['virtual_available'] = qty_available + res[product.id]['incoming_qty'] - res[product.id]['outgoing_qty']

            # print qty_available
            # print "Incoming ", res[product.id]['incoming_qty']
            # print "Outgoing ", res[product.id]['outgoing_qty']
            # print "Virtual ", res[product.id]['virtual_available']
            
        return res
