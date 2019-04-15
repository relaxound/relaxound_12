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


class WpCrmLeadExport(WpImportExport):

    def get_api_method(self, method, args):
        """ get api for crm lead status"""
       
        api_method = None
        print(args[0])
        if method == 'crm_lead_status':
            if args[0]:
                api_method = 'my_form/details/' + str(args[0])

        return api_method

    def export_crm_lead(self, method, arguments):
        """ Export crm lead status"""
        _logger.debug("Start calling Woocommerce api %s", method)
        res_dict = {}
        if(arguments[1].lost_reason):
            status = 'Denied'
        else:
            status = arguments[1].stage_id.name
            if(status=='New'):
                status = 'In Process'
            elif(status=='Won'):
                status = 'Completed'

        result_dict = {
            'form_status': status,
        }
        _logger.info("Exporting status of the Form.....%s",status)
        res = self.export(method, result_dict, arguments)
        if res:
            res_dict = res.json()
        else:
            res_dict = None
        return {'status': res.status_code, 'data':res_dict or {}}