#    Techspawn Solutions Pvt. Ltd.
#    Copyright (C) 2016-TODAY Techspawn(<http://www.Techspawn.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from odoo import models, api, fields, _
from ..model.api import API
from odoo.exceptions import Warning

from ..unit.backend_adapter import WpImportExport


class wp_configure(models.Model):

    """ Models for wordpress configuration """
    _name = "wordpress.configure"
    _description = 'WooCommerce Backend Configuration'

    name = fields.Char(string='name')
    location = fields.Char("Url")
    wp_api = fields.Boolean(string="WP API", default=True)
    consumer_key = fields.Char("Consumer key")
    consumer_secret = fields.Char("Consumer Secret")
    version = fields.Selection([('wc/v2', 'v2')], 'Version')
    verify_ssl = fields.Boolean("Verify SSL")

    @api.multi
    def test_connection(self):
        """ Test connection with the given url """
        location = self.location
        cons_key = self.consumer_key
        sec_key = self.consumer_secret
        version = self.version
        wcapi = API(url=location, consumer_key=cons_key,
                    consumer_secret=sec_key, version=version, wp_api=True, timeout=1000)
        r = wcapi.get("products")
        if r.status_code == 404:
            raise Warning(_("Enter Valid url"))
        msg = ''
        if r.status_code != 200:
            msg = r.json()['message'] + '\n Error Code ' + \
                str(r.json()['data']['status'])
            raise Warning(_(msg))
        else:
            raise Warning(_('Test Success'))
        return True

    @api.multi
    def map_products(self):
        """ Assign backend to all the products """
        all_products = self.env['product.template'].search(
            [('backend_id', '!=', self.id)])
        for product in all_products:
            backends = []
            for backend_id in product.backend_id:
                backends.append(backend_id.id)
            if not self.id in backends:
                backends.append(self.id)
            product.write({'backend_id': [[6, False, backends]]})
        return True

    @api.multi
    def map_product_tags(self):
        """ Assign backend to all the products tag """
        all_tags = self.env['product.product.tag'].search(
            [('backend_id', '!=', self.id)])
        for tag in all_tags:
            backends = []
            for backend_id in tag.backend_id:
                backends.append(backend_id.id)
            if not self.id in backends:
                backends.append(self.id)
            tag.write({'backend_id': [[6, False, backends]]})
        return True

    # @api.multi
    # def map_product_coupons(self):
    #     """ Assign backend to all the products coupon """
    #     all_coupons = self.env['product.coupon'].search(
    #         [('backend_id', '!=', self.id)])
    #     for coupon in all_coupons:
    #         backends = []
    #         for backend_id in coupon.backend_id:
    #             backends.append(backend_id.id)
    #         if not self.id in backends:
    #             backends.append(self.id)
    #         coupon.write({'backend_id': [[6, False, backends]]})
    #     return True

    @api.multi
    def map_taxes(self):
        """ Assign backend to all the taxes """
        all_taxes = self.env['account.tax'].search(
            [('backend_id', '!=', self.id)])
        for tax in all_taxes:
            backends = []
            for backend_id in tax.backend_id:
                backends.append(backend_id.id)
            if not self.id in backends:
                backends.append(self.id)
            tax.write({'backend_id': [[6, False, backends]]})
        return True

    @api.multi
    def map_attributes(self):
        """ Assign backend to all the product attributes """
        all_attributes = self.env['product.attribute'].search(
            [('backend_id', '!=', self.id)])
        for attribute in all_attributes:
            backends = []
            for backend_id in attribute.backend_id:
                backends.append(backend_id.id)
            if not self.id in backends:
                backends.append(self.id)
            attribute.write({'backend_id': [[6, False, backends]]})
        self.map_attribute_values()
        return True

    @api.multi
    def map_attribute_values(self):
        """ Assign backend to all the products attribute values """
        all_att_values = self.env['product.attribute.value'].search(
            [('backend_id', '!=', self.id)])
        for attr_value in all_att_values:
            backends = []
            for backend_id in attr_value.backend_id:
                backends.append(backend_id.id)
            if not self.id in backends:
                backends.append(self.id)
            attr_value.write({'backend_id': [[6, False, backends]]})
        return True

    @api.multi
    def map_categories(self):
        """ Assign backend to all the products categories """
        all_categories = self.env['product.category'].search(
            [('backend_id', '!=', self.id)])
        for category in all_categories:
            backends = []
            for backend_id in category.backend_id:
                backends.append(backend_id.id)
            if not self.id in backends:
                backends.append(self.id)
            category.write({'backend_id': [[6, False, backends]]})
        return True

    @api.multi
    def map_customers(self):
        """ Assign backend to all the customers """
        all_customers = self.env['res.partner'].search(
            [('backend_id', '!=', self.id)])
        for customer in all_customers:
            backends = []
            for backend_id in customer.backend_id:
                backends.append(backend_id.id)
            if not self.id in backends:
                backends.append(self.id)
            customer.write({'backend_id': [[6, False, backends]]})
        return True

    @api.multi
    def map_sale_order(self):
        """ Assign backend to all the sales orders """
        all_sale_orders = self.env['sale.order'].search(
            [('backend_id', '!=', self.id)])
        for sale_order in all_sale_orders:
            backends = []
            for backend_id in sale_order.backend_id:
                backends.append(backend_id.id)
            if not self.id in backends:
                backends.append(self.id)
            sale_order.write({'backend_id': [[6, False, backends]]})
        return True

    # @api.multi
    # def map_major_unit(self):
    #     """ Assign backend to all the sales orders """
    #     all_major_unit = self.env['major_unit.major_unit'].search(
    #         [('backend_id', '!=', self.id)])
    #     for major_unit in all_major_unit:
    #         backends = []
    #         for backend_id in major_unit.backend_id:
    #             backends.append(backend_id.id)
    #         if not self.id in backends:
    #             backends.append(self.id)
    #         major_unit.write({'backend_id': [[6, False, backends]]})
    #     return True

    # @api.multi
    # def map_service_order(self):
    #     """ Assign backend to all the sales orders """
    #     all_service_order = self.env['service.repair_order'].search(
    #         [('backend_id', '!=', self.id)])
    #     for service_order in all_service_order:
    #         backends = []
    #         for backend_id in service_order.backend_id:
    #             backends.append(backend_id.id)
    #         if not self.id in backends:
    #             backends.append(self.id)
    #         service_order.write({'backend_id': [[6, False, backends]]})
    #     return True

    # @api.multi
    # def map_pickup_order(self):
    #     """ Assign backend to all the sales orders """
    #     all_pickup_order = self.env['drm.pickup'].search(
    #         [('backend_id', '!=', self.id)])
    #     for pickup_order in all_pickup_order:
    #         backends = []
    #         for backend_id in pickup_order.backend_id:
    #             backends.append(backend_id.id)
    #         if not self.id in backends:
    #             backends.append(self.id)
    #         pickup_order.write({'backend_id': [[6, False, backends]]})
    #     return True

    # @api.multi
    # def map_standard_job(self):
    #     """ Assign backend to all the sales orders """
    #     all_standard_job = self.env['service.standard_job'].search(
    #         [('backend_id', '!=', self.id)])
    #     for standard_job in all_standard_job:
    #         backends = []
    #         for backend_id in standard_job.backend_id:
    #             backends.append(backend_id.id)
    #         if not self.id in backends:
    #             backends.append(self.id)
    #         standard_job.write({'backend_id': [[6, False, backends]]})
    #     return True

    # @api.multi
    # def map_product_deal(self):
    #     """ Assign backend to all the sales orders """
    #     all_product_deal = self.env['product.deals'].search(
    #         [('backend_id', '!=', self.id)])
    #     for product_deal in all_product_deal:
    #         backends = []
    #         for backend_id in product_deal.backend_id:
    #             backends.append(backend_id.id)
    #         if not self.id in backends:
    #             backends.append(self.id)
    #         product_deal.write({'backend_id': [[6, False, backends]]})
    #     return True

    # @api.multi
    # def map_service_messanger(self):
    #     """ Assign backend to all the sales orders """
    #     all_service_message = self.env['service.messanger'].search(
    #         [('backend_id', '!=', self.id)])
    #     for service_message in all_service_message:
    #         backends = []
    #         for backend_id in service_message.backend_id:
    #             backends.append(backend_id.id)
    #         if not self.id in backends:
    #             backends.append(self.id)
    #         service_message.write({'backend_id': [[6, False, backends]]})
    #     return True

    # @api.multi
    # def unmap_service_messanger(self):
    #     """ Remove particular backend from all the products """
    #     all_service_message = self.env['service.messanger'].search(
    #         [('backend_id', '=', self.id)])
    #     for service_message in all_service_message:
    #         backends = []
    #         for backend_id in service_message.backend_id:
    #             if self.id != backend_id.id:
    #                 backends.append(backend_id.id)
    #         service_message.write({'backend_id': [[6, False, backends]]})
    #     return True

    # @api.multi
    # def unmap_product_deal(self):
    #     """ Remove particular backend from all the products """
    #     all_product_deal = self.env['product.deals'].search(
    #         [('backend_id', '=', self.id)])
    #     for product_deal in all_product_deal:
    #         backends = []
    #         for backend_id in product_deal.backend_id:
    #             if self.id != backend_id.id:
    #                 backends.append(backend_id.id)
    #         product_deal.write({'backend_id': [[6, False, backends]]})
    #     return True

    @api.multi
    def unmap_products(self):
        """ Remove particular backend from all the products """
        all_products = self.env['product.template'].search(
            [('backend_id', '=', self.id)])
        for product in all_products:
            backends = []
            for backend_id in product.backend_id:
                if self.id != backend_id.id:
                    backends.append(backend_id.id)
            product.write({'backend_id': [[6, False, backends]]})
        return True

    @api.multi
    def unmap_product_tags(self):
        """ Remove particular backend from all the product tags """
        all_tags = self.env['product.product.tag'].search(
            [('backend_id', '=', self.id)])
        for tag in all_tags:
            backends = []
            for backend_id in tag.backend_id:
                if self.id != backend_id.id:
                    backends.append(backend_id.id)
            tag.write({'backend_id': [[6, False, backends]]})
        return True

    # @api.multi
    # def unmap_product_coupons(self):
    #     """ Remove particular backend from all the product coupons """
    #     all_coupons = self.env['product.coupon'].search(
    #         [('backend_id', '=', self.id)])
    #     for coupon in all_coupons:
    #         backends = []
    #         for backend_id in coupon.backend_id:
    #             if self.id != backend_id.id:
    #                 backends.append(backend_id.id)
    #         coupon.write({'backend_id': [[6, False, backends]]})
    #     return True

    @api.multi
    def unmap_taxes(self):
        """ Remove particular backend from all the taxes """
        all_taxes = self.env['account.tax'].search(
            [('backend_id', '=', self.id)])
        for tax in all_taxes:
            backends = []
            for backend_id in tax.backend_id:
                if self.id != backend_id.id:
                    backends.append(backend_id.id)
            tax.write({'backend_id': [[6, False, backends]]})
        return True

    @api.multi
    def unmap_attributes(self):
        """ Remove particular backend from all the products attributes """
        all_attributes = self.env['product.attribute'].search(
            [('backend_id', '=', self.id)])
        for attribute in all_attributes:
            backends = []
            for backend_id in attribute.backend_id:
                if self.id != backend_id.id:
                    backends.append(backend_id.id)
            attribute.write({'backend_id': [[6, False, backends]]})
        self.unmap_attribute_values()
        return True

    @api.multi
    def unmap_attribute_values(self):
        """ Remove particular backend from all products attribute values """
        all_att_values = self.env['product.attribute.value'].search(
            [('backend_id', '=', self.id)])
        for attr_value in all_att_values:
            backends = []
            for backend_id in attr_value.backend_id:
                if self.id != backend_id.id:
                    backends.append(backend_id.id)
            attr_value.write({'backend_id': [[6, False, backends]]})
        return True

    @api.multi
    def unmap_categories(self):
        """ Remove particular backend from all the categories """
        all_categories = self.env['product.category'].search(
            [('backend_id', '=', self.id)])
        for category in all_categories:
            backends = []
            for backend_id in category.backend_id:
                if self.id != backend_id.id:
                    backends.append(backend_id.id)
            category.write({'backend_id': [[6, False, backends]]})
        return True

    @api.multi
    def unmap_customers(self):
        """ Remove particular backend from all the customers """
        all_customers = self.env['res.partner'].search(
            [('backend_id', '=', self.id)])
        for customer in all_customers:
            backends = []
            for backend_id in customer.backend_id:
                if self.id != backend_id.id:
                    backends.append(backend_id.id)
            customer.write({'backend_id': [[6, False, backends]]})
        return True

    @api.multi
    def unmap_sale_order(self):
        """ Remove particular backend from all the sales orders """
        all_sale_orders = self.env['sale.order'].search(
            [('backend_id', '=', self.id)])
        for sale_order in all_sale_orders:
            backends = []
            for backend_id in sale_order.backend_id:
                if self.id != backend_id.id:
                    backends.append(backend_id.id)
            sale_order.write({'backend_id': [[6, False, backends]]})
        return True

    # @api.multi
    # def unmap_major_unit(self):
    #     """ Remove particular backend from all the sales orders """
    #     all_major_unit = self.env['major_unit.major_unit'].search(
    #         [('backend_id', '=', self.id)])
    #     for major_unit in all_major_unit:
    #         backends = []
    #         for backend_id in major_unit.backend_id:
    #             if self.id != backend_id.id:
    #                 backends.append(backend_id.id)
    #         major_unit.write({'backend_id': [[6, False, backends]]})
    #     return True

    # @api.multi
    # def unmap_service_order(self):
    #     """ Assign backend to all the sales orders """
    #     all_service_order = self.env['service.repair_order'].search(
    #         [('backend_id', '=', self.id)])
    #     for service_order in all_service_order:
    #         backends = []
    #         for backend_id in service_order.backend_id:
    #             if self.id != backend_id.id:
    #                 backends.append(backend_id.id)
    #         service_order.write({'backend_id': [[6, False, backends]]})
    #     return True

    # @api.multi
    # def unmap_pickup_order(self):
    #     """ Assign backend to all the sales orders """
    #     all_pickup_order = self.env['drm.pickup'].search(
    #         [('backend_id', '=', self.id)])
    #     for pickup_order in all_pickup_order:
    #         backends = []
    #         for backend_id in pickup_order.backend_id:
    #             if self.id != backend_id.id:
    #                 backends.append(backend_id.id)
    #         pickup_order.write({'backend_id': [[6, False, backends]]})
    #     return True

    # @api.multi
    # def unmap_standard_job(self):
    #     """ Assign backend to all the sales orders """
    #     all_standard_job = self.env['service.standard_job'].search(
    #         [('backend_id', '=', self.id)])
    #     for standard_job in all_standard_job:
    #         backends = []
    #         for backend_id in standard_job.backend_id:
    #             if self.id != backend_id.id:
    #                 backends.append(backend_id.id)
    #         standard_job.write({'backend_id': [[6, False, backends]]})
    #     return True

    @api.multi
    def export_products(self):
        """ Export all the products of particular backend """
        all_products = self.env['product.template'].search(
            [('backend_id', '=', self.id)])
        export = WpImportExport(self)
        count = (len(all_products)/100)+1
        for offset in xrange(0, int(count)):
            offset = offset*100
            all_products[offset:offset+99].with_delay().export(self)
        return True

    @api.multi
    def export_taxes(self):
        """ Export all the products of particular backend """
        all_taxes = self.env['account.tax'].search(
            [('backend_id', '=', self.id)])
        export = WpImportExport(self)
        count = (len(all_taxes)/100)+1
        for offset in xrange(0, count):
            offset = offset*100
            all_taxes[offset:offset+99].with_delay().export(self, 'standard')
        return True

    @api.multi
    def export_product_tags(self):
        """ Export all the products of particular backend """
        all_product_tags = self.env['product.product.tag'].search(
            [('backend_id', '=', self.id)])
        export = WpImportExport(self)
        count = (len(all_product_tags)/100)+1
        for offset in xrange(0, int(count)):
            offset = offset*100
            all_product_tags[offset:offset+99].with_delay().export(self)
        return True

    @api.multi
    def export_categories(self):
        """ Export all the products of categories backend """
        all_categories = self.env['product.category'].search(
            [('backend_id', '=', self.id)])
        export = WpImportExport(self)
        count = (len(all_categories)/100)+1
        for offset in xrange(0, int(count)):
            offset = offset*100
            all_categories[offset:offset+99].with_delay().export(self)
        return True

    @api.multi
    def export_attributes(self):
        """ Export all the products attributes of particular backend """
        all_attributes = self.env['product.attribute'].search(
            [('backend_id', '=', self.id)])
        export = WpImportExport(self)
        count = (len(all_attributes)/100)+1
        for offset in xrange(0, int(count)):
            offset = offset*100
            all_attributes[offset:offset+99].with_delay().export(self)
        return True

    @api.multi
    def export_customers(self):
        """ Export all the customers of particular backend """
        all_customers = self.env['res.partner'].search(
            [('backend_id', '=', self.id), ('customer', '=', True)])
        export = WpImportExport(self)
        count = (len(all_customers)/100)+1
        for offset in xrange(0, int(count)):
            offset = offset*100
            all_customers[offset:offset+99].with_delay().export(self)
        return True

    @api.multi
    def export_sale_order(self):
        """ Export all the sales orders of particular backend """
        all_sales_orders = self.env['sale.order'].search(
            [('backend_id', '=', self.id)])
        export = WpImportExport(self)
        count = (len(all_sales_orders)/100)+1
        for offset in xrange(0, int(count)):
            offset = offset*100
            all_sales_orders[offset:offset+99].with_delay().export(self)
        return True

    @api.multi
    def export_invoices_refund(self):
        """ Export all the refund invoice orders of particular backend """
        all_invoice_orders = self.env['account.invoice'].search(
            [('backend_id', '=', self.id)])
        export = WpImportExport(self)
        count = (len(all_invoice_orders)/100)+1
        for offset in xrange(0, count):
            offset = offset*100
            all_invoice_orders[offset:offset+99].with_delay().export(self)
        return True

    # @api.multi
    # def export_product_coupons(self):
    #     """Export all coupons of a particular backend"""
    #     all_product_coupons = self.env['product.coupon'].search(
    #         [('backend_id', '=', self.id)])
    #     export = WpImportExport(self)
    #     count = (len(all_product_coupons)/100)+1
    #     for offset in xrange(0, int(count)):
    #         offset = offset*100
    #         coupon[offset:offset+99].with_delay().export(self)
    #     return True

    # @api.multi
    # def export_service_order(self):
    #     """ Export all the refund invoice orders of particular backend """
    #     all_service_order = self.env['service.repair_order'].search(
    #         [('backend_id', '=', self.id)])
    #     export = WpImportExport(self)
    #     count = (len(all_service_order)/100)+1
    #     for offset in xrange(0, count):
    #         offset = offset*100
    #         service_order[offset:offset+99].with_delay().export(self)
    #     return True

    # @api.multi
    # def export_pickup_order(self):
    #     """ Export all the refund invoice orders of particular backend """
    #     all_pickup_order = self.env['drm.pickup'].search(
    #         [('backend_id', '=', self.id)])
    #     export = WpImportExport(self)
    #     count = (len(all_pickup_order)/100)+1
    #     for offset in xrange(0, count):
    #         offset = offset*100
    #         pickup_order[offset:offset+99].with_delay().export(self)
    #     return True

    # @api.multi
    # def export_standard_job(self):
    #     """ Export all the refund invoice orders of particular backend """
    #     all_standard_job = self.env['service.standard_job'].search(
    #         [('backend_id', '=', self.id)])
    #     export = WpImportExport(self)
    #     count = (len(all_standard_job)/100)+1
    #     for offset in xrange(0, count):
    #         offset = offset*100
    #         standard_job[offset:offset+99].with_delay().export(self)
    #     return True

    # @api.multi
    # def run_campaign(self):
    #     """ Export all the refund invoice orders of particular backend """
    #     all_campaign = self.env['product.deals'].search([])
    #     export = WpImportExport(self)
    #     all_campaign.with_delay().run_campaign(self)
    #     return True

    # @api.multi
    # def import_sale_orders(self):
    #     """ Import all the sale order of particular backend """
    #     sale_order_obj = self.env['sale.order']
    #     sale_order_obj.with_delay().importer(self)
    #     return True

    # @api.multi
    # def import_customer(self):
    #     """Import all the customers of particular backend"""
    #     customer_obj = self.env['res.partner']
    #     customer_obj.with_delay().importer(self)
    #     return True

    # @api.multi
    # def import_tax(self):
    #     """Import all the taxes of particular backend"""
    #     tax_obj = self.env['account.tax']
    #     tax_obj.with_delay().importer(self)
    #     return True

    # @api.multi
    # def import_form(self):
    #     """Import all the customers of particular backend"""
    #     form_obj = self.env['crm.lead']
    #     form_obj.with_delay().importer(self)
    #     return True

    # @api.multi
    # def export_status(self):
    #     """ Export the status of crm_lead of particular backend """
    #     crm_status = self.env['crm.lead'].search(
    #         [('backend_id','=',self.id)])
    #     export = WpImportExport(self)
    #     count = (len(crm_status)/100) + 1
    #     for offset in xrange(0,count):
    #         offset = offset*100
    #         crm_status[offset:offset+99].with_delay().export(self)
    #     return True

    # @api.multi
    # def import_service_rides(self):
    #     """Import all the customers of particular backend"""
    #     repair_order_obj = self.env['service.repair_order']
    #     repair_order_obj.with_delay().importer(self)
    #     return True

    # @api.multi
    # def import_major_units(self):
    #     """Import all the major_units of particular backend"""
    #     major_unit_obj = self.env['major_unit.major_unit']
    #     major_unit_obj.with_delay().importer(self)
    #     return True

    # @api.multi
    # def import_product_deals(self):
    #     """Import all the product deals of particular backend"""
    #     product_deal = self.env['product.deals']
    #     product_deal.with_delay().importer(self)
    #     return True