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
_logger = logging.getLogger(__name__)


class WpImportExport(object):

    """ Models for woocommerce export import """

    def __init__(self, backend):
        """ Initialized all variables """
        self.backend = backend
        self.location = backend.location
        self.consumer_key = backend.consumer_key
        self.consumer_secret = backend.consumer_secret
        self.version = backend.version

    # def get_api_method(self, method, args):
    #     api_method = None

    #     if method == 'refunds':
    #         if not args[0]:
    #             api_method = 'orders/<id>/refunds'
    #         else :
    #             api_method = 'orders/<id>/refunds' + str(args[0])

    #     return api_method

    def importer(self, method, arguments, count=None, date=None):
        """ Import all data to woo commerce"""
        api = API(url=self.location,
                  consumer_key=self.consumer_key,
                  consumer_secret=self.consumer_secret,
                  version=self.version,
                  wp_api=True,
                  timeout=100)

        res = api.get(self.get_api_method(method, arguments, count, date))
        if not res.status_code in [200, 201]:
            status = 'failed'
        else:
            status = 'done'
        arguments[1].env['wordpress.jobs'].create({'api_data': str(self.get_api_method(method, arguments, count, date)),
                                                   'name': 'Import ' + method,
                                                   'request': '',
                                                   'response': res.text,
                                                   'module': str(arguments[1].__class__)[17:-2],
                                                   'module_object_id': '',
                                                   'backend_id': self.backend.id,
                                                   'state': status})
        arguments[1].env.cr.commit()
        _logger.info(
            "Import to api %s, status : %s res : %s", self.get_api_method(method, arguments, count, date), res.status_code, res.text)
        return res

    def export(self, method, result_dict, arguments):
        """ Export all data to woo commerce"""
        api = API(url=self.location,
                  consumer_key=self.consumer_key,
                  consumer_secret=self.consumer_secret,
                  version=self.version,
                  wp_api=True,
                  timeout=2000)

        res = api.post(self.get_api_method(method, arguments), result_dict)
        if not res.status_code in [200, 201]:
            status = 'failed'
        else:
            status = 'done'
        arguments[1].env['wordpress.jobs'].create({'api_data': str(self.get_api_method(method, arguments)),
                                                   'name': 'Export ' + arguments[1].name,
                                                   'request': str(result_dict),
                                                   'response': res.text,
                                                   'module': str(arguments[1].__class__)[17:-2],
                                                   'module_object_id': arguments[1].ids[0],
                                                   'backend_id': self.backend.id,
                                                   'state': status})
        arguments[1].env.cr.commit()
        _logger.info(
            "Export to api %s, status : %s res : %s", self.get_api_method(method, arguments), res.status_code, res.text)
        return res



    def run_campaign(self, method, result_dict):
        """ Export all data to woo commerce"""
        api = API(url=self.location,
                  consumer_key=self.consumer_key,
                  consumer_secret=self.consumer_secret,
                  version=self.version,
                  wp_api=True,
                  timeout=1000)

        res = api.post('campaign/details', result_dict)
        if not res.status_code in [200, 201]:
            status = 'failed'
        else:
            status = 'done'

        _logger.info(
          "Export to api %s, status : %s res : %s", 'campaign/details', res.status_code, res.text)
        return res