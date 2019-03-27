# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
#from openerp.osv import osv
#from openerp.osv import fields

class ResPartner(models.Model):
    _inherit = "res.partner"

    country_name = fields.Char('Country Name', related='country_id.name')
    is_retailer = fields.Boolean('Retailer')

#class ResPartner(osv.osv):
#    _inherit = "res.partner"
#    _description = "Res partner Sequences"
#
#    _columns = {
#        'is_retailer': fields.boolean('Retailer'),
#    }


    @api.model
    def create(self, vals):
        if vals.get('is_retailer') == True:
            vals['ref'] = self.env['ir.sequence'].next_by_code('res.partner') or '/'
        return super(ResPartner, self).create(vals)

    @api.multi
    def write(self, values):
        if values.get('is_retailer') == True:
            values['ref'] = self.env['ir.sequence'].next_by_code('res.partner') or '/'
        return super(ResPartner, self).write(values)

    @api.onchange('category_id')
    def _onchange_retailer(self):
        self.is_retailer = False
        if self.category_id:
            for categ in self.category_id:
                if categ.name == u'Händler':
                    self.is_retailer = True
