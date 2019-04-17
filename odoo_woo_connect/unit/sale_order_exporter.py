#    Techspawn Solutions Pvt. Ltd.
#    Copyright (C) 2016-TODAY Techspawn(<http://www.Techspawn.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import logging
from ..model.api import API
from datetime import datetime
from datetime import timedelta
from ..unit.backend_adapter import WpImportExport
_logger = logging.getLogger(__name__)


class WpSaleOrderExport(WpImportExport):

    def get_api_method(self, method, args):
        """ get api for sale order and values"""

        api_method = None
        if method == 'sales_order':
            if not args[0]:
                api_method = 'orders/details'
            else:
                api_method = 'orders/details/' + str(args[0])
        elif method == 'account_invoice':
            if not args[0]:
                api_method = 'orders/' + \
                    str(args[2].woo_id) + '/refunds'
            else:
                api_method = 'orders/' + \
                    str(args[2].woo_id) + '/refunds/' + str(args[0])
        return api_method

    def get_order_lines(self, order_lines):
        """ get all order lines """
        lines = []
        if order_lines:
            for order_line in order_lines:
                product_id = order_line.product_id.product_tmpl_id.backend_mapping.search(
                    [('backend_id', '=', self.backend.id),
                     ('product_id', '=', order_line.product_id.product_tmpl_id.id)],
                    limit=1)
                variation_id = order_line.product_id.backend_mapping.search(
                    [('backend_id', '=', self.backend.id),
                     ('product_id', '=', order_line.product_id.id)],
                    limit=1)
                if product_id:
                    lines.append({"product_id": product_id.woo_id,
                                  "variation_id": variation_id.woo_id,
                                  "quantity": order_line.product_uom_qty,
                                  "price": order_line.price_unit,
                                  "subtotal": order_line.price_subtotal,
                                  "subtotal_tax": order_line.price_tax,
                                  # "taxes":    tax_id
                                  })
        return lines

    def export_sales_order(self, method, arguments):
        """ Export sale order data"""
        _logger.debug("Start calling Woocommerce api %s", method)
        # res_dict = {}
        check=arguments[1].env['wordpress.odoo.sale.order'].search([('order_id','=',arguments[1].id)])
        customer_mapper = arguments[1].partner_id.backend_mapping.search(
            [('backend_id', '=', self.backend.id),
             ('customer_id', '=', arguments[1].partner_id.id)], limit=1)
        status = ''
        if arguments[1].state == 'done':
            status = 'completed'
        elif arguments[1].state == 'draft':
            status = 'processing'
        elif arguments[1].state == 'sale':
            status = 'on-hold'
        elif arguments[1].state == 'cancel':
            status = 'cancelled'
        if check:
            result_dict = {
            "status": status,
            }
        else:
            result_dict = {
                # "payment_method": "bacs",
                # "payment_method_title": "Direct Bank Transfer",
                # "set_paid": arguments[1].invoiced,
                "customer_id": customer_mapper.woo_id or 0,
                'total_tax': arguments[1].amount_tax,
                "total": arguments[1].amount_total,
                "status": status,
                "billing": {"first_name": arguments[1].partner_id.name or None,
                            "last_name": arguments[1].partner_id.last_name or None,
                            "company": arguments[1].partner_id.company or None,
                            "address_1": arguments[1].partner_id.street or None,
                            "address_2": arguments[1].partner_id.street2 or None,
                            "city": arguments[1].partner_id.city or None,
                            "state": arguments[1].partner_id.state_id.code or None,
                            "postcode": arguments[1].partner_id.zip or None,
                            "country": arguments[1].partner_id.country_id.code or None,
                            "email": arguments[1].partner_id.email or None,
                            "phone": arguments[1].partner_id.phone or None,
                            },
                "shipping": {"first_name": arguments[1].partner_id.name or None,
                             "last_name": arguments[1].partner_id.last_name or None,
                             # "address_1": "969 Market",
                             # "address_2": "",
                             # "city": "San Francisco",
                             # "state": "CA",
                             # "postcode": "94103",
                             # "country": "US"
                             },
                "line_items": self.get_order_lines(arguments[1].order_line),
                "tax_lines": []
                # "shipping_lines": [{
                #                     "method_id": "flat_rate",
                #                     "method_title": "Flat Rate",
                #                     "total": 10
                #                     }]
            }

        res = self.export(method, result_dict, arguments)
        if res:
            res_dict = res.json()
        else:
            res_dict = None
        return {'status': res.status_code, 'data': res_dict or {}}

    def export_invoice_refund(self, method, arguments):
        """ Export refund invoice data"""
        _logger.debug("Start calling Woocommerce api %s", method)

        line_items = []
        for line_item in arguments[1].invoice_line_ids:
            line_items.append({
                # "id": arguments[1].invoice_line_ids.id,
                "name": line_item.product_id.name,
                # "sku": "12345",
                "product_id": line_item.product_id.id,
                # "variation_id": 0,
                "quantity": line_item.quantity,
                # "tax_class": "",
                "price": line_item.price_unit,
                # "subtotal": "-2.00",
                # "subtotal_tax": "0.00",
                # "total": "-2.00",
                # "total_tax": "0.00",
                # "taxes": arguments[1].invoice_line_ids.invoice_line_tax_ids,
                # "meta": []
            })

        result_dict = {
            "amount": str(arguments[1].amount_total),
            "reason": arguments[1].name,
            "line_items": line_items,

        }
        res = self.export(method, result_dict, arguments)
        if res:
            res_dict = res.json()
        else:
            res_dict = None
        return {'status': res.status_code, 'data': res_dict or {}}
