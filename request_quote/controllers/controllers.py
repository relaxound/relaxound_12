# -*- coding: utf-8 -*-
from odoo import fields, http, _
from odoo.addons.website.controllers.backend import WebsiteBackend
from odoo.http import request


class kitepages(http.Controller):

    @http.route(['/quotation'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def quote_send(self, product_id, **kw):
        values = {
            'product_id': int(product_id),
        }
        template = 'request_quote.quotation'
        return request.render(template, values)

    def _filter_attributes(self, **kw):
        return {k: v for k, v in kw.items() if "attribute" in k}

    # @http.route(['/quotation'], type='http', auth="public", methods=['GET'], website=True, csrf=False)
    # def quote_send_get(self, **kw):
    #     values={
    #     }
    #     template = 'request_quote.quotation'
    #     return request.render(template,values)

    # def _filter_attributes(self, **kw):
    #     return {k: v for k, v in kw.items() if "attribute" in k}
