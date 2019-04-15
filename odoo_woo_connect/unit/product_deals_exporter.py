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


class WpProductDealExport(WpImportExport):

    """ Models for woocommerce customer export """

    def get_api_method(self, method, args):
        """ get api for customer"""
        api_method = None
        if method == 'campaign':
            if not args[0]:
                api_method = 'campaign/details'
            else:
                api_method = 'campaign/details/' + str(args[0])
        return api_method

    def get_product(self, product_ids):
        product = []
        if product_ids:
            for product_id in product_ids:
                woo_product = product_id.env['wordpress.odoo.product.template']
                mapper = woo_product.search(
                    [
                        ('backend_id','=',self.backend.id),
                        ('product_id','=',product_id.id),
                    ],limit=1)
                if mapper:
                    product.append(int(mapper.woo_id))
                else:
                    export_product = product_id.export(self.backend)
                    woo_product = product_id.env['wordpress.odoo.product.template']
                    mapper = woo_product.search(
                        [
                            ('backend_id','=',self.backend.id),
                            ('product_id','=',product_id.id),
                        ],limit=1)
                    product.append(int(mapper.woo_id))
        return product

    def get_product_exclude(self, product_excluded_ids):
        product_ex = []
        if product_excluded_ids:
            for product_id in product_excluded_ids:
                woo_product = product_id.env['wordpress.odoo.product.template']
                mapper = woo_product.search(
                    [
                        ('backend_id','=',self.backend.id),
                        ('product_id','=',product_id.id),
                    ],limit=1)
                if mapper:
                    product_ex.append(int(mapper.woo_id))
                else:
                    export_product = product_id.export(self.backend)
                    woo_product = product_id.env['wordpress.odoo.product.template']
                    mapper = woo_product.search(
                        [
                            ('backend_id','=',self.backend.id),
                            ('product_id','=',product_id.id),
                        ],limit=1)
                    product_ex.append(int(mapper.woo_id))
        return product_ex

    def get_product_cat(self, product_categ_ids):
        product_categ = []
        if product_categ_ids:
            for product_id in product_categ_ids:
                woo_category = product_id.env['wordpress.odoo.category']
                mapper = woo_category.search(
                    [
                        ('backend_id','=',self.backend.id),
                        ('category_id','=',product_id.id),
                    ],limit=1)
                if mapper:
                    product_categ.append(int(mapper.woo_id))
                else:
                    export_categ = product_id.export(self.backend)
                    woo_category = product_id.env['wordpress.odoo.category']
                    mapper = woo_category.search(
                        [
                            ('backend_id','=',self.backend.id),
                            ('category_id','=',product_id.id),
                        ],limit=1)
                    product_categ.append(int(mapper.woo_id))
        return product_categ

    def get_exclude_product_cat(self, product_categ_ids):
        product_ex_categ = []
        if product_categ_ids:
            for product_id in product_categ_ids:
                woo_category = product_id.env['wordpress.odoo.category']
                mapper = woo_category.search(
                    [
                        ('backend_id','=',self.backend.id),
                        ('category_id','=',product_id.id),
                    ],limit=1)
                if mapper:
                    product_ex_categ.append(int(mapper.woo_id))
                else:
                    export_categ = product_id.export(self.backend)
                    woo_category = product_id.env['wordpress.odoo.category']
                    mapper = woo_category.search(
                        [
                            ('backend_id','=',self.backend.id),
                            ('category_id','=',product_id.id),
                        ],limit=1)
                    product_ex_categ.append(int(mapper.woo_id))
        return product_ex_categ

    def export_product_deal(self, method, arguments):
        """ Export product deals data"""

        _logger.debug("Start calling Woocommerce api %s", method)

        product_deal_woo_ids = []
        if arguments[1].id:
            mapper = arguments[1].backend_mapping.search(
                [('backend_id', '=', self.backend.id), ('productdeal_id', '=', arguments[1].id)])
            if mapper.woo_id:
                product_deal_woo_ids.append(mapper.woo_id)

        f_image = arguments[1].feature_image.decode('utf-8')
        b_image = arguments[1].banner_image.decode('utf-8')
        result_dict = {
            # "id": arguments[1].id or None,
            "dates_from": arguments[1].campaign_date_from or None,
            "dates_to": arguments[1].campaign_date_to or None,
            "days": {
                "mon": arguments[1].mon or None,
                "tue": arguments[1].tue or None,
                "wed": arguments[1].wed or None,
                "thu": arguments[1].thur or None,
                "fri": arguments[1].fri or None,
                "sat": arguments[1].sat or None,
                "sun": arguments[1].sun or None,
            },

            "post_title": arguments[1].name or None,
            "post_excerpt": arguments[1].desc or None,
            "post_status": arguments[1].status or None,
            "method": arguments[1].price_adjustment_method or None,
            "value": arguments[1].value or None,
            "priority": arguments[1].campaign_priority or None,
            "all_products": arguments[1].all_products,
            # "product_ids": self.get_product(arguments[1].products_ids),
            # "category_ids": self.get_product_cat(arguments[1].product_categ_ids),
            "exclude_product_id": self.get_product_exclude(arguments[1].product_excluded_ids),
            "exclude_category_ids": self.get_exclude_product_cat(arguments[1].exclude_category_ids),
            "feature_image":[{'src':f_image,'id':mapper.featured_image or None, 'name':arguments[1].name, 'position':0}],
            "banner_image":[{'src':b_image,'id':mapper.banner_image or None, 'name':arguments[1].name, 'position':0}],
            "deals_category": arguments[1].deals_category or None,
        }
        if arguments[1].all_products:
            pass
        else:
            result_dict["product_ids"] = self.get_product(arguments[1].products_ids)
            result_dict["category_ids"] = self.get_product_cat(arguments[1].product_categ_ids)
        res = self.export(method, result_dict, arguments)
        if res:
            res_dict = res.json()
        else:
            res_dict = None
        _logger.info("Odoo Product Export Data: %s",res_dict)
        return {'status': res.status_code, 'data': res_dict or {}}


    def run_product_deal(self, method):
        """ Export product deals data"""
        _logger.debug("Start calling Woocommerce api %s", method)
        result_dict = {   
            'run_all':True,
            }
        _logger.info(result_dict)
        res = self.run_campaign(method, result_dict)
        if res:
            res_dict = res.json()
        else:
            res_dict = None
        return {'status': res.status_code, 'data': res_dict or {}}
