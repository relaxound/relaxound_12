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


class WpProductAttributeExport(WpImportExport):

    def get_api_method(self, method, args):
        """ get api for attribute and values"""
        api_method = None
        if method == 'attribute':
            if not args[0]:
                api_method = 'products/attributes/details'
            else:
                api_method = 'products/attributes/details/' + str(args[0])
        elif method == 'attribute_value':
            if not args[0]:
                api_method = 'products/attributes/' + \
                    str(args[2].woo_id) + '/terms/details'
            else:
                api_method = 'products/attributes/' + \
                    str(args[2].woo_id) + '/terms/details/' + str(args[0])
        return api_method

    def export_product_attribute(self, method, arguments):
        """ Export product attribute data"""
        _logger.debug("Start calling Woocommerce api %s", method)
        
        # add visible and variation here
        result_dict = {"name": arguments[1].name,
                       "type": "select",
                       "order_by": "menu_order",
                       "has_archives": True,
                       "visible":  arguments[1].visible,
                       "variation":  arguments[1].create_variant,
                       }
        _logger.debug("Export: %s", result_dict)
        res = self.export(method, result_dict, arguments)
        if res:
            res_dict = res.json()
        else:
            res_dict = res.json()
        return {'status': res.status_code, 'data': res_dict or {}}

    def export_product_attribute_value(self, method, arguments):
        """ Export product attribute value data"""
        _logger.debug("Start calling Woocommerce api %s", method)
        mail = arguments[1].env['stock.location'].search([('name','=',arguments[1].name)]).company_id.email
        ware = arguments[1].env['stock.location'].search([('name','=',arguments[1].name)]).company_id
        ware_city = arguments[1].env['stock.warehouse'].search([('company_id','=',ware.id)]).name
        ware_address = arguments[1].env['stock.warehouse'].search([('company_id','=',ware.id)]).physical_address
        # image = arguments[1].env['stock.location'].search([('name','=',arguments[1].name)]).company_id.logo
        zip_code = arguments[1].env['stock.location'].search([('name','=',arguments[1].name)]).company_id.zip
        phone = arguments[1].env['stock.location'].search([('name','=',arguments[1].name)]).company_id.phone

        result_dict = {"name": arguments[1].name,
                       "city" : ware_city,
                       "store_location": ware_address,
                       "zip_code": zip_code,
                       "store_email": mail,
                       # "image": image.decode('utf-8'),
                       "store_hours":{
                           "Monday": "Closed",
                           "Tuesday": "10am- 6pm",
                           "Wednesday": "10am- 6pm",
                           "Thursday": "10am- 6pm",
                           "Friday": "10am- 6pm",
                           "Saturday": "10am- 5pm",
                           "Sunday": "Closed"
                        },
                       "phone_number": phone
                    }
        res = self.export(method, result_dict, arguments)
        if res:
            res_dict = res.json()
        else:
            res_dict = res.json()
        return {'status': res.status_code, 'data': res_dict or {}}
