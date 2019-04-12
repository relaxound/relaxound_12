# -*- coding: utf-8 -*-
#
#
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
from . backend_adapter import WpImportExport

_logger = logging.getLogger(__name__)


class WpProductExport(WpImportExport):

    def get_api_method(self, method, args):
        """ get api for product and values"""

        api_method = None
        if method == 'products':
            if not args[0]:
                api_method = 'products'
            else:
                api_method = 'products/' + str(args[0])
        return api_method

    def get_attributes(self, product):
        """ get all attributes of product """
        attributes = []
        for attr in product.attribute_line_ids:
            attributes_value = []
            mapper = attr.attribute_id.backend_mapping.search(
                [('backend_id', '=', self.backend.id), ('attribute_id', '=', attr.attribute_id.id)], limit=1)
            if not mapper.woo_id:
                attr.attribute_id.export_product_attribute(self.backend)
                mapper = attr.attribute_id.backend_mapping.search(
                    [('backend_id', '=', self.backend.id), ('attribute_id', '=', attr.attribute_id.id)], limit=1)
            attributes.append({
                "id": mapper.woo_id or None,
                "name": attr.attribute_id.name or None,
                # "visible": attr.attribute_id.visible,
                "variation": attr.attribute_id.create_variant,
                # "options": attributes_value,
            })
        return attributes
    


    def get_category(self, product):
        """ get all categories of product """
        categ_id = []
        if product.categ_ids:
            for categ in product.categ_ids:
                mapper = categ.backend_mapping.search(
                    [('backend_id', '=', self.backend.id), ('category_id', '=', categ.id)])
                categ_id.append({'id': mapper.woo_id or None})
                categ_parent = categ.parent_id
                while categ_parent.parent_id:
                    mapper_parent = categ.backend_mapping.search(
                        [('backend_id', '=', self.backend.id), ('category_id', '=', categ_parent.id)])
                    categ_id.append({'id': mapper_parent.woo_id})
                    categ_parent = categ_parent.parent_id
        return categ_id

    def get_tag(self, product):
        """ get all categories of product """
        tag_id = []
        if product.tag_ids:
            for tag in product.tag_ids:
                mapper = tag.backend_mapping.search(
                    [('backend_id', '=', self.backend.id), ('product_tag_id', '=', tag.id)])
                tag_id.append({'id': mapper.woo_id or None})
        return tag_id

    def get_images(self, product):
        """ get all categories of product """
        count = 1
        product_mapper = product.backend_mapping.search(
            [('backend_id', '=', self.backend.id), ('product_id', '=', product.id)], limit=1)
        if product_mapper:
            product_image_id = product_mapper.image_id
        else:
            product_image_id = 0

        if product.image :
            images = [{"src": product.image or False,
                       "name": product.name or None,
                       "position": 0,
                       'id': product_image_id or 0}]
        else :
            images = []

        if product.product_image_ids:
            for image in product.product_image_ids:
                mapper = image.backend_mapping.search([('backend_id', '=', self.backend.id),
                                                       ('product_image_id', '=', image.id)], limit=1)
                images.append({"src": image.image or None,
                               "name": image.name or product.name + str(count),
                               "position": count,
                               'id': mapper.woo_id or 0})
                count += 1
        return images

    def get_product_variant(self, product):
        """ get all variant of product """
        product_variant = []
        for var_ids in product.product_variant_ids:
            woo_product_comb = var_ids
            tot_price = 0
            attr_array = []
            for attribute in woo_product_comb.attribute_value_ids:
                tot_price += attribute.price_extra
                attr_mapper = attribute.attribute_id.backend_mapping.search(
                    [('backend_id', '=', self.backend.id), ('attribute_id', '=', attribute.attribute_id.id)])
                attr = {
                    'id': attr_mapper.woo_id or None,
                    'name': attribute.attribute_id.name or Non or None,
                    'option': attribute.name or Non or None,
                }
                attr_array.append(attr)
            if woo_product_comb:
                mapper = woo_product_comb.backend_mapping.search(
                    [('backend_id', '=', self.backend.id), ('product_id', '=', woo_product_comb.id)])
                product_variant_dict = {
                    "id": mapper.woo_id or None,
                    "sku": woo_product_comb.default_code or None,
                    "weight": woo_product_comb.weight or None,
                    "regular_price": str(woo_product_comb.regular_price) or None,
                    'sale_price': str(woo_product_comb.sale_price) or None,
                    "stock_quantity": woo_product_comb.qty_available or None,
                    "sale_price": woo_product_comb.lst_price or None,
                    # 'images': self.get_images(arguments[1]) ,
                    "dimensions": [{'width': str(woo_product_comb.website_size_x) or None,
                                    'length': str(woo_product_comb.website_size_y) or None,
                                    'height': str(woo_product_comb.website_size_z) or None,
                                    }],
                    'managing_stock': True,
                    'attributes': attr_array or '',

                }
                product_variant.append(product_variant_dict)
        return product_variant

    def export_product(self, method, arguments):
        """ Export product data"""
        _logger.debug("Start calling Woocommerce api %s", method)

        if arguments[1].website_published:
            status = 'publish'
        else:
            status = 'draft'
        attributes = []
        for attr in arguments[1].attribute_line_ids:
            attributes_value = []
            mapper = attr.attribute_id.backend_mapping.search(
                [('backend_id', '=', self.backend.id), ('attribute_id', '=', attr.attribute_id.id)])

            # export_product_attribute('attribute',[None, attr.attribute_id])
            for value in attr.value_ids:
                # export_product_attribute_value('attribute_value',[None, attr.attribute_id])
                attributes_value.append(value.name)
            attributes.append({
                "id": mapper.woo_id or None,
                "name": attr.attribute_id.name or None,
                "visible": True,
                "variation": True,
                "options": attributes_value,
            })
        result_dict = {
            'name': arguments[1].name or None,
            'sku': arguments[1].default_code or None,
            'weight': str(arguments[1].weight) or None,
            'stock_quantity': arguments[1].qty_available or None,
            'short_description': arguments[1].short_description or '',
            'description': arguments[1].description or '',
            'categories': self.get_category(arguments[1]),
            "attributes": self.get_attributes(arguments[1]),

            'tags': self.get_tag(arguments[1]) or None,
            'dimensions': {'length': str(arguments[1].website_size_x) or None,
                           'width': str(arguments[1].website_size_y) or None,
                           'height': str(arguments[1].website_size_z) or None,
                           },
            'status': status,
        }

        if arguments[1].product_variant_count > 1:
            result_dict.update({
                'type': "variable",
                'regular_price': str(arguments[1].regular_price) or None,
                'sale_price': str(arguments[1].sale_price) or None,
                'variations': self.get_product_variant(arguments[1]),
            })
        else:
            result_dict.update({
                'type': "simple",
                'managing_stock': True,
                'regular_price': str(arguments[1].regular_price) or None,
                'sale_price': str(arguments[1].sale_price) or None,
            })
        if arguments[1].qty_available:
            result_dict['manage_stock'] = True
            result_dict['in_stock'] = True
            result_dict['stock_quantity'] = arguments[1].qty_available
        else:
            result_dict['manage_stock'] = True
            result_dict['in_stock'] = False
            result_dict['stock_quantity'] = arguments[1].qty_available
        _logger.info("Odoo Product Export Data: %s",result_dict)
        r = self.export(method, result_dict, arguments)

        return {'status': r.status_code, 'data': r.json()}
