# -*- coding: utf-8 -*-
from odoo import models,fields

#Trackingnummer aus dem Paket zur Operation hinzufügen
class stock_move_line(models.Model):
    _inherit="stock.move"
    tracking_nr=fields.Char("Tracking Number",related='result_package_id.tracking_nr')

#Trackingnummer pro Paket hinzufügen
class stock_quant_package(models.Model):
    _inherit="stock.quant.package"
    tracking_nr=fields.Char("Tracking Number")
