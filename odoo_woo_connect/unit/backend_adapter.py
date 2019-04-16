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

    def export(self, method, result_dict, arguments):
        """ Export all data to woo commerce"""
        api = API(url=self.location,
                  consumer_key=self.consumer_key,
                  consumer_secret=self.consumer_secret,
                  version="wc/v2",
                  wp_api=True,
                  timeout=100,
                  )

        res = api.post(self.get_api_method(method, arguments), result_dict)
        _logger.info(
            "Export to api %s, status : %s res : %s", self.get_api_method(method, arguments), res.status_code, res.text)
        return res
