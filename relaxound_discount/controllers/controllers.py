# -*- coding: utf-8 -*-
from odoo import http

# class RelaxoundDiscount(http.Controller):
#     @http.route('/relaxound_discount/relaxound_discount/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/relaxound_discount/relaxound_discount/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('relaxound_discount.listing', {
#             'root': '/relaxound_discount/relaxound_discount',
#             'objects': http.request.env['relaxound_discount.relaxound_discount'].search([]),
#         })

#     @http.route('/relaxound_discount/relaxound_discount/objects/<model("relaxound_discount.relaxound_discount"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('relaxound_discount.object', {
#             'object': obj
#         })