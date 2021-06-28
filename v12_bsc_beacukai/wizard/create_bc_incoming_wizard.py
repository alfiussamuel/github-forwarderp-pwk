from odoo import api,fields,models,_ 
import time
from odoo.exceptions import except_orm, Warning, RedirectWarning

class CreateBcIncomingWizard(models.Model):
    _name = 'create.bc.incoming.wizard'

    picking_id = fields.Many2one('stock.picking', 'Picking')
    """ Header """
    submission_no = fields.Char('Submission No.')           
    document_type_id = fields.Many2one('beacukai.document.type', 'Bea Cukai Type')
    tpb_source_id = fields.Many2one('beacukai.tpb', 'TPB Source Office')
    apiu_id = fields.Many2one('beacukai.apiu', 'APIU') 
    register_number = fields.Char('Register No.')
    tpb_dest_id = fields.Many2one('beacukai.tpb', 'TPB Dest Office')
    date = fields.Date('Bea Cukai Date.')
    delivery_purpose_id = fields.Many2one('beacukai.delivery.purpose', 'Delivery Purpose')
    
    """ Notification Data """
    company_npwp = fields.Char('Company NPWP')
    company_name = fields.Char('Company Name')
    company_address = fields.Text('Company Address')
    company_permission_no = fields.Char('Company Permission No.')
    supplier_id = fields.Many2one('res.partner', 'Supplier Name')
    
    """ Complement Documents """
    fbl_awb_number = fields.Char('FBL/AWB No.')
    fbl_awb_date = fields.Date('FBL/AWB Date')
    delivery_note_number = fields.Char('Delivery Note No.')
    delivery_note_date = fields.Date('Delivery Note Date')
    invoice_number = fields.Char('Invoice No.')
    invoice_date = fields.Date('Invoice Date')
    decree_number = fields.Char('Decree No.')
    decree_date = fields.Date('Decree Date')
    contract_number = fields.Char('Contract No.')
    contract_date = fields.Date('Contract Date')
    packing_list_number = fields.Char('Packing List No.')
    packing_list_date = fields.Date('Packing List Date')
    other = fields.Char('Other')
    finish_date = fields.Datetime('Finish Date')
    
    """ Trade Data """
    currency_id = fields.Many2one('res.currency', 'Currency')
    npdbm = fields.Float('NPDBM')
    amount_usd = fields.Float('Amount USD')
    amount_idr = fields.Float('Amount IDR')
    
    """ Packaging Data """
    packing_number = fields.Char('Merk and Packing No.')
    packaging_number = fields.Float('Number and Type Packaging')
    packaging_type = fields.Many2one('uom.uom', 'Number and Type Packaging')        
    
    @api.multi
    def button_create(self):
        for res in self:
            beacukai_id = self.env['beacukai.incoming'].create({
                                                              'picking_id' : res.picking_id.id,
                                                              'submission_no': res.submission_no,                                                                                                                  
                                                              'document_type_id' : res.document_type_id,
                                                              'tpb_source_id' : res.tpb_source_id,
                                                              'apiu_id' : res.apiu_id, 
                                                              'register_number' : res.register_number,
                                                              'tpb_dest_id' : res.tpb_dest_id,
                                                              'date' : res.date,
                                                              'delivery_purpose_id' : res.delivery_purpose_id,                                                   
                                                              'company_npwp' : res.company_npwp,
                                                              'company_name' : res.company_name,
                                                              'company_address' : res.company_address,
                                                              'company_permission_no' : res.company_permission_no,
                                                              'supplier_id' : res.supplier_id,                                                    
                                                              'fbl_awb_number' : res.fbl_awb_number,
                                                              'fbl_awb_date' : res.fbl_awb_date,
                                                              'delivery_note_number' : res.delivery_note_number,
                                                              'delivery_note_date' : res.delivery_note_date,
                                                              'invoice_number' : res.invoice_number,
                                                              'invoice_date' : res.invoice_date,
                                                              'decree_number' : res.decree_number,
                                                              'decree_date' : res.decree_date,
                                                              'contract_number' : res.contract_number,
                                                              'contract_date' : res.contract_date,
                                                              'packing_list_number' : res.packing_list_number,
                                                              'packing_list_date' : res.packing_list_date,
                                                              'other' : res.other,
                                                              'finish_date' : res.finish_date,            
                                                              'currency_id' : res.currency_id,
                                                              'npdbm' : res.npdbm,
                                                              'amount_usd' : res.amount_usd,
                                                              'amount_idr' : res.amount_idr,                                                    
                                                              'packing_number' : res.packing_number,
                                                              'packaging_number' : res.packaging_number,
                                                              'packaging_type' : res.packaging_type,
                                                              })
            
            for pack in res.picking_id.pack_operation_ids:
                self.env['beacukai.incoming.line'].create({
                                                           'reference': beacukai_id.id,
                                                           'product_id' : pack.product_id.id,    
                                                           'product_name' : pack.product_id.name,
                                                           'product_hs_code' : pack.product_id.hs_code,
                                                           'product_qty' : pack.qty_done,
                                                           'product_uom_id' : pack.product_id.uom_id.id,
                                                           'product_price' : pack.product_id.standard_price,                                                                                                                      
                                                           })
                
            if beacukai_id:
                res.picking_id.write({
                                      'is_beacukai_incoming': True,
                                      'beacukai_incoming_id': beacukai_id.id,
                                      })
                