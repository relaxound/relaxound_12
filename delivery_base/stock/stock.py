# -*- coding: utf-8 -*-

from odoo import models,fields,api,_
    
#Trackingnummer aus dem Paket zur Operation hinzufügen
class StockPickingCustom(models.Model):
    _inherit="stock.move"

    tracking_nr = fields.Char("Tracking Number")
    abc = fields.Char("ABC")
    
#Trackingnummer pro Paket hinzufügen
class stock_quant_package(models.Model):
    _inherit="stock.quant.package"    
    tracking_nr=fields.Char("Tracking Number")