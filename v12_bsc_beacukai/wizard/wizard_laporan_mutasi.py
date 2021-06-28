# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _
from datetime import datetime, timedelta


class WizardLaporanMutasi(models.TransientModel):
    _name = 'wizard.laporan.mutasi'
    
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    location_id = fields.Many2one('stock.location', 'Location',default=22)

    @api.multi
    def generate_report(self):
        self.ensure_one()
        mutasi_id = ''
        mutasi_ids = []

        



        for res in self:
            moveline_ids = self.env['stock.move'].search([
                                                            ('state','=','done'),                                                        
                                                            ('date', '>=', res.date_from),
                                                            ('date', '<=', res.date_to),
                                                            '|', ('location_id', '=', res.location_id.id),
                                                            ('location_dest_id', '=', res.location_id.id)
                                                            ])

            if moveline_ids:          
                report_name = "Laporan Mutasi " + res.location_id.name + " , " + res.date_from + " - " + res.date_to
                current_report_ids = self.env['laporan.mutasi'].search([('report_name', '=', report_name)])
                if current_report_ids:
                    for current_report_id in current_report_ids:
                        current_report_id.unlink()

                for product in moveline_ids.mapped('product_id'):              
                    mutasi_id = self.env['laporan.mutasi'].create({
                                                                    'name': report_name,
                                                                    'report_name': report_name,
                                                                    'product_code': product.default_code,
                                                                    'product_id': product.id,                    
                                                                    'uom_id': product.uom_id.id,
                                                                    })
                    mutasi_ids.append(mutasi_id)            

                    new_result = {}  
                    saldo_awal = pemasukan = pengeluaran = penyesuaian = saldo_akhir = stock_opname = selisih = 0
                    keterangan = ''                                            

                    inventory_ids = self.env['stock.inventory.line'].search([
                                    ('product_id','=',product.id),
                                    ('location_id','=',res.location_id.id),
                                    ('inventory_id.date','>=',res.date_from),
                                    ('inventory_id.date','<=',res.date_to)
                                    ])


                    if inventory_ids:
                        for inventory in inventory_ids:
                            stock_opname = inventory.product_qty

                    if product.active:                
                        for move_line in moveline_ids:
                          
                            # self.env['laporan.mutasi.line'].create({
                            #     'mutasi_id': mutasi_id,
                            #     'move_id': move_line.id
                            #     })
                            
                            if move_line.location_id.id == self.location_id.id and move_line.product_id.id == product.id and move_line.date_expected < self.date_from:                                                    
                                saldo_awal -= move_line.product_uom_qty
                                move_line.write({'mutasi_id': mutasi_id.id, 'tipe_mutasi':'Saldo Awal'})
                            elif move_line.location_dest_id.id == self.location_id.id and move_line.product_id.id == product.id and move_line.date_expected < self.date_from:                                                    
                                saldo_awal += move_line.product_uom_qty     
                                move_line.write({'mutasi_id': mutasi_id.id, 'tipe_mutasi':'Saldo Awal'})                                                   
                            elif move_line.location_id.id == self.location_id.id and move_line.product_id.id == product.id and move_line.date_expected >= self.date_from:                        
                                if move_line.location_dest_id.usage == "inventory":                                
                                    penyesuaian -= move_line.product_uom_qty
                                    move_line.write({'mutasi_id': mutasi_id.id, 'tipe_mutasi':'Penyesuaian'})                                
                                else:                                
                                    pengeluaran += move_line.product_uom_qty    
                                    move_line.write({'mutasi_id': mutasi_id.id, 'tipe_mutasi':'Pengeluaran'})                            
                            elif move_line.location_dest_id.id == self.location_id.id and move_line.product_id.id == product.id and move_line.date_expected >= self.date_from:                        
                                if move_line.location_id.usage == "inventory":                                
                                    penyesuaian += move_line.product_uom_qty    
                                    move_line.write({'mutasi_id': mutasi_id.id, 'tipe_mutasi':'Penyesuaian'})                            
                                else:                                
                                    pemasukan += move_line.product_uom_qty      
                                    move_line.write({'mutasi_id': mutasi_id.id, 'tipe_mutasi':'Pemasukan'})                          
                        
                        saldo_akhir = saldo_awal + pemasukan - pengeluaran + penyesuaian
                        selisih = abs(saldo_akhir - stock_opname)
                        if selisih == 0: 
                            keterangan = "Sesuai"
                        else:
                            keterangan = "Tidak Sesuai"

                        mutasi_id.write({
                            'saldo_awal': saldo_awal,
                            'pemasukan': pemasukan,
                            'pengeluaran': pengeluaran,
                            'penyesuaian': penyesuaian,
                            'saldo_akhir': saldo_akhir,
                            'stock_opname' : stock_opname,
                            'selisih' : selisih,
                            'keterangan' : keterangan,
                            })

                    
                
        if mutasi_ids:
            ctx = dict(
                self._context)

            action = self.env['ir.model.data'].xmlid_to_object('v12_bsc_beacukai.action_laporan_mutasi')
            if not action:
                action = {
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'res_model': 'laporan.mutasi',
                    'type': 'ir.actions.act_window',
                }
            else:
                action = action[0].read()[0]
                    
            action['domain'] = "[('report_name','=','" + report_name + "')]"
            action['name'] = _('Laporan Mutasi Per ' + str(self.date_from) + ' - ' + str(self.date_to))        
            action['context'] = ctx
            return action
