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

from odoo import models, api, fields


class wp_jobs(models.Model):
    _name = "wordpress.jobs"
    _description = 'WooCommerce Backend Jobs'

    uuid = fields.Char(string='UUID',
                       readonly=True,
                       select=True,
                       required=True)

    state = fields.Selection([(PENDING, 'Pending'),
                              (ENQUEUED, 'Enqueued'),
                              (STARTED, 'Started'),
                              (DONE, 'Done'),
                              (FAILED, 'Failed')], 	string='State',
                             readonly=True,
                             required=True,
                             select=True)

    name = fields.Char(string='Description', readonly=True)
    func_name = fields.Char(string='Task', readonly=True)
    func_args = fields.Many2many(comodel_name='wordpress.jobs.args',
                                 string='Args')


class wp_jobs_args(models.Model):
    _name = "wordpress.jobs.args"
    _description = 'WooCommerce Backend Jobs Arguments'

    value = fields.Char(string='Description', readonly=True)
