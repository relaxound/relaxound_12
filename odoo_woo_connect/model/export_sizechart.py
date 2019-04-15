from odoo import api, fields, models
from odoo.addons.queue_job.job import job
import odoo.addons.decimal_precision as dp
# from ..unit.product_deals_exporter import WpProductDealExport
# from ..unit.product_deals_importer import WpProductDealImport


class SizeChart(models.Model):

    """ Models for woocommerce product category """
    _inherit = 'all.sizechart'

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
    backend_mapping = fields.One2many(comodel_name='wordpress.odoo.sizechart',
                                      string='SizeChart mapping',
                                      inverse_name='sizechart_id',
                                      readonly=False,
                                      required=False,
                                      )
    @api.multi
    def sync_sizechart(self):
      for backend in self.backend_id:
          self.with_delay().export(backend)
      return

    @api.multi
    @job
    def export(self, backend):
        """ export customer details, save username and create or update backend mapper """
        if len(self.ids) > 1:
            for obj in self:
                obj.with_delay().export(backend)
            return
        mapper = self.backend_mapping.search(
            [('backend_id', '=', backend.id), ('sizechart_id', '=', self.id)])
        method = 'sizechart'                                                        # confused!!!!
        arguments = [mapper.woo_id or None, self]

        
        # export = WpProductDealExport(backend)
        # res = export.export_product_deal(method, arguments)

        # if mapper and (res['status'] == 200 or res['status'] == 201):
        #     mapper.write({'sizechart_id': self.id,
        #                   'backend_id': backend.id,
        #                   'woo_id': mapper.woo_id,
        #                   'banner_image':res['data']['banner_image'],
        #                   'featured_image':res['data']['feature_image']
        #                   })
        # elif (res['status'] == 200 or res['status'] == 201):
        #     self.backend_mapping.create({'sizechart_id': self.id,
        #                                 'backend_id': backend.id,
        #                                 'woo_id': res['data']['id'],
        #                                 'banner_image':res['data']['banner_image'],
        #                                 'featured_image':res['data']['feature_image']
        #                                 })

class SizeChartMapping(models.Model):

    """ Model to store woocommerce id for particular Size Chart category"""
    _name = 'wordpress.odoo.sizechart'

    sizechart_id = fields.Many2one(comodel_name='all.sizechart',
                                     string='Size Chart',
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