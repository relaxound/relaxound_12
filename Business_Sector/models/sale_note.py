# -*- coding: utf-8 -*-
# Copyright 2016-TODAY Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, api


class defaultnote(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def onchange_partner_id_sale_agent(self):

        if self.partner_id.agent_name == 'Rossmanek':

                self.update({'note': "Sie werden betreut durch die Handelsagentur Rossmanek Kontakt: Ole Roßmanek, Timms Hoff 7, 22941 Delingsdorf info@agentur-rossmanek.de"})

        elif self.partner_id.agent_name == 'Pforte':
                self.update({'note': "Sie werden betreut durch die Agentur Pforte Kontakt: Agentur Pforte, Sibeliusstraße 3, 30989 Gehrden E-Mail: gunther.pforte@t-online.de"})

        elif self.partner_id.agent_name == 'Senft':
                self.update({'note': "Sie werden betreut durch die Handelsagentur Senft Kontakt: Christian Senft, Am Rheinberg 19, 55411 Bingen E-Mail: info@cs-handelsagentur.de"})

        elif self.partner_id.agent_name == 'Wirtz':
                self.update({'note': "Sie werden betreut durch die Agentur Wirtz Kontakt: Agentur Wirtz, Tannenweg 23, 41363 Jüchen agenturwirtz@t-online.de"})

        elif self.partner_id.agent_name == 'Kuhnle':
                self.update({'note': "Sie werden betreut durch die Agentur Kuhnle Kontakt: Agentur Kuhnle, Bonwiedenweg 18, 73312 Türkheim s.kuhnle@t-online.de"})

        elif self.partner_id.agent_name == 'Werner':
                self.update({'note': "Sie werden betreut durch die Handelsagentur BUCH + RAUM Kontakt: Thomas Werner, Sonnhart 78, 83131 Nußdorf am Inn werner@buch-raum.de"})

        else:
                self.update({'note' :"Bitte beachten Sie, dass wir bei nicht vereinbartem Skontoabzug oder Kürzung des Rechnungsbetrages eine Bearbeitungsgebühr von 10 EUR erheben müssen."})
