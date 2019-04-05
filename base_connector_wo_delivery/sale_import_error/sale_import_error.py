# -*- coding: utf-8 -*-

from odoo import models,fields

#allgemeine Klasse zum Speichern von Fehlern beim Bestellimport
class SaleImportError(models.Model):
    _name ='sale.import.error'
    _description = 'sale_import'
    
    source=fields.Char('Error Source',index=True)
    ordernumber=fields.Char('Ordernumber',index=True)
    description=fields.Char('Error Description')
    done=fields.Boolean('Done')
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        