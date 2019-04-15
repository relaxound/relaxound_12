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


class WpProductDealImport(WpImportExport):

    """ Models for woocommerce product deals import"""

    def get_api_method(self, method, args, date=None, count=None):
        """ get api for product_deals"""
        api_method = None
        if method == 'campaign':
            if not args[0]:
                api_method = 'campaign/details'
            else:
                api_method = 'campaign/details/' + str(args[0])
        return api_method

    def import_product_deals(self, method, arguments):
        """ Import product_deals data"""
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

    def create_product_deals(self,backend,mapper,res):
        pass

    def write_product_deals(self,backend,mapper,res):
        pass