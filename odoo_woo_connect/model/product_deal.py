from odoo import api, fields, models,_
from odoo.addons.queue_job.job import job
import odoo.addons.decimal_precision as dp
from ..unit.product_deals_exporter import WpProductDealExport
from odoo.exceptions import Warning
class ProductDeal(models.Model):

    """ Models for woocommerce product category """
    _inherit = 'product.deals'

    woo_id = fields.Char(string='woo_id')

    @api.model
    def get_backend(self):
        return self.env['wordpress.configure'].search([]).ids
    backend_id = fields.Many2many(comodel_name='wordpress.configure',
                                  string='Website',
                                  store=True,
                                  readonly=False,
                                  required=False,
                                  default=get_backend,
                                  )
    backend_mapping = fields.One2many(comodel_name='wordpress.odoo.productdeal',
                                      string='ProductDeal mapping',
                                      inverse_name='productdeal_id',
                                      readonly=False,
                                      required=False,
                                      )

    @api.multi
    def sync_product_deals(self):
        for backend in self.backend_id:
            self.with_delay().export(backend)
        return

    @api.multi
    def sync_product_deals_multiple(self):
        for product in self:
            if product:
                for backend in product.backend_id:
                    product.with_delay().export(backend)
        return

                
    # @api.multi
    # @job
    # def importer(self, backend):
    #     """ import and create or update backend mapper """
    #     if len(self.ids) > 1:
    #         for obj in self:
    #             obj.with_delay().single_importer(backend)
    #         return

    #     method = 'campaign'
    #     arguments = [None, self]
    #     importer = WpProductDealImport(backend)
    #     res = importer.import_product_deals(method, arguments)

    #     if (res['status'] == 200 or res['status'] == 201):
    #         if isinstance(res['data']['my_services'], list):
    #             for service_id in res['data']['my_services']:
    #                 self.with_delay().single_importer(backend, service_id)

    # @api.multi
    # @job
    # def single_importer(self, backend, deal_id, woo_id=None):
    #     method = 'campaign'

    #     mapper = self.backend_mapping.search(
    #         [('backend_id', '=', backend.id), ('woo_id', '=', deal_id)], limit=1)
    #     arguments = [deal_id or None, mapper.productdeal_id or self]

    #     importer = WpProductDealImport(backend)
    #     res = importer.import_product_deals(method, arguments)

    #     if mapper:
    #         importer.write_product_deals(
    #             backend, mapper, res)
    #     else:
    #         product_deal_id = importer.create_product_deals(
    #             backend, mapper, res)

    #     if mapper and (res['status'] == 200 or res['status'] == 201):
    #         vals = {
    #             'woo_id': ,
    #             'backend_id': backend.id,
    #             'service_rides_id': mapper.productdeal_id.id,
    #         }
    #         self.backend_mapping.write(vals)
    #     elif service_rides_id:
    #         vals = {
    #             'woo_id': ,
    #             'backend_id': backend.id,
    #             'service_rides_id': product_deal_id.id,
    #         }
    #         self.backend_mapping.create(vals)

    @api.multi
    @job
    def export(self, backend):
        """ export customer details, save username and create or update backend mapper """
        if len(self.ids) > 1:
            for obj in self:
                obj.with_delay().export(backend)
            return
        mapper = self.backend_mapping.search(
            [('backend_id', '=', backend.id), ('productdeal_id', '=', self.id)])
        method = 'campaign'
        arguments = [mapper.woo_id or None, self]
        export = WpProductDealExport(backend)
        res = export.export_product_deal(method, arguments)
        if mapper and (res['status'] == 200 or res['status'] == 201):
            mapper.write({'productdeal_id': self.id,
                          'backend_id': backend.id,
                          'woo_id': mapper.woo_id,
                          'banner_image': res['data']['banner_image'],
                          'featured_image': res['data']['feature_image']
                          })
        elif (res['status'] == 200 or res['status'] == 201):
            self.backend_mapping.create({'productdeal_id': self.id,
                                         'backend_id': backend.id,
                                         'woo_id': res['data']['id'],
                                         'banner_image': res['data']['banner_image'],
                                         'featured_image': res['data']['feature_image']
                                         })

    @api.multi
    @job
    def run_campaign(self, backend):
        """ export customer details, save username and create or update backend mapper """
        method = 'campaign'
        export = WpProductDealExport(backend)
        res = export.run_product_deal(method)


class ProductDealMapping(models.Model):

    """ Model to store woocommerce id for particular product category"""
    _name = 'wordpress.odoo.productdeal'

    productdeal_id = fields.Many2one(comodel_name='product.deals',
                                     string='Product Deals',
                                     ondelete='cascade',
                                     readonly=False,
                                     required=True,
                                     )

    backend_id = fields.Many2one(comodel_name='wordpress.configure',
                                 string='Website',
                                 ondelete='set null',
                                 store=True,
                                 readonly=False,
                                 required=False,
                                 )
    woo_id = fields.Char(string='woo_id')
    featured_image = fields.Char(string="Featured Image")
    banner_image = fields.Char(string="Banner Image")
