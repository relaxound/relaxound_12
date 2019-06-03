from odoo import models, fields, api, _, exceptions, tools
from datetime import datetime
import os
from datetime import date
from ftplib import FTP
import logging
import pandas as pd
from dateutil import parser
import pdb
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
        ftp = FTP("62.214.48.227")
        ftp.login('relaxound', 'qOIg7W1Cic1vSNU')
        ftp.cwd('TEST')
        # print(ftp.pwd())
        orders = self.env['sale.order'].search([('imported_to_lido', '=', False), (
            'invoice_status', '=', 'invoiced'), ('warehouse_id.name', '=', 'LIMAL')])
        if not orders:
            return 1
        _logger.debug("1 ---------------------> %s" % orders)
        current_date = fields.Datetime.now()
        with open(os.path.join("src/user/SALE-ORDER-DATA/shipping_data_%s.csv" % (current_date)), 'wb') as shipping_data:
            shipping_data.write(b'ship_dataname1;is_retailer;ship_company;ship_addr1;ship_addr2;ship_city;ship_state;ship_zip;ship_country;ship_email;bill_name;bill_company;bill_addr1;bill_addr2;bill_city;bill_state;bill_zip;bill_country;inv_num;date;ship_method;client_order_ref;item_quantity;item_line_number;item_name;item_description;item_price;\n')
            for order in orders:
                invoices = self.env['account.invoice'].search(
                    [('origin', '=', order.name)])  
                _logger.debug("2 ---------------------> %s" % invoices)
                data = [order.partner_shipping_id and order.partner_shipping_id.name or '' ,'True' or 'False', '', 
                        order.partner_shipping_id.street or '', order.partner_shipping_id.street2 or '', order.partner_shipping_id.city or '',
                        order.partner_shipping_id.state_id.name or '', order.partner_shipping_id.zip or '', order.partner_shipping_id.country_id.name or '',
                        order.partner_shipping_id.email or '', order.partner_invoice_id.name or '', ' ', order.partner_invoice_id.street or '',
                        order.partner_invoice_id.street2 or '', order.partner_invoice_id.city or '', ' ', order.partner_invoice_id.zip or '',
                        order.partner_invoice_id.country_id 
                        and order.partner_invoice_id.country_id.name or '', 
                        order.name or '', invoices and str(invoices[0].date_invoice) or '', 'PACKET',str(order.order_line.product_uom_qty),order.client_order_ref]
                if invoices:
                    for invoice in invoices:
                        for line in invoice.invoice_line_ids:
                            if line.product_id.type != 'service':
                                if line.product_id:
                                    items = line.product_id
                                    bundle_price = str(line.price_subtotal)
                                    bundle_id = str(line.id)
                                    for item in items:
                                        ship_data = data
                                        # ship_data = data + [bundle_id, str(item.item_id.code), item.item_id.name,
                                        #                     str(item.qty_uom * line.quantity), bundle_price]
                                        ship_data.append('\n')
                                        shipping_data.write(
                                            ';'.join(map(str,ship_data)).encode('utf-8'))
                                        bundle_price = ''
                                        bundle_id = ''
                                else:
                                    ship_data = data
                                    ship_data = data + [str(line.id), str(line.product_id.code), line.name, str(
                                        line.quantity), str(line.price_subtotal)]
                                    ship_data.append('\n')
                                    shipping_data.write(
                                        ';'.join(map(str,ship_data)).encode('utf-8'))
                order.imported_to_lido = True
                order.imported_date = current_date

        shipping_data.close()
        date_time = current_date.strftime("%m-%d-%Y %H.%M.%S")
        # print("date and time:",date_time)     

        file = open("src/user/SALE-ORDER-DATA/shipping_data_%s.csv" % (current_date),'rb')                  
        ftp.storbinary('STOR '+ftp.pwd()+'/shipping_data_%s.csv'%(date_time),file)

        # return self.pool.get('report').get_action(self, 'shipping.data.xlsx')


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _sort_data(self,cwd,ftp):
        time_list=[]
        name_list=[]
        files = ftp.mlsd("/"+cwd)
        dict1={}

        for file in files:
            name = file[0]
            timestamp = file[1]['modify']
            time = parser.parse(timestamp)
            if(file[1]['type']=="dir"):
                pass
            else:
                dict1.update({time:name})
    

        max1=max(dict1)
        file_name = dict1.get(max1)
        return file_name


    @api.model
    def _import_tracking_num(self):
        cwd="TEST"
        ftp = FTP("62.214.48.227")
        ftp.login('relaxound', 'qOIg7W1Cic1vSNU')
        ftp.cwd('/'+cwd)
        filename = self._sort_data(cwd,ftp)
        file_path='src/user/TRACKING-NUMBER/'+filename # server location # src/user/TRACKING-NUMBER/
        localfile = open(file_path, 'wb')
        ftp.retrbinary('RETR '+ftp.pwd()+'/'+ filename, localfile.write, 1024)
        localfile.close()
            
        current_date = fields.Datetime.now()
        date_time = current_date.strftime("%m-%d-%Y %H.%M.%S")
        new_name = 'TRACKING_old_%s.csv'%(date_time)
        # print('new name ==============>', new_name)
        try:
            file = open(file_path)
            # print ('file ===================>', file)
            for line in file.readlines()[1:]:
                data = line.split(',',1)
                # print("line, data --------------------->", line, data[0].replace('"', ''), data[1].replace('"', ''))
                delivery = self.env['stock.picking'].search(
                    [('origin', '=',data[0].replace('"', '') )]) #
                # print ('delivery ====================>', delivery)
                if delivery:
                    delivery[0].write({'carrier_tracking_ref': data[1].replace('"', '')})
            file.close()
            os.rename(file_path,'src/user/TRACKING-NUMBER/'+ new_name) ## server location # src/user/TRACKING-NUMBER/
            ftp.rename(ftp.pwd()+"/"+filename, new_name)
        except Exception as e:
            _logger.warning('invalid custom view(s) for: %s', tools.ustr(e))
            pass

    
