# -*- coding: utf-8 -*-
from odoo import http

# class CustomChatterBox(http.Controller):
#     @http.route('/custom_chatter_box/custom_chatter_box/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_chatter_box/custom_chatter_box/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_chatter_box.listing', {
#             'root': '/custom_chatter_box/custom_chatter_box',
#             'objects': http.request.env['custom_chatter_box.custom_chatter_box'].search([]),
#         })

#     @http.route('/custom_chatter_box/custom_chatter_box/objects/<model("custom_chatter_box.custom_chatter_box"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_chatter_box.object', {
#             'object': obj
#         })