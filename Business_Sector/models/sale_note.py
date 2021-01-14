# -*- coding: utf-8 -*-
# Copyright 2016-TODAY Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, api


class defaultnote(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def onchange_partner_id_sale_agent(self):

        # import pdb;
        # pdb.set_trace()
        if self.partner_id.agent_name == 'Rossmanek':
            self.update({'note': "Ihr persönlicher Ansprechpartner: Handelsagentur Rossmanek\nKontakt: Ole Roßmanek, Timms Hoff 7, 22941 Delingsdorf\nTel. 04532 28 26 331\nE-Mail: info@agentur-rossmanek.de"})

        elif self.partner_id.agent_name == 'Pforte':
            self.update({'note': "Ihr persönlicher Ansprechpartner: Agentur Pforte\nKontakt: Agentur Pforte, Sibeliusstraße 3, 30989 Gehrden\nTel. 05108 6447801\nE-Mail: gunther.pforte@t-online.de"})

        elif self.partner_id.agent_name == 'Senft':
            self.update({'note': "Ihr persönlicher Ansprechpartner: Handelsagentur Senft\nKontakt: Christian Senft, Am Rheinberg 19, 55411 Bingen\nTel. 01702102456\nE-Mail: info@cs-handelsagentur.de"})

        elif self.partner_id.agent_name == 'Wirtz':
            self.update({'note': "Ihr persönlicher Ansprechpartner: Agentur Wirtz\nKontakt: Agentur Wirtz, Tannenweg 23, 41363 Jüchen\nTel. 02165 87 27 50\nE-Mail: agenturwirtz@t-online.de "})

        elif self.partner_id.agent_name == 'Kuhnle':
            self.update({'note': "Ihr persönlicher Ansprechpartner: Agentur Kuhnle\nKontakt: Agentur Kuhnle, Bonwiedenweg 18, 73312 Türkheim\nTel. 07331 951110\nE-Mail: s.kuhnle@t-online.de "})

        elif self.partner_id.agent_name == 'Werner':
            self.update({'note': "Ihr persönlicher Ansprechpartner: Handelsagentur BUCH + RAUM\nKontakt: Thomas Werner, Tulpenweg 9, 83254 Breitbrunn am Chiemsee\nTel. 0172 7238676\nE-Mail: werner@buch-raum.de"})

        elif self.partner_id.agent_name == 'DEsignLICIOUS':
            self.update({'note': "For any concerns you are welcome to contact your sales agency DEsignLICIOUS\nContact: Mirjam Swart\nE-Mail: mirjam@designlicious.nl\nPhone: (+31) 6 36429052"})

        elif self.partner_id.agent_name == 'The Living Connection':
            self.update({'note': "For any concerns you are welcome to contact your sales agency\nThe Living Connection\nContact: Thijs & Anne van de Laak\nE-Mail: anne@thelivingconnection.com\nPhone: 0034 673 820 269"})

        elif self.partner_id.agent_name == 'Handelsagentur Schur GbR':
            self.update({'note': "Ihr persönlicher Ansprechpartner: Handelsagentur Schur GbR\nKontakt: Wolfgang Schur, Johann-Ziegler-Str. 14c, 85221 Dachau\nTel. 08131 333 26 37\nE-Mail: info@ha-schur.com"})

        elif self.partner_id.agent_name == 'Agence made IN':
            self.update({'note':"Your contact person is Jean-Yves Guillou and Charlotte Lagardère\nPhone: 0036 09 73 39 60\nE-Mail: contact@agencemadein.com\n"})

        # Added empty notes instead of below one
        else:
            self.update({'note':""})

        # Remove extra text from sale/invoice template
        # else:
        #         self.update({'note' :"Bitte beachten Sie, dass wir bei nicht vereinbartem Skontoabzug oder Kürzung des Rechnungsbetrages eine Bearbeitungsgebühr von 10 EUR erheben müssen."})


class defaultnote(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('partner_id')
    def onchange_partner_id_sale_agent(self):

        if self.partner_id.agent_name == 'Rossmanek':
            self.update({'comment': "Ihr persönlicher Ansprechpartner: Handelsagentur Rossmanek\nKontakt: Ole Roßmanek, Timms Hoff 7, 22941 Delingsdorf\nTel. 04532 28 26 331\nE-Mail: info@agentur-rossmanek.de"})

        elif self.partner_id.agent_name == 'Pforte':
            self.update({'comment': "Ihr persönlicher Ansprechpartner: Agentur Pforte\nKontakt: Agentur Pforte, Sibeliusstraße 3, 30989 Gehrden\nTel. 05108 6447801\nE-Mail: gunther.pforte@t-online.de"})

        elif self.partner_id.agent_name == 'Senft':
            self.update({'comment': "Ihr persönlicher Ansprechpartner: Handelsagentur Senft\nKontakt: Christian Senft, Am Rheinberg 19, 55411 Bingen\nTel. 01702102456\nE-Mail: info@cs-handelsagentur.de"})

        elif self.partner_id.agent_name == 'Wirtz':
            self.update({'comment': "Ihr persönlicher Ansprechpartner: Agentur Wirtz\nKontakt: Agentur Wirtz, Tannenweg 23, 41363 Jüchen\nTel. 02165 87 27 50\nE-Mail: agenturwirtz@t-online.de "})

        elif self.partner_id.agent_name == 'Kuhnle':
            self.update({'comment': "Ihr persönlicher Ansprechpartner: Agentur Kuhnle\nKontakt: Agentur Kuhnle, Bonwiedenweg 18, 73312 Türkheim\nTel. 07331 951110\nE-Mail: s.kuhnle@t-online.de "})

        elif self.partner_id.agent_name == 'Werner':
            self.update({'comment': "Ihr persönlicher Ansprechpartner: Handelsagentur BUCH + RAUM\nKontakt: Thomas Werner, Tulpenweg 9, 83254 Breitbrunn am Chiemsee\nTel. 0172 7238676\nE-Mail: werner@buch-raum.de"})

        elif self.partner_id.agent_name == 'DEsignLICIOUS':
            self.update({'comment': "For any concerns you are welcome to contact your sales agency DEsignLICIOUS\nContact: Mirjam Swart\nE-Mail: mirjam@designlicious.nl\nPhone: (+31) 6 36429052"})

        elif self.partner_id.agent_name == 'The Living Connection':
            self.update({'comment': "For any concerns you are welcome to contact your sales agency\nThe Living Connection\nContact: Thijs & Anne van de Laak\nE-Mail: anne@thelivingconnection.com\nPhone: 0034 673 820 269"})

        elif self.partner_id.agent_name == 'Handelsagentur Schur GbR':
            self.update({'comment': "Ihr persönlicher Ansprechpartner: Handelsagentur Schur GbR\nKontakt: Wolfgang Schur, Johann-Ziegler-Str. 14c, 85221 Dachau\nTel. 08131 333 26 37\nE-Mail: info@ha-schur.com"})

        elif self.partner_id.agent_name == 'Agence made IN':
            self.update({'comment':"Your contact person is Jean-Yves Guillou and Charlotte Lagardère\nPhone: 0036 09 73 39 60\nE-Mail: contact@agencemadein.com\n"})

        # Added empty notes instead of below one
        else:
            self.update({'comment':""})

        # Remove extra text from sale/invoice template
        # else:
        #         self.update({'note' :"Bitte beachten Sie, dass wir bei nicht vereinbartem Skontoabzug oder Kürzung des Rechnungsbetrages eine Bearbeitungsgebühr von 10 EUR erheben müssen."})

