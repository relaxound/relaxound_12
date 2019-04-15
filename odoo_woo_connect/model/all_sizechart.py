
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

# import xmlrpclib
from collections import defaultdict
from odoo.addons.queue_job.job import job
import base64
from odoo import models, fields, api, _
# from ..unit.product_exporter import WpProductExport
from ..unit.sizechart_exporter import WpSizeChart
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class SizeChart(models.Model):

    _inherit = "all.sizechart"

    backend_mapping = fields.One2many(comodel_name='wordpress.odoo.sizechart',
                                  string='Size chart mapping',
                                  inverse_name='sizechart_id',
                                  readonly=False,
                                  required=False,)

    @api.multi
    def sync_size_chart(self):
        for backend in self.backend_id:
            self.with_delay().export(backend)
        return

    @api.multi
    @job
    def export(self, backend):
        if len(self.ids)>1:
            for obj in self:
                obj.with_delay().export(backend)
            return
        method = 'coupon'
        mapper = self.backend_mapping.search(
            [('backend_id', '=', backend.id), ('sizechart_id', '=', self.id)], limit=1)
        export = WpSizeChart(backend)
        arguments = [mapper.woo_id or None, self]
        res = export.export_size_chart(method, arguments)
        if mapper and (res['status'] == 200 or res['status'] == 201):
            mapper.write(
                {'sizechart_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['id']})
        elif (res['status'] == 200 or res['status'] == 201):
            self.backend_mapping.create(
                {'sizechart_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['id']})
        elif (res['status'] == 400 and res['data']['code'] == 'woocommerce_rest_size_chart_already_exists'):
            if 'resource_id' in res['data']['data'].keys():
                self.backend_mapping.create(
                    {'sizechart_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['data']['resource_id']})


class SizeChartMapping(models.Model):

    _name = 'wordpress.odoo.sizechart'
    sizechart_id = fields.Many2one(comodel_name='all.sizechart',
                                        string='Size Chart',
                                        ondelete='cascade',
                                        readonly=False,
                                        required=True,)

    backend_id = fields.Many2one(comodel_name='wordpress.configure',
                                 string='Website',
                                 ondelete='set null',
                                 store=True,
                                 readonly=False,
                                 required=False,)

    woo_id = fields.Char(string='Woo id')