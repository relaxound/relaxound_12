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
from odoo.exceptions import Warning


_logger = logging.getLogger(__name__)


class WpCustomerExport(WpImportExport):

    """ Models for woocommerce customer export """

    def get_api_method(self, method, args):
        """ get api for customer"""
        api_method = None
        if method == 'customer':
            if not args[0]:
                api_method = 'customers'
            else:
                api_method = 'customers/' + str(args[0])
        return api_method


    def get_shipping_address(self, child_ids):
        """ return shipping address customer """
        shipping = []
        if child_ids:
            for shipping_id in child_ids:
                if shipping_id.type == 'contact':
                    shipping.append({
                        "type": shipping_id.type or None,
                        "name": shipping_id.name or None,
                        "email": shipping_id.email or None,
                        "phone": shipping_id.phone or None,
                        "mobile": shipping_id.mobile or None,
                        "notes": shipping_id.comment or None,
                    })

                elif shipping_id.type == 'invoice' or shipping_id.type == 'delivery' or shipping_id.type == 'other':
                    shipping.append({
                        "type": shipping_id.type or '',
                        "name": shipping_id.name or '',
                        "email": shipping_id.email or '',
                        "address_1": shipping_id.street or '',
                        "address_2": shipping_id.street2 or '',
                        "city": shipping_id.city or '',
                        "state": shipping_id.state_id.code or '',
                        "postcode": shipping_id.zip or '',
                        "country": shipping_id.country_id.code or '',
                        "phone": shipping_id.phone or '',
                        "mobile": shipping_id.mobile or '',
                        "notes": shipping_id.comment or '',
                    })
        return shipping


    def export_customer(self, method, arguments):
        """ Export customer data"""
        _logger.debug("Start calling Woocommerce api %s", method)

        if arguments[1].company_type == 'company':
            company = arguments[1].name
        else:
            company = None

        result_dict = {
            "email": arguments[1].email or '',
            "first_name": arguments[1].first_name or arguments[1].name or '',
            "last_name": arguments[1].last_name or '',
            "username": arguments[1].username or '',
            "password": arguments[1].password or 'None',
            "company": company or None,
            "shipping": {"first_name": arguments[1].first_name or arguments[1].name or '',
                        "last_name": arguments[1].last_name or '',
                        "company": arguments[1].company or '',
                        "address_1": arguments[1].street or '',
                        "address_2": arguments[1].street2 or '',
                        "city": arguments[1].city or '',
                        "state": arguments[1].state_id.code or '',
                        "postcode": arguments[1].zip or '',
                        "country": arguments[1].country_id.code or '',
                        "email": arguments[1].email or '',
                        "phone": arguments[1].phone or '',
                        },
            "billing": {"first_name": arguments[1].first_name or arguments[1].name or '',
                        "last_name": arguments[1].last_name or '',
                        "company": arguments[1].company or '',
                        "address_1": arguments[1].street or '',
                        "address_2": arguments[1].street2 or '',
                        "city": arguments[1].city or '',
                        "state": arguments[1].state_id.code or '',
                        "postcode": arguments[1].zip or '',
                        "country": arguments[1].country_id.code or '',
                        "email": arguments[1].email or '',
                        "phone": arguments[1].phone or '',
                        },
        }

        r = self.export(method, result_dict, arguments)

        return {'status': r.status_code, 'data': r.json()}

