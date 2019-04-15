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


class WpProductCouponExport(WpImportExport):

    def get_api_method(self, method, args):
        """ get api for coupon and values"""
        api_method = None
        if method == 'coupon':
            if not args[0]:
                api_method = 'coupons/details'
            else:
                api_method = 'coupons/details/' + str(args[0])
        return api_method

    def get_product_id(self, product):

        product_id = []
        if product.product_ids:
          if product.product_ids.details_model == 'nadanew.vehicle.product':
            pp=product.env['product.product'].search([('product_tmpl_id','=',product.product_ids.id)])
            mu=product.env['major_unit.major_unit'].search([('product_id','in',pp.ids)])
            woo = product.env['wordpress.odoo.mu.product'].search([('major_unit_id','in',mu.ids)]).woo_id
            product_id.append(woo or None)
          else:
            for prod in product.product_ids:
                mapper = prod.backend_mapping.search(
                    [('backend_id', '=', self.backend.id), ('product_id', '=', prod.id)], limit=1)
                product_id.append(mapper.woo_id or None)
        return product_id

    def get_excluded_product_id(self, product):

        excluded_product_id = []
        if product.exclude_product_ids:
            for prod in product.product_ids:
                mapper = prod.backend_mapping.search(
                    [('backend_id', '=', self.backend.id), ('product_id', '=', prod.id)], limit=1)
                excluded_product_id.append(mapper.woo_id or None)
        return excluded_product_id

    def get_product_category_id(self, product):

        product_category_id = []
        if product.product_category_ids:
            for categ in product.product_category_ids:
                mapper = categ.backend_mapping.search(
                    [('backend_id', '=', self.backend.id), ('category_id', '=', categ.id)], limit=1)
                product_category_id.append(mapper.woo_id or None)
        return product_category_id

    def get_exclude_product_category_id(self, product):

        exclude_product_category_id = []
        if product.exclude_product_category_ids:
            for categ in product.exclude_product_category_ids:
                mapper = categ.backend_mapping.search(
                    [('backend_id', '=', self.backend.id), ('category_id', '=', categ.id)], limit=1)
                exclude_product_category_id.append(mapper.woo_id or None)
        return exclude_product_category_id

    def get_customer_email(self, product):

        customer_email = []
        if product.customer_emails:
            for customer in product.customer_emails:
                customer_email.append(customer.email)
        return customer_email

    def export_product_coupon(self, method, arguments):
        """ Export product coupon data"""
        _logger.debug("Start calling Woocommerce api %s", method)

        result_dict = {"code": arguments[1].name or None,
                       "type": arguments[1].type or None,
                       "amount": str(arguments[1].amount) or None,
                       "enable_free_shipping": arguments[1].enable_free_shipping or None,
                       "date_expires": arguments[1].expiry_date or None,
                       "minimum_amount": str(arguments[1].minimum_amount) or None,
                       "maximum_amount": str(arguments[1].maximum_amount) or None,
                       "individual_use": arguments[1].individual_use or None,
                       "exclude_sale_items": arguments[1].exclude_sale_items or None,
                       "product_ids": self.get_product_id(arguments[1]) or None,
                       "exclude_product_ids": self.get_excluded_product_id(arguments[1]) or None,
                       "product_category_ids": self.get_product_category_id(arguments[1]) or None,
                       "exclude_product_category_id": self.get_exclude_product_category_id(arguments[1]) or None,
                       "customer_emails": self.get_customer_email(arguments[1]) or None,
                       "usage_limit": arguments[1].usage_limit or None,
                       "usage_limit_per_user": arguments[1].usage_limit_per_user or None,
                       "limit_usage_to_x_items": arguments[1].limit_usage_to_x_items or None,
                       "usage_count": arguments[1].usage_count or None,
                       "sequence": arguments[1].sequence or None,
                       "description": arguments[1].desc or None,
                       # "description": arguments[1].desc or None,
                       }
        res = self.export(method, result_dict, arguments)
        if res:
            res_dict = res.json()
        else:
            res_dict = None
        return {'status': res.status_code, 'data': res_dict or {}}
