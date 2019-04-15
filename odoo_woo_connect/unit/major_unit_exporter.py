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
from ..unit.product_exporter import WpProductExport
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class WpMajorUnitExport(WpImportExport):

    """ Models for woocommerce customer export """

    def get_api_method(self, method, args):
        """ get api for customer"""

        api_method = None
        if method == 'my_rides':
            if not args[0]:
                api_method = 'my_rides/details'
            else:
                api_method = 'my_rides/details/' + str(args[0])
        else:
            api_method=method
        return api_method

    def export_major_unit(self, method, arguments):
        """ Export customer data"""

        _logger.debug("Start calling Woocommerce api %s", method)

        customer_woo_ids = []
        if arguments[1].partner_id:
            for customer_id in arguments[1].partner_id:
                mapper = customer_id.backend_mapping.search(
                    [('backend_id', '=', self.backend.id), ('customer_id', '=', customer_id.id)])
                if mapper.woo_id:
                    customer_woo_ids.append(mapper.woo_id)
                else:
                    customer_id.export(self.backend)
                    mapper = customer_id.backend_mapping.search(
                        [('backend_id', '=', self.backend.id), ('customer_id', '=', customer_id.id)])
                    if mapper.woo_id:
                        customer_woo_ids.append(mapper.woo_id)
            cr_make = None
            cr_year = None
            cr_type = None
            cr_model = None
            if arguments[1]:
                for major in arguments[1].attribute_value_ids:
                    if major.attribute_id.name.lower() == 'make':
                        cr_make = major.name
                    elif major.attribute_id.name.lower() == 'year' or major.attribute_id.name.lower() == 'years':
                        cr_year = major.name
                    elif major.attribute_id.name.lower() == 'model':
                        cr_model = major.name
                    elif major.attribute_id.name.lower() == 'type':
                        cr_type = major.name
           
            if not customer_woo_ids:
                raise UserError("Please check customer's details")

            result_dict = {
                "cr_customer_id": customer_woo_ids[0] or None,
                "cr_ride_name": arguments[1].name or None,
                "cr_year": cr_year or None,
                "cr_make": cr_make or None,
                "cr_model": cr_model or None,
                "cr_type": cr_type or 'type',
                "cr_mileage": arguments[1].mileage or None,
                # "cr_rides_img_url":arguments[1].image or None,
                "cr_vin": arguments[1].vin_sn[5:] or None,
                "cr_purchase_date": arguments[1].purchase_date,
                "cr_store": arguments[1].cr_store_id.name or None,
                "cr_sales_adviser": arguments[1].cr_sales_adviser or None,
                "cr_form_status": arguments[1].form or None
            }
            res = self.export(method, result_dict, arguments)
            _logger.info("Odoo major unit Export Data: %s",res.json())
            return {'status': res.status_code, 'data': res.json()}