# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from suds.client import Client
import base64
# import urllib2
from datetime import datetime, timedelta
import os
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from lxml import etree
from _struct import pack

import logging

_logger = logging.getLogger(__name__)


class ProviderDhl(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[('dhl_de', "DHL DE")])

    cig_user = fields.Char(string="CGI User")
    cig_pass = fields.Char(string="CIG Pass")
    dhl_user = fields.Char(string="DHL User")
    dhl_signature = fields.Char(string="DHL Signature")
    dhl_ekp = fields.Char(string="DHL EKP")
    dhl_test_mode = fields.Boolean(default=True, string="Test Mode",
                                   help="Uncheck this box to use production DHL Web Services")
    dhl_product = fields.Selection(selection=[('EPN', 'DHL Paket National'), ('BPI', 'DHL Paket International')])

    def deleteShipment(self, client, trackingNrs):
        token = client.factory.create('ns1:AuthentificationType')
        token.user = self.dhl_user
        token.signature = self.dhl_signature
        token.accountNumber = self.dhl_ekp
        token.type = 0
        client.set_options(soapheaders=token)
        xml = u'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cis="http://dhl.de/webservice/cisbase" xmlns:de="http://de.ws.intraship">'
        xml += '<soapenv:Header><cis:Authentification>'
        xml += '<cis:user>' + self.dhl_user + '</cis:user>'
        xml += '<cis:signature>' + self.dhl_signature + '</cis:signature>'
        xml += '<cis:accountNumber>' + self.dhl_ekp + '</cis:accountNumber> <cis:type>0</cis:type>'
        xml += '</cis:Authentification></soapenv:Header>'
        xml += '<soapenv:Body><de:DeleteShipmentDDRequest><cis:Version><cis:majorRelease>1</cis:majorRelease><cis:minorRelease>0</cis:minorRelease></cis:Version>'
        for tnr in trackingNrs:
            xml += '<ShipmentNumber><cis:shipmentNumber>' + tnr + '</cis:shipmentNumber></ShipmentNumber>'
        xml += '</de:DeleteShipmentDDRequest></soapenv:Body></soapenv:Envelope>'

        res = client.service.deleteShipmentDD(__inject={'msg': xml.encode("utf-8")})
        return res

    def dhl_de_get_shipping_price_from_so(self, orders):
        return [0]

    def createClient(self, soapaction):
        module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # entsprechende WSDL je nach Modus laden
        url = 'file:///' + os.path.join(module_dir, 'static/wsdl/geschaeftskundenversand-api-1.0.wsdl')
        if self.dhl_test_mode:
            url = 'file:///' + os.path.join(module_dir, 'static/wsdl/geschaeftskundenversand-api-1.0_test.wsdl')

        base64string = base64.encodestring('%s:%s' % (self.cig_user, self.cig_pass)).replace('\n', '')
        authenticationHeader = {
            "SOAPAction": soapaction,
            "Authorization": "Basic %s" % base64string
        }
        client = Client(url=url, headers=authenticationHeader)

        return client

    def dhl_de_send_shipping(self, pickings):
        res = []
        if 1 == 1:
            shipping_data = {
                'exact_price': 0,
                'tracking_number': ''
            }
            return res + [shipping_data]
        warehouse_obj = self.env['stock.warehouse']

        for picking in pickings:

            # Prüfen, ob alle Artikel in Paketen sind
            for spo in picking.pack_operation_product_ids:
                if not (spo.result_package_id):
                    raise UserError(_('Not all articles are in packages.'))

            client = self.createClient('urn:createShipmentDD')

            # Request zusammenbauen
            token = client.factory.create('ns1:AuthentificationType')
            token.user = self.dhl_user
            token.signature = self.dhl_signature
            token.accountNumber = self.dhl_ekp
            token.type = 0

            client.set_options(soapheaders=token)
            xml = u'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cis="http://dhl.de/webservice/cisbase" xmlns:de="http://de.ws.intraship">'
            xml += '<soapenv:Header><cis:Authentification>'
            xml += '<cis:user>' + self.dhl_user + '</cis:user>'
            xml += '<cis:signature>' + self.dhl_signature + '</cis:signature>'
            xml += '<cis:accountNumber>' + self.dhl_ekp + '</cis:accountNumber> <cis:type>0</cis:type>'
            xml += '</cis:Authentification></soapenv:Header>'
            xml += '<soapenv:Body><de:CreateShipmentDDRequest><cis:Version><cis:majorRelease>1</cis:majorRelease><cis:minorRelease>0</cis:minorRelease><cis:build>14</cis:build> </cis:Version>'

            if len(picking.package_ids) == 0:
                raise osv.except_osv((_('Error')), (_('No packages')))

            export = ExportDocument(shipping_cost=picking.sale_id.shipping_cost if picking.sale_id else 0.00)
            # pro Paket wird eine Order anlegen
            for pack in picking.package_ids:

                # Gewicht berechnen
                weight = 0
                for quant in pack.quant_ids:
                    weight += quant.product_id.weight * quant.qty
                    export.append(quant)
                xml += '<ShipmentOrder><SequenceNumber>%d</SequenceNumber>' % pack.id
                xml += '<Shipment><ShipmentDetails>'
                xml += '<ProductCode>' + self.dhl_product + '</ProductCode>'
                xml += '<ShipmentDate>' + datetime.date.today().isoformat() + '</ShipmentDate>'
                xml += '<cis:EKP>' + self.dhl_ekp + '</cis:EKP>'
                xml += '<Attendance><cis:partnerID>01</cis:partnerID></Attendance>'
                if picking.sale_id.name:
                    xml += '<CustomerReference>' + picking.sale_id.name + '</CustomerReference>'
                xml += '<ShipmentItem><WeightInKG>%f</WeightInKG> <PackageType>PK</PackageType></ShipmentItem></ShipmentDetails>' % weight

                location = picking.location_id

                while location.usage != 'view':
                    location = location.location_id

                wh = False
                whs = warehouse_obj.search([('code', '=like', location.name)])
                if len(whs) > 0:
                    wh = whs[0]
                if not (wh):
                    wh = warehouse_obj.browse(1)

                partner = wh.partner_id
                export.country_code = partner.country_id.code

                if not (partner.street):
                    raise UserError(_('No street in company data.'))

                # Straße und Hausnummer aus dem Adressfeld bestimmen
                street = ""
                street2 = partner.street2
                nr = ""
                split = filter(None, partner.street.split(' '))
                if len(split) == 1:
                    street = partner.street[:-2]
                    nr = partner.street[-2:]
                else:
                    street = split[:-1]
                    nr = split[-1]

                if street and len(street) > 50:
                    street = street[:50]
                if street2 and len(street2) > 50:
                    street2 = street2[:50]
                if nr and len(nr) > 7:
                    nr = nr[:7]

                xml += '<Shipper><Company>'
                xml += '<cis:Company><cis:name1>' + partner.name.replace('&', '&amp;') + '</cis:name1></cis:Company></Company><Address>'
                xml += '<cis:streetName>' + ' '.join(street).replace('&', '&amp;') + '</cis:streetName>'
                xml += '<cis:streetNumber>' + nr.replace('&', '&amp;') + '</cis:streetNumber>'
                xml += '<cis:Zip>'
                if street2 and len(street2) > 0:
                    xml += '<cis:careOfName>' + street2.replace('&', '&amp;') + '</cis:careOfName>'
                if partner.country_id.code == 'DE':
                    xml += '<cis:germany>' + partner.zip.replace('&', '&amp;') + '</cis:germany>'
                elif partner.country_id.code == 'UK':
                    xml += '<cis:england>' + partner.zip.replace('&', '&amp;') + '</cis:england>'
                else:
                    xml += '<cis:other>' + partner.zip.replace('&', '&amp;') + '</cis:other>'
                xml += '</cis:Zip>'
                xml += '<cis:city>' + partner.city.replace('&', '&amp;') + '</cis:city>'
                xml += '<cis:Origin><cis:countryISOCode>' + partner.country_id.code + '</cis:countryISOCode></cis:Origin></Address>'

                xml += '<Communication>'
                if partner.email:
                    xml += '<cis:email>' + partner.email.replace('&', '&amp;') + '</cis:email>'
                xml += '<cis:contactPerson>' + partner.name.replace('&', '&amp;') + '</cis:contactPerson>'
                xml += '</Communication></Shipper>'

                partner = picking.partner_id
                if not (partner.street):
                    raise UserError(_('No street in partner.'))

                xml += '<Receiver><Company>'
                if partner.company_type == 'company':
                    xml += '<cis:Company><cis:name1>' + partner.name.replace('&',
                                                                             '&amp;') + '</cis:name1>'
                    if partner.woo_company_name_ept:
                        xml += '<cis:name2>' + partner.woo_company_name_ept.replace('&',
                                                                '&amp;') + '</cis:name2></cis:Company>'
                    else:
                        xml += '</cis:Company>'
                else:
                    xml += '<cis:Person><cis:firstname></cis:firstname><cis:lastname>' + partner.name.replace('&',
                                                                                                              '&amp;') + '</cis:lastname> </cis:Person>'

                street = ""
                street2 = partner.street2
                nr = ""
                split = filter(None, partner.street.split(' '))
                if len(split) == 1:
                    street = partner.street[:-2]
                    nr = partner.street[-2:]
                else:
                    street = split[:-1]
                    nr = split[-1]

                if street and len(street) > 50:
                    street = street[:50]
                if street2 and len(street2) > 50:
                    street2 = street2[:50]
                if nr and len(nr) > 7:
                    nr = nr[:7]

                xml += '</Company><Address><cis:streetName>' + ' '.join(street).replace('&',
                                                                                        '&amp;') + '</cis:streetName><cis:streetNumber>' + nr.replace(
                    '&', '&amp;') + '</cis:streetNumber>'
                if street2 and len(street2) > 0:
                    xml += '<cis:careOfName>' + street2.replace('&', '&amp;') + '</cis:careOfName>'
                xml += '<cis:Zip>'

                if partner.country_id.code == 'DE':
                    xml += '<cis:germany>' + partner.zip.replace('&', '&amp;') + '</cis:germany>'
                elif partner.country_id.code == 'UK':
                    xml += '<cis:england>' + partner.zip.replace('&', '&amp;') + '</cis:england>'
                else:
                    xml += '<cis:other>' + partner.zip.replace('&', '&amp;') + '</cis:other>'
                xml += '</cis:Zip>'
                xml += '<cis:city>' + partner.city.replace('&', '&amp;') + '</cis:city>'
                xml += '<cis:Origin><cis:countryISOCode>' + partner.country_id.code + '</cis:countryISOCode></cis:Origin></Address>'
                xml += '<Communication>'
                if 'Packstation' in partner.street or 'packstation' in partner.street:
                    xml += '<cis:contactPerson>' + partner.street2.replace('&', '&amp;') + '</cis:contactPerson>'
                else:
                    if partner.email:
                        xml += '<cis:email>' + partner.email.replace('&', '&amp;') + '</cis:email>'
#                    xml += '<cis:contactPerson>' + partner.name.replace('&', '&amp;') + '</cis:contactPerson>'
                xml += '</Communication></Receiver>'
                if self.dhl_product == 'BPI':
                    export_xml = str(export)
                    xml += export_xml
                xml += '</Shipment> </ShipmentOrder>'

            xml += '</de:CreateShipmentDDRequest></soapenv:Body></soapenv:Envelope>'

            shipment = client.service.createShipmentDD(__inject={'msg': xml.encode("utf-8")})

            # Fehlerauswertung
            if shipment.status.StatusCode != 0:
                if hasattr(shipment, 'CreationState'):
                    errorMessage = _('The following error(s) occured:\n\n') + shipment.status.StatusMessage + '\n'

                    for cs in shipment.CreationState:
                        for sm in cs.StatusMessage:
                            errorMessage += sm + '\n'
                    raise UserError(errorMessage)
                else:
                    raise UserError(_('The following error(s) occured:\n\n') + shipment.status.StatusMessage)

            shipping_data = {
                'exact_price': 0,
                'tracking_number': ''
            }
            warnings = []
            tnrs = []

            # Prüfen, ob es Warnungen gab
            for cs in shipment.CreationState:
                for sm in cs.StatusMessage:
                    if "Warning" in sm:
                        warnings.append(sm)
                tnrs.append(cs.ShipmentNumber.shipmentNumber)

            # wenn es Warnungen gab und diese nicht ignoriert werden sollen, wird ein entsprechender Fehler ausgegeben
            if len(warnings) > 0 and not (picking.ignore_warnings):
                # Sendungen löschen, damit diese keine Kosten erzeugen
                try:
                    self.deleteShipment(self.createClient('urn:deleteShipmentDD'), tnrs)
                except:
                    pass
                raise UserError(_(
                    'The following warning(s) occured (rerun with \'Warnings Checked\' if everything is fine):\n\n') + '\n'.join(
                    warnings))
            else:
                for cs in shipment.CreationState:
                    for pack in picking.package_ids:
                        if pack.id == int(cs.SequenceNumber):
                            # Label herunterladen
                            url = cs.Labelurl

                            response = urllib2.urlopen(url)
                            data = response.read()
                            carrier_tracking_ref = cs.ShipmentNumber.shipmentNumber
                            attachments = [('LabelDHL-%s.pdf' % carrier_tracking_ref, data)]

                            if self.dhl_product == 'BPI':
                                export_client = self.createClient('urn:getExportDocDD')

                                # Request zusammenbauen
                                token = export_client.factory.create('ns1:AuthentificationType')
                                token.user = self.dhl_user
                                token.signature = self.dhl_signature
                                token.accountNumber = self.dhl_ekp
                                token.type = 0

                                export_client.set_options(soapheaders=token)
                                xml = u'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cis="http://dhl.de/webservice/cisbase" xmlns:de="http://de.ws.intraship">'
                                xml += '<soapenv:Header><cis:Authentification>'
                                xml += '<cis:user>' + self.dhl_user + '</cis:user>'
                                xml += '<cis:signature>' + self.dhl_signature + '</cis:signature>'
                                xml += '<cis:accountNumber>' + self.dhl_ekp + '</cis:accountNumber> <cis:type>0</cis:type>'
                                xml += '</cis:Authentification></soapenv:Header>'
                                xml += '<soapenv:Body><de:GetExportDocDDRequest><cis:Version><cis:majorRelease>1</cis:majorRelease><cis:minorRelease>0</cis:minorRelease><cis:build>14</cis:build> </cis:Version>'
                                xml += """<ShipmentNumber><cis:shipmentNumber>%s</cis:shipmentNumber></ShipmentNumber>""" % (
                                    carrier_tracking_ref,)
                                xml += '</de:GetExportDocDDRequest></soapenv:Body></soapenv:Envelope>'
                                export_doc_res = export_client.service.getExportDocDD(
                                    __inject={'msg': xml.encode("utf-8")})
                                for doc_data in export_doc_res.ExportDocData:
                                    export_url = getattr(doc_data, 'ExportDocURL', None)
                                    if export_url:
                                        response = urllib2.urlopen(export_url)
                                        data = response.read()
                                        attachments.append(('ExportLabelDHL-%s.pdf' % carrier_tracking_ref, data))

                            # Nachricht im Picking mit dem entsprechenden Label anlegen

                            logmessage = (
                                _("Shipment created into DHL for package %s <br/> <b>Tracking Number : </b>%s") % (
                                    pack.name, carrier_tracking_ref))
                            picking.message_post(body=logmessage, attachments=attachments)

                            # Trackingnummer am Package speichern
                            pack.tracking_nr = carrier_tracking_ref

                            shipping_data = {
                                'exact_price': 0,
                                'tracking_number': carrier_tracking_ref
                            }
                            break
            res = res + [shipping_data]

        return res

    def dhl_de_get_tracking_link(self, pickings):
        res = []
        for picking in pickings:
            res = res + [
                'https://nolp.dhl.de/nextt-online-public/set_identcodes.do?lang=de&idc=%s' % picking.carrier_tracking_ref]
        return res

    def dhl_de_cancel_shipment(self, picking):

        if not (picking.carrier_tracking_ref):
            return

        client = self.createClient('urn:deleteShipmentDD')

        tnrs = []
        for pack in picking.package_ids:
            tnrs.append(pack.tracking_nr)
        self.deleteShipment(client, tnrs)

        for pack in picking.package_ids:
            pack.tracking_nr = ''

        picking.write({'carrier_tracking_ref': '',
                       'carrier_price': 0.0})


class ExportDocument(object):
    """<ExportDocument>
                        <InvoiceType>commercial</InvoiceType>
                        <InvoiceDate>2015-11-05</InvoiceDate>                        
                        <ExportType>1</ExportType>  
                        <TermsOfTrade>CPT</TermsOfTrade>
                        <Amount>2000</Amount>
                        <Description>Verkaufen</Description>
                        <CountryCodeOrigin>DE</CountryCodeOrigin>
                        <AdditionalFee>0.0</AdditionalFee>
                        <CustomsValue>2.23</CustomsValue>
                        <CustomsCurrency>EUR</CustomsCurrency>
                        <PermitNumber>?</PermitNumber>
                        <AttestationNumber>?</AttestationNumber>
                        <ExportDocPosition>
                            <Description>Harddisk</Description>
                            <CountryCodeOrigin>DE</CountryCodeOrigin>
                            <Amount>200</Amount>
                            <NetWeightInKG>1</NetWeightInKG>
                            <GrossWeightInKG>1.2</GrossWeightInKG>
                            <CustomsValue>200</CustomsValue>
                            <CustomsCurrency>EUR</CustomsCurrency>
                        </ExportDocPosition>
                    </ExportDocument>"""

    def __init__(self, invoice_type='commercial', country_code='DE', export_type='1', invoice_date=fields.Date.today(),
                 shipping_cost=0.00):
        super(ExportDocument, self).__init__()
        self.invoice_type = invoice_type
        self.invoice_date = invoice_date
        self.export_type = export_type
        self.country_code = country_code
        self.value = 0.0
        self.amount = 0
        self.pos = []
        self.shipping_cost = shipping_cost

    def append(self, quant):
        new_position = {}
        # new_position['description'] = quant.product_id.name
        new_position['description'] = "Relaxtool/design gift: Activated by a motion sensor the Zwitscherbox is" \
                                      " playing birds chirping/forest atmosphere for 2min."
        new_position['amount'] = str(int(quant.qty))
        self.amount += quant.qty
        total_price = quant.sale_price_total
        new_position['value'] = str(total_price)
        # new_position['value'] = str(quant.cost)
        self.value += total_price

        new_position['weight'] = str(quant.product_id.weight)
        # new_position['iso_country_code'] = self.country_code
        new_position['iso_country_code'] = 'IN'
        new_position['CustomsTariffNumber'] = '85437090'
        self.pos.append(new_position)

    def __str__(self):
        root = etree.Element('ExportDocument')
        child = etree.SubElement(root, 'InvoiceType')
        child.text = self.invoice_type
        child = etree.SubElement(root, 'InvoiceDate')
        child.text = self.invoice_date
        child = etree.SubElement(root, 'ExportType')
        child.text = self.export_type
        child = etree.SubElement(root, 'TermsOfTrade')
        child.text = "CPT"
        child = etree.SubElement(root, 'Amount')
        child.text = str(int(self.amount))
        child = etree.SubElement(root, 'Description')
        child.text = "Verkaufen"
        child = etree.SubElement(root, 'CountryCodeOrigin')
        child.text = self.country_code
        child = etree.SubElement(root, 'AdditionalFee')
        child.text = str(self.shipping_cost)
        child = etree.SubElement(root, 'CustomsValue')
        child.text = str(self.value)
        child = etree.SubElement(root, 'CustomsCurrency')
        child.text = "EUR"
        child = etree.SubElement(root, 'PermitNumber')
        child.text = "?"
        child = etree.SubElement(root, 'AttestationNumber')
        child.text = "?"

        for pos in self.pos:
            position = etree.SubElement(root, 'ExportDocPosition')
            child = etree.SubElement(position, 'Description')
            child.text = pos['description']
            child = etree.SubElement(position, 'CountryCodeOrigin')
            child.text = pos['iso_country_code']
            child = etree.SubElement(position, 'Amount')
            child.text = pos['amount']
            child = etree.SubElement(position, 'NetWeightInKG')
            child.text = pos['weight']
            child = etree.SubElement(position, 'GrossWeightInKG')
            child.text = pos['weight']
            child = etree.SubElement(position, 'CustomsValue')
            child.text = pos['value']
            child = etree.SubElement(position, 'CustomsCurrency')
            child.text = 'EUR'
            child = etree.SubElement(position, 'CustomsTariffNumber')
            child.text = pos['CustomsTariffNumber']
        return etree.tostring(root)
