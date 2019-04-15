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


class WpCategoryExport(WpImportExport):

    def get_api_method(self, method, args):
        """ get api for category and values"""
        api_method = None
        if method == 'category':
            if not args[0]:
                api_method = 'products/categories/details'
            else:
                api_method = 'products/categories/details/' + str(args[0])
        return api_method

    def export_product_category(self, method, arguments):
        """ Export product category data"""
        _logger.debug("Start calling Woocommerce api %s", method)
        if arguments[1].parent_id:
            mapper = arguments[1].parent_id.backend_mapping.search(
                [('backend_id', '=', self.backend.id), ('category_id', '=', arguments[1].parent_id.id)], limit=1)
            parent = mapper.woo_id or None
            if not parent:
                res = self.export_product_category(
                    method, [None, arguments[1].parent_id])
                if res['status'] == 201 or res['status'] == 200:
                    arguments[1].parent_id.write({'slug': res['data']['slug']})
                    if res['data']['image']:
                        image_id = res['data']['image']['id']
                    else:
                        image_id = None
                    if mapper:
                        mapper.write({'category_id': arguments[1].parent_id.id, 'backend_id': self.backend.id, 'woo_id': res[
                                     'data']['id'], 'image_id': image_id})
                    if mapper:
                        mapper.create({'category_id': arguments[
                                      1].parent_id.id, 'backend_id': self.backend.id, 'woo_id': res['data']['id'], 'image_id': image_id})

                    parent = arguments[1].parent_id.woo_id
        else:
            parent = 0

        mapper = arguments[1].backend_mapping.search(
            [('backend_id', '=', self.backend.id),
             ('category_id', '=', arguments[1].id)],
            limit=1)

        image_dict = {}
        if mapper.image_id:
            image_dict['id'] = mapper.image_id
            image_dict['src'] = arguments[1].image or None
        else:
            image_dict=None

        result_dict = {
            'name': arguments[1].name,
            'image': image_dict,
            'desc': arguments[1].desc or None,
        }
        if parent != 0:
            result_dict.update({'parent': parent, })
        if arguments[1].slug:
            result_dict.update({'slug': arguments[1].slug or None})
        _logger.info(result_dict)
        res = self.export(method, result_dict, arguments)
        if res:
            res_dict = res.json()
        else:
            res_dict = res.json()
        return {'status': res.status_code, 'data': res_dict or {}}
