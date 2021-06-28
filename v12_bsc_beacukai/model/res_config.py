# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api


class BcConfigSettings(models.TransientModel):
    _name = 'bc.config.settings'
    _inherit = 'res.config.settings'

    # company_id = fields.Many2one('res.company', string='Company', required=True,
    #     default=lambda self: self.env.user.company_id)
    no_tpb = fields.Char("No Izin TPB")
    tgl_tpb = fields.Date("Tanggal Izin TPB")
    jenis_api = fields.Selection([
        ('APIU', 'APIU'),
        ('APIP', 'APIP')
        ],"Jenis API")
    nomor_api = fields.Char("Nomor API")
    bc_type = fields.Selection([
        (0, 'Kawasan Berikat'),
        (1, 'Gudang Berikat')
        ],"Jenis TPB")
    # group_bc_kawasan_berikat = fields.Boolean("Kawasan Berikat",implied_group='group_bc_kawasan_berikat')
    # group_bc_kawasan_berikat2 = fields.Boolean("Kawasan Berikat",implied_group='group_bc_kawasan_berikat')
    module_v10_bsc_beacukai_kb = fields.Boolean("Kawasan Berikat")
    module_v10_bsc_beacukai_gb = fields.Boolean("Gudang Berikat")
    # module_bc_gudang_berikat = fields.Boolean("Gudang Berikat")

    
    @api.multi
    def set_bc_type(self):
        self.env['ir.config_parameter'].set_param(
            'bc_type', (self.bc_type or ''))
        self.env['ir.config_parameter'].set_param('no_tpb', (self.no_tpb or ''))
        self.env['ir.config_parameter'].set_param('tgl_tpb', (self.tgl_tpb or ''))
        self.env['ir.config_parameter'].set_param('jenis_api', (self.jenis_api or ''))
        self.env['ir.config_parameter'].set_param('nomor_api', (self.nomor_api or ''))
        irModuleObj = self.env['ir.module.module']
        irModuleObj.update_list()
        if self.bc_type == 0:
            moduleIds = irModuleObj.search([('state', '!=', 'installed'),('name', '=', 'v10_bsc_beacukai_kb')])
            if moduleIds:
               moduleIds[0].button_immediate_install()
            moduleUns = irModuleObj.search([('state', '=', 'installed'),('name', '=', 'v10_bsc_beacukai_gb')])
            if moduleUns:
               moduleUns[0].button_immediate_uninstall()
        else:
            moduleIds = irModuleObj.search([('state', '!=', 'installed'),('name', '=', 'v10_bsc_beacukai_gb')])
            if moduleIds:
               moduleIds[0].button_immediate_install()
            moduleUns = irModuleObj.search([('state', '=', 'installed'),('name', '=', 'v10_bsc_beacukai_kb')])
            if moduleUns:
               moduleUns[0].button_immediate_uninstall()

    def get_default_bc_type(self,fields):
        val = {}
        val['bc_type'] = self.env['ir.config_parameter'].get_param('bc_type', default='')
        val['no_tpb'] = self.env['ir.config_parameter'].get_param('no_tpb', default='')
        val['tgl_tpb'] = self.env['ir.config_parameter'].get_param('tgl_tpb', default='')
        val['jenis_api'] = self.env['ir.config_parameter'].get_param('jenis_api', default='')
        val['nomor_api'] = self.env['ir.config_parameter'].get_param('nomor_api', default='')

        return val