from odoo import api, fields, models
import odoo.addons.decimal_precision as dp
from ..unit.standard_job_exporter import StandardJobExport
from odoo.addons.queue_job.job import job
from odoo.exceptions import Warning

class StandardJob(models.Model):

    """ Models for woocommerce product category """
    _inherit = 'service.standard_job'

    @api.model
    def get_backend(self):
        return self.env['wordpress.configure'].search([]).ids
    backend_id = fields.Many2many(comodel_name='wordpress.configure',
                                  string='Website',
                                  store=True,
                                  readonly=False,
                                  required=True,
                                  default=get_backend,
                                  )
    backend_mapping = fields.One2many(comodel_name='wordpress.odoo.service.standard_job',
                                      string='Standard Job mapping',
                                      inverse_name='standard_job_id',
                                      readonly=False,
                                      required=False,
                                      )
    warehouse = fields.Many2many(comodel_name='stock.warehouse',string='Warehouse',readonly=True,compute='_com_warehouse')

    @api.depends('store_location')
    def _com_warehouse(self):
      loc = self.env['stock.location'].search([('name','=',self.store_location.name)])
      ware = self.env['stock.warehouse'].search([('company_id','=',loc.company_id.id)])
      self.warehouse = ware

    

    @api.multi
    def sync_standard_job(self):
        print("sync")
        for backend in self.backend_id:
            self.with_delay().export(backend)
        return

    @api.multi
    def build_product(self):
      o=self.env['product.template'].search([('name','=',self.name)])
      if not o:
        values={
        'name':self.name,
        'details_model':"other",
        'type':'consu'
        }
        obj=self.env['product.template'].create(values)

        values1=[(0,0, {'product_id':x.product_id.id,'product_qty':x.quantity}) for x in self.product_ids]
        self.env['mrp.bom'].create({'product_tmpl_id':obj.id,'bom_line_ids':values1})
      else:
        raise Warning("Product is already created")

    @api.multi
    @job
    def export(self, backend):
        """ export customer details, save username and create or update backend mapper """
        if len(self.ids) > 1:
            for obj in self:
                obj.with_delay().export(backend)
            return
        mapper = self.backend_mapping.search(
            [('backend_id', '=', backend.id), ('standard_job_id', '=', self.id)])
        method = 'products'
        arguments = [mapper.woo_id or None, self]
        export = StandardJobExport(backend)
        res = export.export_standard_job(method, arguments)

        if mapper and (res['status'] == 200 or res['status'] == 201):
            self.write({'slug': res['data']['slug']})
            mapper.write(
                {'standard_job_id': self.id,
                'backend_id': backend.id,
                'woo_id': res['data']['id'],
                # 'std_job_image':res['data']['service_images']
                })
        elif (res['status'] == 200 or res['status'] == 201):
            self.write({'slug': res['data']['slug']})
            self.backend_mapping.create(
                {'standard_job_id': self.id,
                'backend_id': backend.id,
                'woo_id': res['data']['id'],
                # 'std_job_image':res['data']['service_images']
                })


class ServiceRidesMapping(models.Model):

    """ Model to store woocommerce id for particular product category"""
    _name = 'wordpress.odoo.service.standard_job'

    standard_job_id = fields.Many2one(comodel_name='service.standard_job',
                                      string='Standard Job',
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
    std_job_image = fields.Char(string="Standard Job Image")
