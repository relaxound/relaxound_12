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


class WpCrmLeadImport(WpImportExport):

    def get_api_method(self, method, args, count=None, date=None):
        """ get api for crm lead status"""
        api_method = None
        print(args[0])
        if method == 'my_import_form':
            if not args[0]:
                api_method = 'my_form/details'
            else:
                api_method = 'my_form/details/' + str(args[0])

        return api_method

    def import_crm_lead(self, method, arguments):
        """ Export crm lead status"""
        _logger.debug("Start calling Woocommerce api %s", method)
        result = {}

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

    def write_form(self,backend,mapper,res,partner_id,major_unit_id):
        bkend_id = mapper.backend_id.search([('id','=',backend.id)])
        temp=res['data']['form_name'].lower()
        if 'valid_driver_license' in res['data'].keys():
            valid_driver_license=res['data']['valid_driver_license']
        else:
            valid_driver_license=None

        if 'valid_insurance' in res['data'].keys():
            valid_insurance=res['data']['valid_insurance']
        else:
            valid_insurance=None
        vals={
        'name' : res['data']['ride_name'],
        'backend_id' : [[4,bkend_id.id,bkend_id]],
        'first_name' : res['data']['first_name'],
        'last_name' : res['data']['last_name'],
        'planned_revenue' : 0.0,
        'probability' : 0.0,
        'major_unit_id' : major_unit_id.id or None,
        'form_type' : temp or None,
        'partner_id' : partner_id.id or None,
        'email_from' : res['data']['email_id'] or None,
        'phone' : res['data']['phone_number'] or None,
        'next_activity_id' : None,
        'partner_name' : res['data']['agreement_full_name'] or None,
        'location_att' : res['data']['user_city_location'] or None,
        'street' : res['data']['address1'] or None,
        'first_name' : res['data']['first_name'] or None,
        'last_name' : res['data']['last_name'] or None,
        # 'test_ride_date' : res['data']['test_ride_date'] or None,
        # 'test_ride_time' : res['data']['test_ride_time'] or None,
        # 'date_of_birth' : res['data']['date_of_birth'] or None,
        'contact_name' : res['data']['agreement_full_name'] or None,
        'mobile' : res['data']['phone_number'] or None,
        'fax' :  None,
        'opt_out' : None,
        'campaign_id' :  None,
        'source_id' : None,
        # 'day_open' : res['data']['form_submission_date'] or None,
        'reffered' : None,
        'credit_card_type' :res['data']['card_type'] or None,
        'card_number' : res['data']['card_number'] or None,
        'name_on_card' : res['data']['name_on_card'] or None,
        'month' :res['data']['expiry_month'] or None,
        'year_deposite' :res['data']['expiry_year'] or None,
        'cvv' : res['data']['card_cvv'] or None,
        'valid_driver_license':valid_driver_license,
        'valid_insurance':valid_insurance,
        'attach_img':res['data']['trade_in_images']  or None,
        

        }
        _logger.info(vals)
        mapper.crm_lead_id.write(vals) 

    def create_form(self,backend,mapper,res,partner_id,major_unit_id):
        bkend_id = mapper.backend_id.search([('id','=',backend.id)])
        if 'valid_driver_license' in res['data'].keys():
            valid_driver_license=res['data']['valid_driver_license']
        else:
            valid_driver_license=None

        if 'valid_insurance' in res['data'].keys():
            valid_insurance=res['data']['valid_insurance']
        else:
            valid_insurance=None,
        temp=res['data']['form_name'].lower()
        vals={
        'name' : res['data']['ride_name'],
        'backend_id' : [[4,bkend_id.id,bkend_id]],
        'first_name' : res['data']['first_name'],
        'last_name' : res['data']['last_name'],
        'planned_revenue' : None,
        'probability' : None,
        'major_unit_id' : major_unit_id.id or None,
        'form_type' : temp or None,
        'partner_id' : partner_id.id or None,
        'email_from' : res['data']['email_id'] or None,
        'phone' : res['data']['phone_number'] or None,
        'next_activity_id' : None,
        'partner_name' : res['data']['agreement_full_name'] or None,
        'location_att' : res['data']['user_city_location'] or None,
        'street' : res['data']['address1'] or None,
        'first_name' : res['data']['first_name'] or None,
        'last_name' : res['data']['last_name'] or None,
        # 'test_ride_date' : res['data']['test_ride_date'] or None,
        # 'test_ride_time' : res['data']['test_ride_time'] or None,
        # 'date_of_birth' : res['data']['date_of_birth'] or None,
        'contact_name' : res['data']['agreement_full_name'] or None,
        'mobile' : res['data']['phone_number'] or None,
        'fax' :  None,
        'opt_out' : None,
        'campaign_id' :  None,
        'source_id' : None,
        # 'day_open' : res['data']['form_submission_date'] or None,
        'reffered' : None,
        'credit_card_type' :res['data']['card_type'] or None,
        'card_number' : res['data']['card_number'] or None,
        'name_on_card' : res['data']['name_on_card'] or None,
        'month' :res['data']['expiry_month'] or None,
        'year_deposite' :res['data']['expiry_year'] or None,
        'cvv' : res['data']['card_cvv'] or None, 
        'valid_driver_license':valid_driver_license,
        'valid_insurance': valid_insurance,
        'attach_img':res['data']['trade_in_images']  or None,
        }

        _logger.info(vals)
        res_partner = mapper.crm_lead_id.create(vals)
        return res_partner