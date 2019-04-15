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

from odoo import api
import logging
from ..model.api import API
from datetime import datetime
from datetime import timedelta
from ..unit.backend_adapter import WpImportExport
_logger = logging.getLogger(__name__)


class WpMajorUnitImport(WpImportExport):

    """ Models for woocommerce customer export """

    def get_api_method(self, method, args, date=None, count=None):
        """ get api for major_unit"""
        api_method = None
        if method == 'my_rides':
            if not args[0]:
                api_method = 'my_rides/details'
            else:
                api_method = 'my_rides/details/' + str(args[0])
        return api_method

    def import_major_unit(self, method, arguments):
        """ Import major_unit data"""
        _logger.debug("Start calling Woocommerce api %s", method)
        res = self.importer(method, arguments)
        try:
            if 'false' or 'true' or 'null'in res.content:
                result = res.content.decode('utf-8')
                result=result.replace(
                    'false', 'False')
                result = result.replace('true', 'True')
                result = result.replace('null', 'False')
                result = eval(result)
            else:
                result = eval(res.content)
        except:
            _logger.error("api.call(%s, %s) failed", method, arguments)
            raise
        else:
            _logger.debug("api.call(%s, %s) returned %s ",
                          method, arguments, result)

        return {'status': res.status_code, 'data': result or {}}

    def create_major_unit(self, backend, mapper, res, partner_id):
        if res['data']['ride_details']:
            product_name = res['data']['ride_details']['cr_ride_name']
            check_product = mapper.majorunit_id.prod_lot_id.product_id.search([('name','=',product_name)])
            if not check_product:
            	prod_vals = {
            		'name' : product_name
            	}
            	product_id = mapper.majorunit_id.prod_lot_id.product_id.create(prod_vals)
            else:
            	product_id = check_product[0]

            prod_lot_vals = {
            	'product_id' : product_id.id
            }
            prod_lot_id = mapper.majorunit_id.prod_lot_id.create(prod_lot_vals)
            vals = {
                'mileage': res['data']['ride_details']['cr_mileage'],
                'make': res['data']['ride_details']['cr_make'],
                'year': res['data']['ride_details']['cr_year'],
                'model': res['data']['ride_details']['cr_model'],
                'product_name': res['data']['ride_details']['cr_ride_name'],
                'prod_lot_id' : prod_lot_id.id,
                'backend_id' : [[6,0,[backend.id]]],
                'location_id': mapper.env.ref('stock.stock_location_customers').id,
            }
            if partner_id:
                vals['partner_id'] = partner_id[0].customer_id.id
            major_unit = mapper.majorunit_id.create(vals)
            return major_unit

    def write_major_unit(self, backend, mapper, res, partner_id):
        vals = {
            'mileage': res['data']['ride_details']['cr_mileage'],
            'make': res['data']['ride_details']['cr_make'],
            'year': res['data']['ride_details']['cr_year'],
            'model': res['data']['ride_details']['cr_model'],
            'product_name': res['data']['ride_details']['cr_ride_name'],
            'vin_sn': res['data']['ride_details']['cr_vin'],
            'backend_id': [[6,0,[backend.id]]],
            'prod_lot_id': mapper.majorunit_id.prod_lot_id.id,
        }
        if partner_id:
            vals['partner_id'] = partner_id[0].customer_id.id
        mapper.majorunit_id.write(vals)