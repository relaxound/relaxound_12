from odoo import api, fields, models
from odoo.addons.queue_job.job import job
import odoo.addons.decimal_precision as dp
from ..unit.major_unit_exporter import WpMajorUnitExport
from ..unit.major_unit_importer import WpMajorUnitImport
from ..unit.major_unit_product_exporter import WpMajorProductExport
from odoo.exceptions import UserError
from lxml import etree

class MajorUnit(models.Model):

    """ Models for woocommerce product category """
    _inherit = 'major_unit.major_unit'

    image_id = fields.Char('Image id')
    slug = fields.Char('Slug')
    image = fields.Binary("Image",help="This field holds the image used as image for the cateogry")
    woo_id = fields.Char(string='woo_id')
    mu_name = fields.Char(compute="_compute_major_unit_name_mu", store=True)
    sales_price=fields.Float("Sales price", related='product_id.product_tmpl_id.list_price')
    minap= fields.Float(string = 'Minimum Advertising Price' ,related='product_id.product_tmpl_id.minap')
    regular_price= fields.Float(string = 'Regular Price',related='product_id.product_tmpl_id.regular_price')
    msrp=fields.Float(string='MSRP',related='product_id.product_tmpl_id.msrp')
    manufacturer_ids=fields.One2many('major_unit.manufacturer', 'major_unit_id', string='Finance and Insurance')
    manufacturer_charges=fields.Float(string="Manufacturer Charges",compute="_compute_extra_charges")
    financing_charges=fields.Float(string='Financing Charges',compute="_compute_extra_charges")
    setup_charges_total=fields.Float(string='Setup Charges', compute="_compute_extra_charges" )
    free_flooring_end=fields.Datetime(string="Free Flooring End")
    @api.multi
    @api.depends('prod_lot_id', 'prod_lot_id.name', 'prod_lot_id.product_id',
                 'prod_lot_id.product_id.attribute_value_ids')
    def _compute_major_unit_name_mu(self):
        for record in self:
            make = record.prod_lot_id.product_id.attribute_value_ids.filtered(
                lambda r: r.attribute_id == r.env.ref('drm_product_attributes.product_attribute_make'))
            year = record.prod_lot_id.product_id.attribute_value_ids.filtered(
                lambda r: r.attribute_id == r.env.ref('drm_product_attributes.product_attribute_year'))
            model = record.prod_lot_id.product_id.attribute_value_ids.filtered(
                lambda r: r.attribute_id == r.env.ref('drm_product_attributes.product_attribute_model'))
            if make:
                str1= ''.join(str(make.name))
            else:
                str1=''
            if year:
                str2=''.join(str(year.name))
            else:
                str2=''
            if model:
                str3=''.join(str(model.name))
            else:
                str3=''
            str4=str1+' '+str2+' '+str3+' '
            record.mu_name = str4
            prod_m=self.env['product.template'].search([('name','=','Freight Charges')]).product_variant_id
            prod_f=self.env['product.template'].search([('name','=','Document Fees')]).product_variant_id
            record.update({'manufacturer_ids': [[0, False, {'manufacturer_price': 0.0, 'product_id': prod_m.id, 'major_unit_id': record.id}]],\
              'finance_ids': [[0, False, {'lst_price': 0.0, 'product_id': prod_f.id, 'major_unit_id': record.id}]]})

    def get_major_unit_location(self):
        location = self.location_id
        if not location:
            location = self.env['stock.location'].create({
                'name': self.prod_lot_id.name})
            location.location_id=self.env.ref('major_unit.stock_location_major_units')
            self.location_id = location.id
        return location

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
    backend_mapping = fields.One2many(comodel_name='wordpress.odoo.majorunit',
                                      string='Majorunit mapping',
                                      inverse_name='majorunit_id',
                                      readonly=False,
                                      required=False,
                                      )

    backend_mapping_mu_pro = fields.One2many(comodel_name='wordpress.odoo.mu.product',
                                      string='Majorunit product mapping',
                                      inverse_name='major_unit_id',
                                      readonly=False,
                                      required=False,
                                      )

    @api.model
    def create_ride(self, vals):
        major_unit = self._create_major_unit(vals['category_id'], vals['make_id'], vals[
                                             'model_id'], vals['year_id'], vals['vin'])
        return major_unit.id

    @api.model
    def create(self, vals):
        """ Override create method """
        majorunit_id = super(MajorUnit, self).create(vals)
        check_prod_lot_id = self.env['major_unit.major_unit'].search([('prod_lot_id.name','=',majorunit_id.prod_lot_id.name)])
        if len(check_prod_lot_id) > 1 :
            raise UserError('this vin number is already exists!')
        if majorunit_id.partner_id:
          prod_prod= self.env['product.product'].search([('id','=',majorunit_id.product_id.id)])
          product=  self.env['product.template'].search([('id','=',prod_prod.product_tmpl_id.id)])
          product.write({'customer_owned':True,'sale_ok':False,'purchase_ok':False})
          if majorunit_id.product_id.customer_owned:
            majorunit_id.form = 'customer_owned'
        return majorunit_id


    @api.multi
    def major_unit_to_quotation(self):
      #inherit this function to add multiple products  of manufacturer and finance tabs
        product_ids_list=[]
        product_ids_list.append((0,0, {
                    'name': self.name,
                    'price_unit': self.sales_price,
                    'product_id': self.product_id.id,
                    'product_uom_qty': 1,
                    'product_uom': self.product_id.product_tmpl_id.uom_id.id,
                    'purchase_price': self.standard_price,
                    'lot_id': self.prod_lot_id.id,
                }))
        for man in self.manufacturer_ids:
          product_ids_list.append((0,0, {
                    'name': man.product_id.name,
                    'price_unit': man.manufacturer_price,
                    'product_id': man.product_id.id,
                    'product_uom_qty': 1,
                    'product_uom': man.product_id.product_tmpl_id.uom_id.id,
                }))
        for fin in self.finance_ids:
          product_ids_list.append((0,0, {
                    'name': fin.product_id.name,
                    'price_unit': fin.lst_price,
                    'product_id': fin.product_id.id,
                    'product_uom_qty': 1,
                    'product_uom': fin.product_id.product_tmpl_id.uom_id.id,
                    
                }))

        for setup in self.product_line_ids:
          product_ids_list.append((0,0, {
                    'name': setup.product_id.name,
                    'price_unit': setup.price_unit,
                    'product_id': setup.product_id.id,
                    'product_uom_qty': setup.product_uom_qty,
                    'product_uom': setup.product_id.product_tmpl_id.uom_id.id,
                    
                }))
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'target': 'current',
            'type': 'ir.actions.act_window',
            'context': {
                'default_order_line': product_ids_list,
                'default_details_model': 'sale.deal',
            }
        }


    @api.multi
    def sync_major_unit(self):
      for backend in self.backend_id:
        if self.partner_id:
          self.with_delay().export_mu_pro(backend)
          self.with_delay().export(backend)
        else:
          self.with_delay().export_mu_pro(backend)
      return

    @api.multi
    @job
    def importer(self, backend):
        """ import and create or update backend mapper """
        if len(self.ids) > 1:
            for obj in self:
                obj.with_delay().single_importer(backend)
            return

        method = 'my_rides'
        arguments = [None, self]
        importer = WpMajorUnitImport(backend)
        res = importer.import_major_unit(method, arguments)
        if (res['status'] == 200 or res['status'] == 201):
            if isinstance(res['data']['my_rides'], list):
                for major_unit_id in res['data']['my_rides']:
                    self.with_delay().single_importer(backend, major_unit_id)
                # for i in range(0,20):
                #   self.with_delay().single_importer(backend,res['data']['my_rides'][i])

    @api.multi
    @job
    def single_importer(self, backend, major_unit_id, woo_id=None):
        method = 'my_rides'
        mapper = self.backend_mapping.search(
            [('backend_id', '=', backend.id), ('woo_id', '=', major_unit_id)], limit=1)
        arguments = [major_unit_id or None, mapper.majorunit_id or self]

        importer = WpMajorUnitImport(backend)
        res = importer.import_major_unit(method, arguments)
        if res['data']['ride_details']:
          partner_id = self.env['wordpress.odoo.res.partner'].search(
              [('backend_id', '=', backend.id), ('woo_id', '=', res['data']['ride_details']['cr_customer_id'])])
          if partner_id:
            pass
          else:
            partner = self.env['res.partner']
            partner.single_importer(backend, res['data']['ride_details']['cr_customer_id'],False)
            partner_id = self.env['wordpress.odoo.res.partner'].search(
              [('backend_id', '=', backend.id), ('woo_id', '=', res['data']['ride_details']['cr_customer_id'])])

        # if res['data']['ride_details']:
          if mapper:
              importer.write_major_unit(backend, mapper, res, partner_id)

          else:
              major_unit = importer.create_major_unit(backend, mapper, res, partner_id)

          if mapper and (res['status'] == 200 or res['status'] == 201):
              vals = {
                  'woo_id': res['data']['ride_details']['cr_rides_id'],
                  'backend_id': backend.id,
                  'majorunit_id': mapper.majorunit_id.id,
              }
              self.backend_mapping.write(vals)
          else:
              vals = {
                  'woo_id': res['data']['ride_details']['cr_rides_id'],
                  'backend_id': backend.id,
                  'majorunit_id': major_unit.id,
              }
              self.backend_mapping.create(vals)

    @api.multi
    @job
    def export(self, backend):
        """ export customer details, save username and create or update backend mapper """
        if len(self.ids) > 1:
            for obj in self:
              if obj.partner_id:
                obj.with_delay().export(backend)
              else:
                obj.with_delay().export_mu_pro(backend)
            return
        mapper = self.backend_mapping.search(
            [('backend_id', '=', backend.id), ('majorunit_id', '=', self.id)])
        method = 'my_rides'
        arguments = [mapper.woo_id or None, self]
        export = WpMajorUnitExport(backend)
        res = export.export_major_unit(method, arguments)
        if mapper and (res['status'] == 200 or res['status'] == 201):
            self.write({'username': res['data'][
                       'ride_details']['cr_customer_id']})
            mapper.write(
                {'majorunit_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['ride_details']['cr_rides_id']})
        elif (res['status'] == 200 or res['status'] == 201):
            self.write({'username': res['data'][
                       'ride_details']['cr_customer_id']})
            self.backend_mapping.create(
                {'majorunit_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['ride_details']['cr_rides_id']})
        elif (res['status'] == 100):
          pass

    @api.multi
    @job
    def export_mu_pro(self, backend):
        """ export customer details, save username and create or update backend mapper """
        if len(self.ids) > 1:
            for obj in self:
              if obj.partner_id:
                obj.with_delay().export_mu_pro(backend)
                obj.with_delay().export(backend)
              else:
                obj.with_delay().export_mu_pro(backend)
            return
        mapper = self.backend_mapping_mu_pro.search(
            [('backend_id', '=', backend.id), ('major_unit_id', '=', self.id)])
        method = 'products'
        arg=self.product_id.product_tmpl_id
        arg.vin=self.vin
        if self.partner_id:
          arg.cust_owned='yes'
        else:
          arg.cust_owned='no'
        arguments = [mapper.woo_id or None, arg]
        export = WpMajorProductExport(backend)
        res = export.export_major_unit(method, arguments)
        if mapper and (res['status'] == 200 or res['status'] == 201):
            mapper.write(
                {'major_unit_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['id']})
        elif (res['status'] == 200 or res['status'] == 201):
            self.backend_mapping_mu_pro.create(
                {'major_unit_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['id']})
        elif (res['status'] == 100):
          pass


    @api.depends('manufacturer_ids','finance_ids','manufacturer_ids.manufacturer_price','finance_ids.lst_price')
    def _compute_extra_charges(self):
      self.manufacturer_charges=sum([item.manufacturer_price for item in self.manufacturer_ids])
      self.financing_charges=sum([product.lst_price for product in self.finance_ids])
      if self.product_line_ids:
        self.setup_charges_total=sum([products.price_unit for products in self.product_line_ids])


class MajorUnitMapping(models.Model):

    """ Model to store woocommerce id for particular product category"""
    _name = 'wordpress.odoo.majorunit'

    majorunit_id = fields.Many2one(comodel_name='major_unit.major_unit',
                                   string='Product Major Unit',
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
    image_id = fields.Char('Image id')
    woo_id = fields.Char(string='woo_id')


class stockproductlot(models.Model):

    """ Models for woocommerce product category """
    _inherit = 'stock.production.lot'

    product_qty = fields.Float(string="Quantity", default=1.00, compute='_product_qty')

    @api.one
    @api.depends('quant_ids.quantity','product_id')
    def _product_qty(self):
        if len(self.quant_ids)>1:
          for quant in self.quant_ids:
            if quant.quantity!=0:
              self.product_qty = sum(self.quant_ids.mapped('quantity'))
              break
            elif quant.quantity==0:
              self.product_qty = 1.00

        elif self.quant_ids.quantity == 0:
            self.product_qty = 1.00
        else:
            self.product_qty = sum(self.quant_ids.mapped('quantity'))

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(stockproductlot, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        from_mu = self._context.get('creation_from_major_unit')
        if from_mu:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='product_id']"):
                node.set('domain', "[('details_model', 'in', ['vehicle','nadanew.vehicle.product'])]")
            res['arch'] = etree.tostring(doc)
        return res


class MUImageMapping(models.Model):

    """ Model to store woocommerce id for particular product"""
    _name = 'wordpress.odoo.mu.image'
    majorunit_id = fields.Many2one(comodel_name='major_unit.major_unit',
                                 string='Major Unit',
                                 ondelete='cascade',
                                 readonly=False,
                                 required=True,)
    mu_image_id = fields.Many2one(comodel_name='major_unit.image',
                                       string='Major Unit image',
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

class MajorUnitImages(models.Model):
    _inherit = 'major_unit.image'
    sequence = fields.Integer(string="Seq")
    default = fields.Boolean(string="Main Product Image")
    woo_id = fields.Char(string="Woo id")
    position = fields.Integer(string="Position")
    src = fields.Char(string="Source")
    backend_mapping = fields.One2many(comodel_name='wordpress.odoo.mu.image',
                                      string='Major unit Image mapping',
                                      inverse_name='mu_image_id',
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
        return super(MajorUnitImages, self).create(vals)

class MajorUnitManufacturer(models.Model):
    _name = 'major_unit.manufacturer'

    major_unit_id = fields.Many2one('major_unit.major_unit', 'Major Unit')
    product_id = fields.Many2one('product.product', 'Product')
    manufacturer_price = fields.Float('Price')
    @api.onchange('product_id')
    def onchange_product_id(self):
      self.manufacturer_price=self.product_id.lst_price



class MajorUnitFinanceInherit(models.Model):
    _name = 'major_unit.finance'

    major_unit_id = fields.Many2one('major_unit.major_unit', 'Major Unit')
    product_id = fields.Many2one('product.product', 'Product')
    lst_price = fields.Float(string='Price')
    @api.onchange('product_id')
    def onchange_product_id(self):
      self.lst_price=self.product_id.lst_price