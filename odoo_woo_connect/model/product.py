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

import logging

# import xmlrpclib
from collections import defaultdict
from odoo.addons.queue_job.job import job
from datetime import datetime
import base64
from odoo import models, fields, api, _
from ..unit.product_exporter import WpProductExport
from ..unit.product_variation_exporter import WpProductVariationExport
from ..unit.product_tag_exporter import WpProductTagExport
from odoo.exceptions import Warning
import re
_logger = logging.getLogger(__name__)


class ProductTags(models.Model):

    """ Models for product tags """
    _name = "product.product.tag"
    _order = 'sequence, name'

    sequence = fields.Integer('Sequence', help="Determine the display order")
    name = fields.Char(string="Name")
    slug = fields.Char(string="Slug")
    desc = fields.Text(string="Description")
    product_id = fields.Many2one(comodel_name='product.template',
                                 string='Product')
    backend_mapping = fields.One2many(comodel_name='wordpress.odoo.product.tag',
                                      string='Product tag mapping',
                                      inverse_name='product_tag_id',
                                      readonly=False,
                                      required=False,)

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

    @api.model
    def create(self, vals):
        """ Override create method """
        backend_obj = self.env['wordpress.configure']
        backend_ids = backend_obj.search([('name', '!=', None)])
        vals['backend_id'] = [[6, 0, backend_ids.ids]]
        tag_id = super(ProductTags, self).create(vals)
        return tag_id

    @api.multi
    def sync_tag(self):
        for backend in self.backend_id:
            self.with_delay().export(backend)
        return

    @api.multi
    @job
    def export(self, backend):
        """ export product attributes, save slug and create or update backend mapper """
        if len(self.ids) > 1:
            for obj in self:
                obj.with_delay().export(backend)
            return
        method = 'tag'
        mapper = self.backend_mapping.search(
            [('backend_id', '=', backend.id), ('product_tag_id', '=', self.id)], limit=1)
        export = WpProductTagExport(backend)
        arguments = [mapper.woo_id or None, self]
        res = export.export_product_tag(method, arguments)
        if mapper and (res['status'] == 200 or res['status'] == 201):
            self.write({'slug': res['data']['slug']})
            mapper.write(
                {'product_tag_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['id']})
        elif (res['status'] == 200 or res['status'] == 201):
            self.write({'slug': res['data']['slug']})
            backend_mapping = self.backend_mapping.create(
                {'product_tag_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['id']})
        elif (res['status'] == 400 and res['data']['code'] == 'term_exists'):
            if 'resource_id' in res['data']['data'].keys():
                backend_mapping = self.backend_mapping.create(
                    {'product_tag_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['data']['resource_id']})
        # return backend_mapping

class ProductTagMapping(models.Model):

    """ Model to store woocommerce id for particular product"""
    _name = 'wordpress.odoo.product.tag'
    product_tag_id = fields.Many2one(comodel_name='product.product.tag',
                                     string='Product tag',
                                     ondelete='cascade',
                                     readonly=False,
                                     required=True,)

    backend_id = fields.Many2one(comodel_name='wordpress.configure',
                                 string='Website',
                                 ondelete='set null',
                                 store=True,
                                 readonly=False,
                                 required=False,)

    woo_id = fields.Char(string='Woo id')


class ProductMultiImages(models.Model):

    """ Models for product images """
    _inherit = "product.image"
    sequence = fields.Integer(string="Seq")
    default = fields.Boolean(string="Main Product Image")
    woo_id = fields.Char(string="Woo id")
    product_id = fields.Many2one(comodel_name='product.product',
                                 string='Product')
    position = fields.Integer(string="Position")
    src = fields.Char(string="Source")
    backend_mapping = fields.One2many(comodel_name='wordpress.odoo.product.image',
                                      string='Product Image mapping',
                                      inverse_name='product_image_id',
                                      readonly=False,
                                      required=False,)
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

    @api.model
    def create(self, vals):
        if 'image' in vals.keys():
              name=str(vals['name']).split(".")[0]
              vals['name']=name
        return super(ProductMultiImages, self).create(vals)


class ProductImageMapping(models.Model):

    """ Model to store woocommerce id for particular product"""
    _name = 'wordpress.odoo.product.image'
    product_id = fields.Many2one(comodel_name='product.product',
                                 string='Product',
                                 ondelete='cascade',
                                 readonly=False,
                                 required=True,)
    product_image_id = fields.Many2one(comodel_name='product.image',
                                       string='Product image',
                                       ondelete='cascade',
                                       readonly=False,
                                       required=True,)

    backend_id = fields.Many2one(comodel_name='wordpress.configure',
                                 string='Website',
                                 ondelete='set null',
                                 store=True,
                                 readonly=False,
                                 required=False,)

    woo_id = fields.Char(string='Woo id')


class ProductTemplate(models.Model):

    """ Models for woocommerce product template """
    _inherit = 'product.template'

    website_published = fields.Boolean()
    from_wp = fields.Boolean('from_wp')
    superseded_t = fields.Many2one(comodel_name='product.template.details', string='Superseded Part No')
    @api.model
    def get_categ_ids(self):
        return self.env['product.category'].search([('slug', '=', 'all')])

   


    categ_ids = fields.Many2many(comodel_name='product.category',
                                 relation='product_categ_rel',
                                 column1='product_id',
                                 column2='categ_id',
                                 string='Product Categories',
                                 default=get_categ_ids)
    image_ids = fields.One2many(related='product_variant_ids.image_ids',
                                string='Product Images')
    tag_ids = fields.Many2many(comodel_name='product.product.tag',
                               inverse_name='product_id',
                               string='Product Tags')
    short_description = fields.Text('Short Description')
    product_status = fields.Selection([('pending', 'Pending Review'),
                                       ('draft', 'Draft'),
                                       ('publish', 'Publish')],
                                      'Status',
                                      default='publish')
    slug = fields.Char('Slug')
    list_price = fields.Float('Sales Price')
    regular_price = fields.Float('Regular Price')
    standard_price = fields.Float('Purchase Price')
    wp_managing_stock = fields.Boolean('WP Managing Stock')

    dimention_unit = fields.Many2one(comodel_name='product.uom',
                                     string='Dimention Unit',
                                     ondelete='set null')
    website_size_x = fields.Integer('Length')
    website_size_y = fields.Integer('Width')
    website_size_z = fields.Integer('Height')

    backend_mapping = fields.One2many(comodel_name='wordpress.odoo.product.template',
                                      string='Product mapping',
                                      inverse_name='product_id',
                                      readonly=False,
                                      required=False,
                                      )
    vin=fields.Char()
    enable_deposit = fields.Boolean(string="Enable Deposit", default=False)
    type_of_deposit = fields.Selection([('fixed','Fixed Value'),
                                        ('percent','Percentage Of Price')])
    deposit_amount = fields.Float(string='Deposite Amount')
    _sql_constraints = [ ('part_number_unique', 'unique(part_number)', 'part number already exists!') ]
    location_id=fields.Many2many(comodel_name='stock.location',
                                 column1='product_id',
                                 column2='categ_id',
                                 string='location',
                               )

    tax_status = fields.Selection([('taxable','Taxable'),
                                    ('none','None')],
                                    default='none',
                                    required=True )
    tax_class = fields.Selection([('standard','Standard rates'),
                                  ('showroom','Showroom rates'),
                                  ('accessories','Accessories rates'),
                                  ('apparel','Apparel rates'),
                                  ('parts','Parts rates'),
                                  ('service', 'Service rates'),
                                  ('deals','Deals rates')],
                                  default='standard',
                                  required=True)
    msrp = fields.Float(string='MSRP',
                       help='Manufacturer’s suggested Retail Price')

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

    type = fields.Selection([
        ('consu', _('Consumable')),
        ('service', _('Service')),
        ('product', 'Stockable Product')], string='Product Type', default='product', required=True,
        help='A stockable product is a product for which you manage stock. The "Inventory" app has to be installed.\n'
             'A consumable product, on the other hand, is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.\n'
             'A digital content is a non-material product you sell online. The files attached to the products are the one that are sold on '
             'the e-commerce such as e-books, music, pictures,... The "Digital Product" module has to be installed.')
    item_number = fields.Char(string="Part Number / Item Number")

    warranty = fields.Float('Warranty')
  
    sale_delay = fields.Float(
        'Customer Lead Time', default=0)
    

    _sql_constraints = [('item_number_unique', 'unique(item_number)', 'item_number already exists!')]

     
    @api.multi
    @api.onchange('details_model')
    def enable_deposit_on_vehicle(self):
        if self.details_model == 'nadanew.vehicle.product' :
            self.enable_deposit = True
            self.type_of_deposit = 'fixed'
            self.deposit_amount = 500.0
        else:
            self.enable_deposit = False


    @api.multi
    def wp_price_check(self, regular_price, list_price, context=None):
        """ Check sales price and regular price """
        if regular_price < list_price:
            res = {'warning': {
                'title': _('Warning'),
                'message': _('Regular Price should be greater than Sales Price'),
            }
            }
            return res
        res = {'value': {
            'list_price': list_price,
            'regular_price': regular_price,
              }
        }
        return res

    @api.model
    def create(self, vals):
        import pdb;pdb.set_trace()
        """ Override create method to check price before creating and export """
        if 'description' in vals:
          if vals['description']=='Setup Charges' or vals['description']=='Document Fees' or vals['description']=='Freight Charges':
              categ_obj = self.env['product.category'].search([('name','=','ignore-cart-count')])

              product_id = super(ProductTemplate, self).create(vals)
              product_id.categ_ids=categ_obj
              return product_id
 
        attribute_id = self.env['product.attribute'].search([('name', '=ilike', 'Categories')])
        if not attribute_id:
            attribute_id = self.env['product.attribute'].create({'name': 'Categories', 'create_variant': False})
        value_ids = []
        if 'categ_ids' in vals:
            categ_obj = self.env['product.category'].search([('id', 'in', vals['categ_ids'][0][2])])
            for category in categ_obj:
                value_id = self.env['product.attribute.value'].search([('name', '=ilike', category.name)],limit=1)
                if not value_id:
                    value_id = self.env['product.attribute.value'].create({'attribute_id': attribute_id.id, 'name': category.name})
                value_ids.append(value_id.id)
            if 'attribute_line_ids' in vals.keys():
                vals['attribute_line_ids'].append([0, False, {'attribute_id': attribute_id.id, 'value_ids': [[6, False, value_ids]]}])
        #location attribute values    
        if 'company_id' in vals:
          location_attr=self.env['product.attribute'].search([('name', '=ilike', 'Location')])
          if not location_attr:
            location_attr = self.env['product.attribute'].create({'name': 'Location', 'create_variant': False})
          location_vals=[]  
          location_ids=self.env['stock.location'].search([('company_id','=',vals['company_id'])])
          for location in location_ids:
              loc_id = self.env['product.attribute.value'].search([('name', '=ilike', location.name)],limit=1)
              if not loc_id:
                      loc_id = self.env['product.attribute.value'].create({'attribute_id': location_attr.id, 'name': location.name})
              location_vals.append(loc_id.id)    
          if 'attribute_line_ids' in vals.keys():
              vals['attribute_line_ids'].append([0, False, {'attribute_id': location_attr.id,  'value_ids': [[6, False, [location_vals[0]]]]}])
          else:
              vals['attribute_line_ids'] = [[0, False, {
                  'attribute_id': location_attr.id,  'value_ids': [[6, False, [location_vals[0]]]]}]]
        if 'list_price' in vals.keys() and 'regular_price' in vals.keys():

            check = self.wp_price_check(vals['regular_price'], vals['list_price'], None)
            if 'warning' in check:
                raise Warning(check['warning']['message'])

        product_id = super(ProductTemplate, self).create(vals)
        return product_id

    @api.multi
    def write(self, vals):
        """ Override write method to export when any details is changed """
        if self.name and self.name=='Setup Charges' or self.name=='Freight Charges' or self.name=='Document Fees':
          product = super(ProductTemplate, self).write(vals)
          return product
        else:
          attribute_line_ids = []
          if 'categ_ids' in vals:
              attribute_id = self.env['product.attribute'].search([('name', '=ilike', 'Categories')])
              if not attribute_id:
                  attribute_id = self.env['product.attribute'].create({'name': 'Categories', 'create_variant': False})
              value_ids = []
              categ_obj = self.env['product.category'].search([('id', 'in', vals['categ_ids'][0][2])])
              for category in categ_obj:
                  value_id = self.env['product.attribute.value'].search([('name', '=ilike', category.name)])
                  if not value_id:
                      value_id = self.env['product.attribute.value'].create({'attribute_id': attribute_id.id,
                                                                             'name': category.name})
                  value_ids.append(value_id.id)
              attribute_line_id = self.env['product.attribute.line'].search([('attribute_id', '=', attribute_id.id),
                                                                             ('product_tmpl_id', '=', self.id)])
              if attribute_line_id:
                  attribute_line_id.update({'value_ids': [[6, False, value_ids]]})
              else:
                  attribute_line_ids.append([0, 0, {'attribute_id': attribute_id.id,
                                                    'value_ids': [[6, False, value_ids]]}])
                  self.write({'attribute_line_ids': attribute_line_ids})        
          if (self.backend_id or 'backend_id' in vals.keys()) and not ('default_code' in vals.keys() or 'slug' in vals.keys()):
              if 'regular_price' in vals.keys() and 'list_price' in vals.keys():
                  check = self.wp_price_check(vals['regular_price'], vals['list_price'], None)
                  if 'warning' in check:
                      raise Warning(check['warning']['message'])
              
              product = super(ProductTemplate, self).write(vals)
          else:
              product = super(ProductTemplate, self).write(vals)
          #passing msrp and minap values to product variant
        #   if self.product_variant_ids:
        #       for var in self.product_variant_ids:
        #         var.minap=self.minap
        #         var.msrp=self.msrp
          return product

    @api.multi
    def sync_product(self):
      for backend in self.backend_id:
          self.with_delay().export(backend)
      return

    @api.multi
    @job
    def export(self, backend):
        """ export product details, save default code & slug and create or update backend mapper """
        if len(self.ids) > 1:
            for obj in self:
                obj.with_delay().export(backend)
            return
        if self.details_model=='nadanew.vehicle.product':
          pp=self.env['product.product'].search([('product_tmpl_id','=',self.id)])
          mu=self.env['major_unit.major_unit'].search([('product_id','in',pp.ids)])
          for backend in self.backend_id:
            for m in mu:
              if m.partner_id:
                m.with_delay().export(backend)
              else:
                m.with_delay().export_mu_pro(backend)
        else:
          mapper = self.backend_mapping.search(
              [('backend_id', '=', backend.id), ('product_id', '=', self.id)], limit=1)
          arguments = []
          method = 'products'
          arguments = [mapper.woo_id or None, self]
          export = WpProductExport(backend)
          if arguments[1].customer_owned:
            return True
          else:
            res = export.export_product(method, arguments)
            if mapper and (res['status'] == 200 or res['status'] == 201):
                self.write(
                    {'default_code': res['data']['sku'], 'slug': res['data']['slug']})
                mapper.write({'product_id': self.id, 'backend_id': backend.id, 'woo_id': res[
                             'data']['id'], 'image_id': res['data']['images'][0]['id'],
                             'motorcycle_image_id':res['data']['motorcycle_image']['id'],
                             })

                self.map_images(res, backend)
            elif (res['status'] == 200 or res['status'] == 201):
                self.write(
                    {'default_code': res['data']['sku'], 'slug': res['data']['slug']})
                self.backend_mapping.create({'product_id': self.id, 'backend_id': backend.id, 'woo_id': res[
                                            'data']['id'], 'image_id': res['data']['images'][0]['id'],
                                            'motorcycle_image_id':res['data']['motorcycle_image']['id'],
                                            })
                self.map_images(res, backend)
            if self.product_variant_count > 1:
                self.export_variation(res['data']['id'], backend)

    def export_variation(self, parent_woo_id, backend):
        if len(self.ids) > 1:
            for obj in self:
                obj.with_delay().export_variation(backend)
            return

        for variant in self.product_variant_ids:
            mapper = variant.backend_mapping.search(
                [('backend_id', '=', backend.id), ('product_id', '=', variant.id)], limit=1)
            arguments = []
            method = 'variation'
            arguments = [parent_woo_id, variant, mapper.woo_id or None]
            export = WpProductVariationExport(backend)
            res = export.export_product_variant(method, arguments)
            if mapper and (res['status'] == 200 or res['status'] == 201):
                variant.write({'default_code': res['data']['sku']})
                mapper.write({'product_id': variant.id, 'backend_id': backend.id,
                              'woo_id': res['data']['id'], 'image_id': res['data']['image']['id']})
            elif (res['status'] == 200 or res['status'] == 201):
                variant.write({'default_code': res['data']['sku']})
                mapper.create({'product_id': variant.id, 'backend_id': backend.id,
                               'woo_id': res['data']['id'], 'image_id': res['data']['image']['id']})

    def map_images(self, res, backend):
        """ map product images with particular woo id and create or update backend mapper"""
        if res['data']['images']:
            for image_data in res['data']['images']:
                if image_data['id'] != 0:
                    if image_data['position'] != 0:
                        image_id = self.get_image_id(
                            self.image_ids, image_data, backend)
                        if not image_id:
                            continue
                        mapper = image_id.backend_mapping.search([('backend_id', '=', backend.id),
                                                                  ('product_image_id',
                                                                   '=', image_id.id),
                                                                  ('woo_id', '=', int(image_data['id']))],
                                                                 limit=1)
                        if not mapper:
                            mapper.create({'product_image_id': image_id.id,
                                           'product_id': self.id,
                                           'backend_id': backend.id,
                                           'woo_id': int(image_data['id'])})
                        else:
                            mapper.write({'product_image_id': image_id.id,
                                          'product_id': self.id,
                                          'backend_id': backend.id,
                                          'woo_id': int(image_data['id'])})
        return True

    def get_image_id(self, image_ids, record, backend):
        """ check and get the correct variant for particular woo id"""
        for image_id in image_ids:
            if record['position'] == image_id.sequence:
                return image_id

    @api.multi
    def update_stock(self, vals):
        """ Changes the Product Quantity by making a Physical Inventory. """
        update_stock_id = self.env['stock.change.product.qty'].create({'product_tmpl_id': vals['product_tmpl_id'],
                                                                       'lot_id': False,
                                                                       'product_id': vals['product_id'],
                                                                       'new_quantity': vals['new_quantity'],
                                                                       'location_id': vals['location_id'],
                                                                       'product_variant_count': vals['product_variant_count']})
        update_stock_id.change_product_qty()
        return True

    @api.multi
    def variant_from_wp(self, vals):
        """ Create varients from wordpress  """
        self.create_variant_ids()
        return True


class ProductMapping(models.Model):

    """ Model to store woocommerce id for particular product"""
    _name = 'wordpress.odoo.product.template'

    product_id = fields.Many2one(comodel_name='product.template',
                                 string='Product Template',
                                 ondelete='cascade',
                                 readonly=False,
                                 required=True,
                                 )

    image_id = fields.Char('Image id')
    motorcycle_image_id = fields.Char('Motor Cycle Image id')

    backend_id = fields.Many2one(comodel_name='wordpress.configure',
                                 string='Website',
                                 ondelete='set null',
                                 store=True,
                                 readonly=False,
                                 required=False,
                                 )

    woo_id = fields.Char(string='Woo id')


class ProductProduct(models.Model):

    """ Models for woocommerce product variant """
    _inherit = 'product.product'

    woo_id = fields.Char(string='Woo id')
    image_ids = fields.One2many(comodel_name='product.image',
                                inverse_name='product_id',
                                string='Product Images')
    variant_regular_price = fields.Float('Variant Regular Price', related='regular_price')
    website_size_x = fields.Integer('Length')
    website_size_y = fields.Integer('Width')
    website_size_z = fields.Integer('Height')
    wp_managing_stock = fields.Boolean('WP Managing Stock')

    backend_mapping = fields.One2many(comodel_name='wordpress.odoo.product.product',
                                      string='Product mapping',
                                      inverse_name='product_id',
                                      readonly=False,
                                      required=False,
                                      )
    schedule_sale1=fields.Boolean(string='Schedule Sale')
    schedule_date_start1=fields.Date(string='Schedule start date', default=datetime.today())
    schedule_date_end1=fields.Date(string='Schedule end date', default=datetime.today())

    @api.model
    def create(self, vals):
        """ Override create method """
        if 'image_ids' in vals.keys():
          for image in vals['image_ids'] :
            if image[2]!= False:
              name=str(image[2]['name']).split(".")[0]
              image[2]['name']=name
        return super(ProductProduct, self).create(vals)

    @api.multi
    def write(self, vals):
        """ Override write method to export when any details is changed """
        if 'image_ids' in vals.keys():
          for image in vals['image_ids'] :
            if image[2]!= False:
              name=str(image[2]['name']).split(".")[0]
              image[2]['name']=name     
        return super(ProductProduct, self).write(vals)

    @api.multi
    def sync_product(self):
        for backend in self.product_tmpl_id.backend_id:
            self.product_tmpl_id.with_delay().export(backend)
        return

    @api.multi
    @job
    def export(self, backend):
        """ export product variant details, and create or update backend mapper """
        if len(self.ids) > 1:
            for obj in self:
                obj.with_delay().export(backend)
            return
        return self.product_tmpl_id.export(backend)

    @api.multi
    def wp_price_check(self, lst_price, variant_sale_price, context=None):
        """ Check sales price and regular price """

        if lst_price < variant_sale_price:
            res = {'warning': {
                'title': _('Warning'),
                'message': _('Variant regular price should be greater than Variant sale price'),
            }
            }
            return res

        res = {'value': {
            'lst_price': lst_price,
            'variant_sale_price': variant_sale_price,
        }
        }
        return res

    @api.multi
    def _website_price(self):
        try:
            res = super(ProductProduct, self)._website_price()
        except RuntimeError:
            pass


class ProductProductMapping(models.Model):

    """ Model to store woocommerce id for particular product variant"""
    _name = 'wordpress.odoo.product.product'

    product_id = fields.Many2one(comodel_name='product.product',
                                 string='Product',
                                 ondelete='cascade',
                                 readonly=False,
                                 required=True,
                                 )

    image_id = fields.Char('Image id')

    backend_id = fields.Many2one(comodel_name='wordpress.configure',
                                 string='Website',
                                 ondelete='set null',
                                 store=True,
                                 readonly=False,
                                 required=False,
                                 )

    woo_id = fields.Char(string='Woo id')