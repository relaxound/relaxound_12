# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Agile Business Group (http://www.agilebg.com)
#    @author Lorenzo Battistini <lorenzo.battistini@agilebg.com>
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
##############################################################################

from odoo import models, api


class BetterZipGeonamesImport(models.TransientModel):
    _inherit = 'better.zip.geonames.import'

    @api.model
    def select_or_create_state(
        self, row, country_id, code_row_index=4, name_row_index=3
    ):
        return super(BetterZipGeonamesImport, self).select_or_create_state(
            row, country_id, code_row_index=6, name_row_index=5)
    def setUp(self):
        super(BetterZipGeonamesImport, self).setUp()
        self.country = self.env.ref('base.mc')
        self.wizard = self.env['better.zip.geonames.import'].create({
            'country_id': self.country.id,
        })

    def test_import_country(self):
        self.wizard.with_context(max_import=10).run_import()
        state_domain = [
            ('code', '=', '01'),
            ('country_id', '=', self.country.id)
        ]
        states = self.env['res.country.state'].search(state_domain)
        self.assertEqual(len(states), 1)
        zip_domain = [
            ('name', '=', '98000'),
            ('city', '=', 'Ciappaira'),
            ('state_id', '=', states[0].id),
            ('country_id', '=', self.country.id),
        ]
        zips = self.env['res.better.zip'].search(zip_domain)
        self.assertEqual(len(zips), 1)
        # Reimport again to see that there's no duplicates
        self.wizard.with_context(max_import=10).run_import()
        states = self.env['res.country.state'].search(state_domain)
        self.assertEqual(len(states), 1)
        zips = self.env['res.better.zip'].search(zip_domain)
        self.assertEqual(len(zips), 1)

    def test_delete_old_entries(self):
        zip_entry = self.env['res.better.zip'].create({
            'city': 'Test city',
            'country_id': self.country.id,
        })
        self.wizard.run_import()
        self.assertFalse(zip_entry.exists())