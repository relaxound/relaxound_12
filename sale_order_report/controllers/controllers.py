# -*- coding: utf-8 -*-
from odoo import http

# class SaleOrder(http.Controller):
#     @http.route('/sale__order/sale__order/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale__order/sale__order/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale__order.listing', {
#             'root': '/sale__order/sale__order',
#             'objects': http.request.env['sale__order.sale__order'].search([]),
#         })

#     @http.route('/sale__order/sale__order/objects/<model("sale__order.sale__order"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale__order.object', {
#             'object': obj
#         })