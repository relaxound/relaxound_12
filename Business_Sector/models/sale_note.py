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
                self.update({'note': "your contact person is Mirjam Swart\nPhone: 0031 6 36429052\nE-Mail: mirjam@designlicious.nl"})

        elif self.partner_id.agent_name == 'The Living Connection':
                self.update({'note': "your contact person is Thijs van de Laak and Anne Vendrig\nPhone: 0034 673 820 269\nE-Mail: anne@thelivingconnection.com"})
        else:
                self.update({'note' :"Bitte beachten Sie, dass wir bei nicht vereinbartem Skontoabzug oder Kürzung des Rechnungsbetrages eine Bearbeitungsgebühr von 10 EUR erheben müssen."})