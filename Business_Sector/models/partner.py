# -*- coding: utf-8 -*-
# Copyright 2016-TODAY Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
import csv

class BusinessSector(models.Model):

        _inherit = 'res.partner'

        # Added one field Business sector with dropdown
        
        business_sec = fields.Selection([
                ('sec1', 'Beauty / Wellness'),
                ('sec2', 'Books'), 
                ('sec3', 'Gardening'),
                ('sec4', 'Gastronomy'),
                ('sec5', 'Art / Culture'),
                ('sec6', 'Home Living'),
                ('sec7', 'Misc'),
                ('sec8', 'GPC'),
                ('sec9', 'retail store'),], string='Business Sector:')

        agent_name = fields.Char('Sales Agent')


        @api.onchange('zip', 'category_id','country_id')
        def onchange_zip(self):
                ids = self.category_id
                tag_name = []
                for id in ids:
                    tag_name.append(id.name)

                if self.zip != None and self.zip != '' and 'Händler' in tag_name and self.country_id.code=='DE':
                        with open('src/user/zip_code.csv', 'r') as csv_file:
                                csv_obj = csv.reader(csv_file)
                                print("#### CSV OPENED #########")
                                all_val = [i for i in csv_obj]
                                val = [(i[0], i[1]) for i in all_val]
                                for v in val:
                                        if self.zip in v:
                                                self.update({'agent_name': v[1]})
                                                break
                                        else:
                                                self.update({'agent_name': None})

                elif 'Händler' in tag_name and self.country_id.code in ['NL','BE','LU']:
                        self.update({'agent_name': 'DEsignLICIOUS'})

                elif 'Händler' in tag_name and self.country_id.code == 'ES':
                        self.update({'agent_name': 'The Living Connection'})

                elif 'Händler' in tag_name and self.country_id.code == 'AT':
                        self.update({'agent_name': 'Handelsagentur Schur GbR'})

                else:
                        self.update({'agent_name': None})