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
import json
import base64
from ..unit.backend_adapter import WpImportExport
import re
from odoo import http
from odoo.http import request
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class WpProductExport(WpImportExport):

    def get_api_method(self, method, args):
        """ get api for product and values"""
        api_method = None
        if method == 'products':
            if not args[0]:
                api_method = 'products/details'
            else:
                api_method = 'products/details/' + str(args[0])
        return api_method

    def get_category(self, product):
        """ get all categories of product """
        categ_id = []
        if product.categ_id:
            mapper = product.categ_id.backend_mapping.search(
                [('backend_id', '=', self.backend.id), ('category_id', '=', product.categ_id.id)], limit=1)
            if mapper.woo_id:
                categ_id.append({'id': mapper.woo_id or None})
            else:
                product.categ_id.export(self.backend)
                mapper = product.categ_id.backend_mapping.search(
                    [('backend_id', '=', self.backend.id), ('category_id', '=', product.categ_id.id)], limit=1)
                categ_id.append({'id': mapper.woo_id or None})

        if product.public_categ_ids:
            for e_categ in product.public_categ_ids:
                mapper = e_categ.backend_mapping.search(
                    [('backend_id', '=', self.backend.id), ('ecom_category_id', '=', e_categ.id)], limit=1)
                if mapper.woo_id:
                    categ_id.append({'id': mapper.woo_id or None})
                else:
                    e_categ.export(self.backend)
                    mapper = e_categ.backend_mapping.search(
                        [('backend_id', '=', self.backend.id), ('ecom_category_id', '=', e_categ.id)], limit=1)
                    categ_id.append({'id': mapper.woo_id or None})
                e_categ_parent = e_categ.parent_id
                while e_categ_parent.parent_id:
                    mapper_parent = e_categ.backend_mapping.search(
                        [('backend_id', '=', self.backend.id), ('ecom_category_id', '=', e_categ_parent.id)], limit=1)
                    categ_id.append({'id': mapper_parent.woo_id})
                    e_categ_parent = e_categ_parent.parent_id

        if product.categ_ids:
            for categ in product.categ_ids:
                mapper = categ.backend_mapping.search(
                    [('backend_id', '=', self.backend.id), ('category_id', '=', categ.id)], limit=1)
                if mapper.woo_id:
                    categ_id.append({'id': mapper.woo_id or None})
                else:
                    categ.export(self.backend)
                    mapper = categ.backend_mapping.search(
                        [('backend_id', '=', self.backend.id), ('category_id', '=', categ.id)], limit=1)
                    categ_id.append({'id': mapper.woo_id or None})

                categ_parent = categ.parent_id
                while categ_parent.parent_id:
                    mapper_parent = categ.backend_mapping.search(
                        [('backend_id', '=', self.backend.id), ('category_id', '=', categ_parent.id)], limit=1)
                    categ_id.append({'id': mapper_parent.woo_id})
                    categ_parent = categ_parent.parent_id
        return categ_id

    def get_tag(self, product):
        """ get all categories of product """
        tag_id = []
        if product.tag_ids:
            for tag in product.tag_ids:
                mapper = tag.backend_mapping.search(
                    [('backend_id', '=', self.backend.id), ('product_tag_id', '=', tag.id)], limit=1)
                if mapper.woo_id:
                    tag_id.append({'id': mapper.woo_id or None})
                else:
                    tag.export(self.backend)
                    mapper = tag.backend_mapping.search(
                        [('backend_id', '=', self.backend.id), ('product_tag_id', '=', tag.id)], limit=1)
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
            # images = [{"src": str(product.image).split("\'")[1:2] or None,
            images = [{"src": product.image.decode('utf-8') or None,
                       "name": product.name or None,
                       "position": 0,
                       'id': product_image_id or 0}]
        else :
            images = []

        if product.product_image_ids:
            for image in product.product_image_ids:
                mapper = image.backend_mapping.search([('backend_id', '=', self.backend.id),
                                                       ('product_image_id', '=', image.id)], limit=1)
                images.append({"src": image.image.decode('utf-8') or None,
                               "name": image.name or product.name + str(count),
                               "position": count,
                               'id': mapper.woo_id or 0})
                count += 1
        return images

    def get_custom_tabs(self, custom_tabs_ids):
        tab = []
        for tabs in custom_tabs_ids:
            if tabs.name:
                tab_id=re.sub(r'\s',r'-',tabs.name.lower())
                tab.append({'id':tab_id or None,
                            'title': tabs.name or None,
                            'content': tabs.description or None})
            else:
                tab.append({'id':tab_id or None,
                            'title': tabs.name or None,
                            'content': tabs.description or None})
        return tab

    def get_custom_charts(self, custom_chart_ids):
        tab = []
        for tabs in custom_chart_ids:
            if tabs.name:
                tab.append({'id':tabs.id or None,
                            'title': tabs.name.name or None,
                            'description': tabs.description or None,
                            'table': tabs.table or None,
                            'image_src': tabs.image.decode("utf-8") or None,
                            'image_name': tabs.name.name or None})
            else:
                tab.append({'id':tabs.id or None,
                            'title': tabs.name.name or None,
                            'description': tabs.description or None,
                            'table': tabs.table or None,
                            'image_src': tabs.image.decode("utf-8") or None,
                            'image_name': tabs.name.name or None})
        return tab

    def get_custom_review(self, custom_reviews_ids, prod_type, prod_template_id):
        review = []
        if len(custom_reviews_ids) <= 0 :
            custom_reviews_ids = http.request.env['product.review'].sudo().search([('product_type', '=', prod_type)])
            obj = http.request.env['product.template'].sudo().search([('id', '=', prod_template_id)])
            obj.write({
                'review_type_id': [(6, 0,custom_reviews_ids.ids)]
                })
            for reviews in custom_reviews_ids:
                if reviews.rating >= 1:
                    reviews.rating = 0
                review.append({'feature_name': reviews.name or None,
                           'feature_rate': reviews.rating})
            return review
        else:
            for reviews in custom_reviews_ids:
                review.append({'feature_name': reviews.name or None,
                           'feature_rate': reviews.rating})
            return review

    def get_attributes(self, product):
        """ get all attributes of product """
        attributes = []
        for attr in product.attribute_line_ids:
            attributes_value = []
            mapper = attr.attribute_id.backend_mapping.search(
                [('backend_id', '=', self.backend.id), ('attribute_id', '=', attr.attribute_id.id)], limit=1)
            if not mapper.woo_id:
                attr.attribute_id.export(self.backend)
                mapper = attr.attribute_id.backend_mapping.search(
                    [('backend_id', '=', self.backend.id), ('attribute_id', '=', attr.attribute_id.id)], limit=1)
            for value in attr.value_ids:
                val_mapper = value.backend_mapping.search(
                    [('backend_id', '=', self.backend.id), ('attribute_value_id', '=', value.id)], limit=1)
                if not val_mapper.woo_id:
                    value.export(self.backend)
                attributes_value.append(value.name)
            attributes.append({
                "id": mapper.woo_id or 0,
                "name": attr.attribute_id.name or None,
                "visible": attr.attribute_id.visible,
                "variation": attr.attribute_id.create_variant,
                "options": attributes_value,
            })
        return attributes

    def get_alternative_products(self, alternative_product_ids):
        alt_prod_ids = []
        for i , alt_prod_id in enumerate(alternative_product_ids):
            mapper = alt_prod_id.backend_mapping.search(
                [('backend_id', '=', self.backend.id), ('product_id', '=', alt_prod_id.id)], limit=1)
            if not mapper.woo_id:
                alt_prod_id.export(self.backend)
                mapper = alt_prod_id.backend_mapping.search(
                [('backend_id', '=', self.backend.id), ('product_id', '=', alt_prod_id.id)], limit=1)
            else:
                alt_prod_ids.append(mapper.woo_id or 0,)
        return alt_prod_ids

    def export_product(self, method, arguments):
        """ Export product data"""
        _logger.debug("Start calling Woocommerce api %s", method)
        details_model = arguments[1].details_model

        if arguments[1].product_variant_count > 1:
            product_type = "variable"
        else:
            product_type = "simple"

        if 'nadanew.vehicle.product' == arguments[1].details_model:
            sold_individually = True
        else:
            sold_individually = False
    

        regular_price = 0
        if arguments[1].regular_price and details_model == 'nadanew.vehicle.product':
            regular_price = arguments[1].regular_price
            if(regular_price == 0.0):
                regular_price = ""
            else:
                regular_price = str(regular_price)
        else:
            regular_price = arguments[1].regular_price
            if(regular_price == 0.0):
                regular_price = ""
            else:
                regular_price = str(regular_price)

        minap = arguments[1].minap
        if arguments[1].minap and details_model == 'nadanew.vehicle.product':
            minap = arguments[1].minap 

        start = None
        end = None
        if arguments[1].schedule_sale:
            start = arguments[1].schedule_date_start
            end = arguments[1].schedule_date_end

        if minap == 0.0:
            minap = ""
        if details_model == 'product.template.details':
            if arguments[1].details_model_record:
                if arguments[1].details_model_record.part_number:
                    part_number=arguments[1].details_model_record.part_number
            else:
                 part_number=""
        elif arguments[1].item_number:
            part_number=arguments[1].item_number
        else:
            part_number=""

        list_price=str(arguments[1].list_price)
        if product_type=='variable':
            list_price=None
            regular_price=None
        elif list_price == '0.0' and product_type=='simple' :
            list_price=None
        grouped=arguments[1].grouped
        d=[]
        if grouped:
            line=arguments[1].product_line
            for i in range(len(line)):
                mapper = line[i].product_id.backend_mapping.search([('backend_id', '=', arguments[1].backend_id.id), ('product_id', '=', line[i].product.product_tmpl_id.id)])
                d.append({'bundle_order':i,'product_id':mapper.woo_id,'bp_quantity':line[i].qty})
                product_type='yith_bundle'
        else:
            d=[]
        if 'vin' in arguments[1]:
            vin=arguments[1].vin
        else:
            vin=False
        if details_model == 'product.template.details':
            if arguments[1].details_model_record:
                if arguments[1].details_model_record.part_reference_number:
                    reference_number = arguments[1].details_model_record.part_reference_number
                else:
                    reference_number = ""
            else:
                reference_number = ""
        else:
            reference_number = ""


        if details_model == 'product.template.details':
            details_model = 'parts'

        result_dict = {
            'type': product_type,
            'name': arguments[1].name or None,
            'status': arguments[1].product_status or 'publish',
            'sku': arguments[1].default_code or None,
            'weight': str(arguments[1].weight) or None,
            # 'managing_stock': True,
            'stock_quantity': arguments[1].qty_available or None,
            'short_description': arguments[1].short_description or '',
            'description': arguments[1].description or '',
            'categories': self.get_category(arguments[1]),
            'attributes': self.get_attributes(arguments[1]),
            'images': self.get_images(arguments[1]) ,
            'tags': self.get_tag(arguments[1]),
            'tax_class':arguments[1].tax_class or "",
            'tax_status':arguments[1].tax_status or "",
            'dimensions': {'length': str(arguments[1].website_size_x) or "",
                           'width': str(arguments[1].website_size_y) or "",
                           'height': str(arguments[1].website_size_z) or "",
                           },
            'sale_price': list_price,
            'regular_price': regular_price,
            'product_type': details_model or None,
            '_minimum_advertised_price': minap,
            'motorcycle_image': [{
                "id" : arguments[1].backend_mapping.motorcycle_image_id or int(),
                "name" : arguments[1].name,
                "src": arguments[1].motorcycle_image or None,
                "position" : 0
            }],
            'enable_motorcycle_of_the_month': arguments[1].motorcycle_of_month or None,
            'custom_tabs': self.get_custom_tabs(arguments[1].custom_tabs_ids),
            'cross_sell_ids': self.get_alternative_products(arguments[1].alternative_product_ids),
            'custom_size_charts': self.get_custom_charts(arguments[1].custom_chart_ids),
            # 'video_link': arguments[1].details.video_url or None,
            'sold_individually': sold_individually or None,
            '_rewardsystemcheckboxvalue': arguments[1].product_rewards.rewardsystemcheckboxvalue or None,
            '_rewardsystem_options': arguments[1].product_rewards.rewardsystem_options or None,
            '_rewardsystempercent': arguments[1].product_rewards.rewardsystempercent or None,
            '_rewardsystempoints': arguments[1].product_rewards.rewardsystempoints or None,
            'part_number': part_number or None,
            'reference_number': reference_number or None,
            'date_on_sale_from': start or None,
            'date_on_sale_to': end or None,
            'cbpr_rating_features': self.get_custom_review(arguments[1].review_type_id,arguments[1].details_model,arguments[1].id),
            'job_code': arguments[1].job_code or None,
            'hours': arguments[1].hours or None,
            'job_description': arguments[1]. job_description or None,
            'charge_by': arguments[1].charge_by or None,
            'labor_rate': arguments[1].labor_rate or None,
            '_yith_wcpb_bundle_data':d or None,
            'vehicle_vin_no':vin or None,
            'cbpr_rating_type' : 5.00,
            # '_serial_numbers': self.get_lot_numbers(arguments[1]) or None,
            # 'customer_owned' : arguments[1].customer_owned,
            'enable_deposit' : arguments[1].enable_deposit,
            'type_of_deposit' : arguments[1].type_of_deposit or None,
            'deposit_amount' : arguments[1].deposit_amount or None,
        }
        if arguments[1].qty_available:
            result_dict['manage_stock'] = True
            result_dict['in_stock'] = True
            result_dict['stock_quantity'] = arguments[1].qty_available
        else:
            result_dict['manage_stock'] = True
            result_dict['in_stock'] = False
            result_dict['stock_quantity'] = arguments[1].qty_available

        if result_dict['name'] =='Setup Charges' or result_dict['name']=='Document Fees' or result_dict['name']=='Freight Charges':

            result_dict['manage_stock'] = False
            result_dict['stock_status']="onbackorder"
            result_dict['regular_price']=str(0)
            result_dict['in_stock'] = True
            if result_dict['description']=='Document Fees':
                result_dict['name']='Financing Charges'
            elif result_dict['name']=='Freight Charges':
                result_dict['name']='Manufacturer Charges'


        _logger.info("Odoo Product Export Data: %s",result_dict)

        res = self.export(method, result_dict, arguments) 
        if res:
            res_dict = res.json()
        else:
            res_dict = None
        return {'status': res.status_code, 'data': res_dict or {}}
