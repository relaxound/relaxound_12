# -*- coding: utf-8 -*-
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
    
class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def _multi_export_shipping_data(self, orders):
        ftp = FTP("ftp.techops.techspawnmobiles.com")
        ftp.login(' relaxound@techops.techspawnmobiles.com', 'password@123456')
        ftp.cwd('demo-test')
        current_date = fields.Datetime.now()
        # with open(os.path.join('shipping_data_%s.csv' % (current_date)), 'wb') as shipping_data:

        with open(os.path.join("/home/mac37/Desktop/Export/LIMAR/shipping_data_%s.csv" % (current_date)), 'wb') as shipping_data:
            shipping_data.write(b'ship_name;is_retailer;ship_company;ship_addr1;ship_addr2;ship_city;ship_state;ship_zip;ship_country;ship_email;bill_name;bill_company;bill_addr1;bill_addr2;bill_city;bill_state;bill_zip;bill_country;inv_num;date;ship_method;item_line_number;item_name;item_description;item_quantity;item_price\n')
            for order in orders:
                invoices = self.env['account.invoice'].search([('origin', '=', order.name)])
                data = [order.partner_shipping_id and order.partner_shipping_id.name or '',
                        order.partner_id.is_retailer and 'True' or 'False', '' or '',
                        order.partner_shipping_id.street or '', order.partner_shipping_id.street2 or '',
                        order.partner_shipping_id.city or '', ' ', order.partner_shipping_id.zip or '',
                        order.partner_shipping_id.country_id.name or '', order.partner_shipping_id.email or '',
                        order.partner_invoice_id.name or '', ' ', order.partner_invoice_id.street or '',
                        order.partner_invoice_id.street2 or '', order.partner_invoice_id.city or '',
                        order.partner_invoice_id.state_id.name or ' ', order.partner_invoice_id.zip or '',
                        order.partner_invoice_id.country_id and order.partner_invoice_id.country_id.name or '',
                        order.name or '', datetime.today().strftime('%Y-%m-%d'), 'PACKET']
                if order:
                    for line in order.order_line:
                        if line.product_id.type != 'service':
                            if line.product_id.item_ids:
                                items = line.product_id.item_ids
                                bundle_price = str(line.price_subtotal)
                                bundle_id = str(line.id)
                                for item in items:
                                    ship_data = data + [bundle_id, str(item.item_id.code), item.item_id.name,
                                                        str(item.qty_uom * line.product_uom_qty), bundle_price]
                                    ship_data.append('\n')
                                    shipping_data.write(';'.join(ship_data).encode('utf-8'))
                                    bundle_price = ''
                                    bundle_id = ''
                            else:
                                ship_data = data + [str(line.id), str(line.product_id.code), line.name,
                                                    str(line.product_uom_qty), str(line.price_subtotal)]
                                ship_data.append('\n')
                                shipping_data.write(';'.join(ship_data).encode('utf-8'))
                order.imported_to_lido = True
                order.imported_date = current_date
                shipping_data.close()

            date_time = current_date.strftime("%m-%d-%Y %H.%M.%S")
            file = open("/home/mac37/Desktop/Export/LIMAR/shipping_data_%s.csv" % (current_date),'rb')
            ftp.storbinary('STOR '+ftp.pwd()+'/shipping_data_%s.csv' % (date_time), file)

                # ftp.storbinary('STOR'+ftp.pwd()+'/shipping_data_%s.csv' % (current_date.replace(":", ".", 3)),
                #        open("/home/mac37/Desktop/Export", "LIMAR", 'shipping_data_%s.csv' % (current_date)), 'rb')


class sale_popup1(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def order_export(self, sale_ids):
        orders = self.env['sale.order'].search(
            [('id', 'in', sale_ids), ('imported_to_lido', '=', False), ('warehouse_id.name', '=', 'YourCompany')])
        if orders:
            self.env['account.invoice']._multi_export_shipping_data(orders)
        return True

    @api.multi
    def uni_order_export(self):
        orders = self.env['sale.order'].search(
            [('id', '=', self.id), ('imported_to_lido', '=', False), ('warehouse_id.name', '=', 'YourCompany')])
        if orders:
            self.env['account.invoice']._multi_export_shipping_data(orders)
        return True
