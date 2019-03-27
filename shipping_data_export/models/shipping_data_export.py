# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from keyrings.alt import file

from odoo import models, fields, api, _, exceptions, tools
from datetime import datetime
import os
from datetime import date
from ftplib import FTP
import logging
_logger = logging.getLogger(__name__)
try:
    import openpyxl
except ImportError:
    _logger.debug('Can not import openpyxl`.')


class SaleOrder(models.Model):
    _inherit = "sale.order"

    imported_to_lido = fields.Boolean('Imported to Lido')
    imported_date = fields.Datetime('Imported Date')

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def _export_shipping_data(self):
        # ftp = FTP("62.214.48.227")
        # ftp.login('relaxound', 'qOIg7W1Cic1vSNU')
        # ftp.cwd('/ORDERS')
        orders = self.env['sale.order'].search([('imported_to_lido', '=', False),('invoice_status', '=', 'invoiced'),('warehouse_id.name', '=', 'LIMAL')])
        if not orders:
            return 1
        _logger.debug("1 ---------------------> %s" % orders)
        current_date = fields.Datetime.now()
        with open(os.path.join("/export", "LIMAR", 'shipping_data_%s.csv'%(current_date)), 'wb') as shipping_data:
            shipping_data.write('ship_name;is_retailer;ship_company;ship_addr1;ship_addr2;ship_city;ship_state;ship_zip;ship_country;ship_email;bill_name;bill_company;bill_addr1;bill_addr2;bill_city;bill_state;bill_zip;bill_country;inv_num;date;ship_method;item_line_number;item_name;item_description;item_quantity;item_price\n')
            for order in orders:

                invoices = self.env['account.invoice'].search([('origin', '=', order.name)])
                _logger.debug("2 ---------------------> %s" % invoices)
                data = [order.partner_shipping_id and order.partner_shipping_id.name or '', order.partner_id.is_retailer and 'True' or 'False', order.partner_id.woo_company_name_ept or '', order.partner_shipping_id.street or '', order.partner_shipping_id.street2 or '', order.partner_shipping_id.city or '', ' ', order.partner_shipping_id.zip or '',order.partner_shipping_id.country_id.name or '', order.partner_shipping_id.email or '',order.partner_invoice_id.name or '', ' ', order.partner_invoice_id.street or '', order.partner_invoice_id.street2 or '', order.partner_invoice_id.city or '', order.partner_invoice_id.state_id.name or ' ', order.partner_invoice_id.zip or '', order.partner_invoice_id.country_id and order.partner_invoice_id.country_id.name or '', order.name or '', invoices and invoices[0].date_invoice or '','PACKET']
        if invoices:
            for invoice in invoices:
                for line in invoice.invoice_line_ids:
                    if line.product_id.type != 'service':
                        if line.product_id.pitem_ids:
                            items = line.product_id.pitem_ids
                            bundle_price = str(line.price_subtotal)
                            bundle_id = str(line.id)
                            for item in items:
                                ship_data = data
                                ship_data = data + [bundle_id, str(item.item_id.code), item.item_id.name,
                                                                str(item.qty_uom * line.quantity), bundle_price]
                                ship_data.append('\n')
                                shipping_data.write(';'.join(ship_data).encode('utf-8'))
                                bundle_price = ''
                                bundle_id = ''
                        else:
                            ship_data = data
                            ship_data = data + [str(line.id), str(line.product_id.code), line.name, str(line.quantity), str(line.price_subtotal)]
                            ship_data.append('\n')
                            shipping_data.write(';'.join(ship_data).encode('utf-8'))
        order.imported_to_lido = True
        order.imported_date = current_date
            # ftp.storbinary('STOR shipping_data_%s.csv'%(current_date.replace(":", ".", 3)), open('/export/LIMAR/shipping_data_%s.csv'%(current_date), 'rb'))

        # return self.pool.get('report').get_action(self, 'shipping.data.xlsx')

class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _import_tracking_num(self, ftp=None):
        filename = 'TRACKING.csv'
        localfile = open('/export/TRACKING/'+'TRACKING.csv', 'wb')
        # ftp = FTP("62.214.48.227")
        # ftp.login('relaxound', 'qOIg7W1Cic1vSNU')
        # ftp.cwd('/TRACKING')
        # ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
        # # ftp.close()
        localfile.close()

        # os.rename('/home/ghandi/Documents/'+ filename,
        #           '/home/ghandi/Documents/TRACKING.csv')
        current_date = fields.Datetime.now()
        new_name = 'TRACKING_old_' + current_date.replace(":", ".", 3) +'.csv'
        print('new name ==============>', new_name)
        try:
            file = open('/export/TRACKING/TRACKING.csv')
            print('file ===================>', file)
            for line in file.readlines()[1:]:
                data = line.split(';')
                print('line, data --------------------->', line, data[0].replace('"', ''), data[1].replace('"', ''))
                delivery = self.env['stock.picking'].search([('origin', '=', data[0].replace('"', ''))])
                print('delivery ====================>', delivery)
                if delivery:
                    delivery[0].write({'carrier_tracking_ref': data[1].replace('"', '')})
            file.close()
            os.rename('/export/TRACKING/TRACKING.csv',
                      '/export/TRACKING/' + new_name)
            ftp.rename('TRACKING.csv', new_name)
            ftp.close()
        except Exception as e:
            _logger.warning('invalid custom view(s) for: %s', tools.ustr(e))
            pass