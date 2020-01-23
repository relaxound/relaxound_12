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
    

class sale_popup1(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def order_export(self):
        ftp = FTP("62.214.48.227")
        ftp.login('relaxound', 'qOIg7W1Cic1vSNU')
        ftp.cwd('TEST')

        
        try:
            sale_ids = self.id

            orders = self.env['sale.order'].search([('id', '=', sale_ids), ('imported_to_lido', '=', False), (
            'invoice_status', 'in', ['invoiced','to invoice']), ('warehouse_id.name', '=', 'LIMAL')])

        except ValueError as e:
            sale_ids = self._context.get('active_ids', [])
            orders = self.env['sale.order'].search([('id', 'in', sale_ids), ('imported_to_lido', '=', False), (
            'invoice_status', 'in', ['invoiced','to invoice']), ('warehouse_id.name', '=', 'LIMAL')])

        _logger.debug("1 ---------------------> %s" % orders)
        current_date = fields.Datetime.now()
        # with open(os.path.join("/home/mansi/Desktop/Shipping/shipping_data_%s.csv" % (current_date)), 'wb') as shipping_data:
        with open(os.path.join("src/SALE-ORDER/shipping_data_%s.csv" % (current_date)), 'wb') as shipping_data:
            shipping_data.write(b'ship_dataname1;is_retailer;ship_company;ship_addr1;ship_addr2;ship_city;ship_state;ship_zip;ship_country;ship_email;bill_name;bill_company;bill_addr1;bill_addr2;bill_city;bill_state;bill_zip;bill_country;inv_num;date;ship_method;item_line_number;item_name;item_description;item_quantity;item_price;\n')
            for order in orders:
                invoices = self.env['account.invoice'].search(
                    [('origin', '=', order.name)])
                _logger.debug("2 ---------------------> %s" % invoices)
                data = [order.partner_shipping_id and order.partner_shipping_id.name or '' , str(order.is_retailer), '',
                        order.partner_shipping_id.street or '', order.partner_shipping_id.street2 or '', order.partner_shipping_id.city or '',
                        order.partner_shipping_id.state_id.name or '', order.partner_shipping_id.zip or '', order.partner_shipping_id.country_id.name or '',
                        order.partner_shipping_id.email or '', order.partner_invoice_id.name or '', ' ', order.partner_invoice_id.street or '',
                        order.partner_invoice_id.street2 or '', order.partner_invoice_id.city or '', ' ', order.partner_invoice_id.zip or '',
                        order.partner_invoice_id.country_id and order.partner_invoice_id.country_id.name or '',order.name or '', invoices and str(invoices[0].date_invoice) or '', 'PACKET']
                                if invoices:
                    for invoice in invoices:
                        for line in invoice.invoice_line_ids:
                            if line.product_id.type != 'service':
                                if line.product_id.pitem_ids:
                                    items = line.product_id.pitem_ids
                                    # items = line.product_id
                                    bundle_price = str(line.price_subtotal)
                                    bundle_id = str(line.id)
                                    for item in items:
                                        ship_data = data
                                        ship_data = data + [bundle_id, str(item.item_id.default_code),
                                                            item.item_id.name,
                                                            str(item.qty_uom), bundle_price]
                                        ship_data.append('\n')
                                        shipping_data.write(
                                            ';'.join(map(str, ship_data)).encode('utf-8'))
                                        bundle_price = ''
                                        bundle_id = ''
                                else:
                                    ship_data = data
                                    ship_data = data + [str(line.id), str(line.product_id.code), line.name, str(
                                        line.quantity), str(line.price_subtotal)]
                                    ship_data.append('\n')
                                    shipping_data.write(
                                        ';'.join(map(str,ship_data)).encode('utf-8'))
                else:
                    for line in order.order_line:
                        if line.product_id.type != 'service':
                            if line.product_id.pitem_ids:
                                items = line.product_id.pitem_ids
                                # items = line.product_id
                                bundle_price = str(line.price_subtotal)
                                bundle_id = str(line.id)
                                for item in items:
                                    ship_data = data
                                    ship_data = data + [bundle_id, str(item.item_id.default_code),item.item_id.name,
                                                        str(item.qty_uom), bundle_price]
                                    ship_data.append('\n')
                                    shipping_data.write(
                                        ';'.join(map(str, ship_data)).encode('utf-8'))
                                    bundle_price = ''
                                    bundle_id = ''
                            else:
                                ship_data = data
                                ship_data = data + [str(line.id), str(line.product_id.code), line.name, str(
                                    line.product_uom_qty), str(line.price_subtotal)]
                                ship_data.append('\n')
                                shipping_data.write(
                                    ';'.join(map(str,ship_data)).encode('utf-8'))
                    

            order.imported_to_lido = True
            order.imported_date = current_date

        shipping_data.close()
        date_time = current_date.strftime("%m-%d-%Y %H.%M.%S")
        # print("date and time:",date_time)     

        file = open("src/SALE-ORDER/shipping_data_%s.csv" % (current_date),'rb')
        # file = open("/home/mansi/Desktop/Shipping/shipping_data_%s.csv" % (current_date),'rb')
        ftp.storbinary('STOR '+ftp.pwd()+'/shipping_data_%s.csv'%(date_time),file)