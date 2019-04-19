from odoo import fields,models

class woo_req_type_ept(models.Model):
    _name='woo.req.type.ept'
    _description='woo.req.type.ept'
    
    name=fields.Char('Type')