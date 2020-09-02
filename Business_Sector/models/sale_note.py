# -*- coding: utf-8 -*-
# Copyright 2016-TODAY Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, api


class defaultnote(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def onchange_partner_id_sale_agent(self):

        if self.partner_id.agent_name == 'Rossmanek':

                self.update({'note': "Sie werden betreut durch die Handelsagentur Rossmanek\nKontakt: Ole Roßmanek, Timms Hoff 7, 22941 Delingsdorf\nE-Mail: info@agentur-rossmanek.de"})

        elif self.partner_id.agent_name == 'Pforte':
                self.update({'note': "Sie werden betreut durch die Agentur Pforte\nKontakt: Agentur Pforte, Sibeliusstraße 3, 30989 Gehrden\nE-Mail: gunther.pforte@t-online.de"})

        elif self.partner_id.agent_name == 'Senft':
                self.update({'note': "Sie werden betreut durch die Handelsagentur Senft\nKontakt: Christian Senft, Am Rheinberg 19, 55411 Bingen\nE-Mail: info@cs-handelsagentur.de"})

        elif self.partner_id.agent_name == 'Wirtz':
                self.update({'note': "Sie werden betreut durch die Agentur Wirtz\nKontakt: Agentur Wirtz, Tannenweg 23, 41363 Jüchen\nE-Mail: agenturwirtz@t-online.de"})

        elif self.partner_id.agent_name == 'Kuhnle':
                self.update({'note': "Sie werden betreut durch die Agentur Kuhnle\nKontakt: Agentur Kuhnle, Bonwiedenweg 18, 73312 Türkheim\nE-Mail: s.kuhnle@t-online.de"})

        elif self.partner_id.agent_name == 'Werner':
                self.update({'note': "Sie werden betreut durch die Handelsagentur BUCH + RAUM\nKontakt: Thomas Werner, Tulpenweg 9, 83254 Breitbrunn am Chiemsee\nE-Mail: werner@buch-raum.de"})

        elif self.partner_id.agent_name == 'DEsignLICIOUS':
                self.update({'note': "For any concerns you are welcome to contact your sales agency DEsignLICIOUS\nContact: Mirjam Swart\nE-Mail: mirjam@designlicious.nl\nPhone: (+31) 6 36429052"})

        elif self.partner_id.agent_name == 'The Living Connection':
                self.update({'note': "For any concerns you are welcome to contact your sales agency\nThe Living Connection\nContact: Thijs & Anne van de Laak\nE-Mail: anne@thelivingconnection.com\nPhone: 0034 673 820 269"})

        elif self.partner_id.agent_name == 'Handelsagentur Schur GbR':
                self.update({'note': "Ihr persönlicher Ansprechpartner: Handelsagentur Schur GbR\nKontakt: Wolfgang Schur, Johann-Ziegler-Str. 14c, 85221 Dachau\nTel. 08131 333 26 37\nE-Mail: info@ha-schur.com"})

        else:
                self.update({'note' :"Bitte beachten Sie, dass wir bei nicht vereinbartem Skontoabzug oder Kürzung des Rechnungsbetrages eine Bearbeitungsgebühr von 10 EUR erheben müssen."})

