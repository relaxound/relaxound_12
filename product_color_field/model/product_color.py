# -*- coding: utf-8 -*-

from odoo import models, fields

class ProductColor(models.Model):
    _name = 'product.color'
    _description ='Color Module'
    name = fields.Char('Name', translate=True, required=True)
    
#     def name_get(self, cr, uid, ids, context=None):
#         if context is None:
#             context = {}
#         if isinstance(ids, (int, long)):
#             ids = [ids]
#         res = []
#         for record in self.browse(cr, uid, ids, context=context):
#             res.append((record.id, '%s %s' % (record.number,record.name)))
#         return res
#     
#     def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
#         result=[]
#         for color in self.browse(cr, user, self.search(cr, user, ['|',('name','ilike',name),('number','ilike',name)]), context):
#             result.append((color.id,'%s %s' % (color.number,color.name)))        
#         return result