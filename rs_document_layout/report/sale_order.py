from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from dateutil.relativedelta import relativedelta
from datetime import datetime , timedelta


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    price_tax = fields.Float(compute='_compute_amount',digits=dp.get_precision('Product Price'), string='Total Tax', readonly=True, store=True)
    single_unit=fields.Integer(string="Single Unit")
    name = fields.Char(string="Description")

    # bundle product single unit
    @api.onchange('product_id','product_uom_qty')
    def custom_quantity(self):
        if self.product_id.type == 'service':
            self.update({'single_unit':0})

        elif self.product_id.name and self.product_id.default_code:
            if ('20x' in self.product_id.name or '20X' in self.product_id.name) or ('20x' in self.product_id.default_code or '20X' in self.product_id.default_code) :
                self.product_id.default_code = self.product_id.default_code.replace('-20x', '')
                product = self.env['product.product'].search(['&',('default_code', '=', self.product_id.default_code),('sale_ok', '=', 'True')] )
                self.product_id.name = product.name
                self.update({'single_unit':self.product_uom_qty*20})

            elif ('80x' in self.product_id.name or '80X' in self.product_id.name) or ('80x' in self.product_id.default_code or '80X' in self.product_id.default_code):
                self.product_id.default_code = self.product_id.default_code.replace('-80x', '')
                product = self.env['product.product'].search(['&',('default_code', '=', self.product_id.default_code),('sale_ok', '=', 'True')] )
                self.product_id.name = product.name
                self.update({'single_unit':self.product_uom_qty*80})

            else:
                self.update({'single_unit':self.product_uom_qty})

    @api.model
    def _prepare_add_missing_fields(self, values):
        """ Deduce missing required fields from the onchange """
        res = {}
        onchange_fields = ['name', 'price_unit', 'product_uom', 'tax_id']
        if values.get('order_id') and values.get('product_id') and any(f not in values for f in onchange_fields):
            with self.env.do_in_onchange():
                line = self.new(values)
                line.product_id_change()
                for field in onchange_fields:
                    if field not in values:
                        res[field] = line._fields[field].convert_to_write(line[field], line)
        return res

    @api.multi
    def _prepare_invoice_line(self, qty):
        res=super(SaleOrderLine,self)._prepare_invoice_line(qty)
        res.update({'single_unit':self.single_unit})
        return res


    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product = self.product_id.with_context(
                warehouse=self.order_id.warehouse_id.id,
                lang=self.order_id.partner_id.lang or self.env.user.lang or 'en_US'
            )
            product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
            # if float_compare(product.virtual_available, product_qty, precision_digits=precision) == -1:
            #     is_available = self._check_routing()
            #     if not is_available:                   
            #         message =  _('You plan to sell %s %s of %s but you only have %s %s available in %s warehouse.') % \
            #                 (self.product_uom_qty, self.product_uom.name, self.product_id.name, product.virtual_available, product.uom_id.name, self.order_id.warehouse_id.name)
            #         # We check if some products are available in other warehouses.
            #         if float_compare(product.virtual_available, self.product_id.virtual_available, precision_digits=precision) == -1:
            #             message += _('\nThere are %s %s available across all warehouses.\n\n') % \
            #                     (self.product_id.virtual_available, product.uom_id.name)
            #             for warehouse in self.env['stock.warehouse'].search([]):
            #                 quantity = self.product_id.with_context(warehouse=warehouse.id).virtual_available
            #                 if quantity > 0:
            #                     message += "%s: %s %s\n" % (warehouse.name, quantity, self.product_id.uom_id.name)
            #         warning_mess = {
            #             'title': _('Not enough inventory!'),
            #             'message' : message
            #         }
            #         return {'warning': warning_mess}
        return {}
        


class CustomSaleOrderfilter(models.Model):
    _inherit = "sale.order"


    category_id_new = fields.Char(string='Customer Tag', related='partner_id.category_id.name')
    country_id_new = fields.Char(string='Customer Country', related='partner_id.country_id.name')
    lang_new = fields.Selection('res.partner', string='Customer Lang', related='partner_id.lang')
    zip_new = fields.Char(string='Customer Zip', related='partner_id.zip')
    city_new = fields.Char(string='Customer City', related='partner_id.city')
    state_new = fields.Char(string='Customer Federal State', related='partner_id.state_id.name')
    # is_retailer_new = fields.Boolean('Retailer', related='partner_id.is_retailer')
    client_order_ref = fields.Char(string='Customer Reference', copy=True)
    partner_invoice_id = fields.Many2one('res.partner',compute='_partner_invoice_address_change')
    partner_shipping_id = fields.Many2one('res.partner',compute='_partner_shipping_address_change')

    @api.model
    def fields_get(self, fields=None):
        fields_to_hide = ['order_date']
        res = super(CustomSaleOrderfilter, self).fields_get()
        for field in fields_to_hide:
            res[field]['selectable'] = False
        return res


    @api.depends('order_date')
    def _get_date_order(self):
        order_date = (self.order_date + timedelta(days=14)).strftime('%d-%m-%Y')
        return order_date

    @api.onchange('partner_invoice_id')
    def _partner_invoice_address_change(self):
        for child in self.partner_id.child_ids:
            if child.type == 'contact':
                self.partner_invoice_id = self.partner_id
            elif child.type == 'invoice' or child.type == 'delivery':
                addr = self.partner_id.address_get(['invoice','delivery'])
                self.partner_invoice_id = addr and addr.get('invoice')
            else:
                pass


    @api.onchange('partner_shipping_id')
    def _partner_shipping_address_change(self):
        for child in self.partner_id.child_ids:
            if child.type == 'contact':
                self.partner_shipping_id = self.partner_id
            elif child.type == 'invoice' or child.type == 'delivery':
                addr = self.partner_id.address_get(['invoice','delivery'])
                self.partner_shipping_id = addr and addr.get('delivery')
            else:
                pass

class Custominvoicefilter(models.Model):
    _inherit = "account.invoice"


    category_id_new = fields.Char(string='Customer Tag', related='partner_id.category_id.name')
    country_id_new = fields.Char(string='Customer Country', related='partner_id.country_id.name')
    lang_new = fields.Selection('res.partner', string='Customer Lang', related='partner_id.lang')
    zip_new = fields.Char(string='Customer Zip', related='partner_id.zip')
    is_retailer_new = fields.Boolean('Retailer', related='partner_id.is_retailer')
    city_new = fields.Char(string='Customer City', related='partner_id.city')
    state_new = fields.Char(string='Customer Federal State', related='partner_id.state_id.name')
    origin1 = fields.Many2one('sale.order',compute="_get_source_document_value",string='Source Document')

    @api.model
    def _get_source_document_value(self):

        for line in self:
            sol = self.env['sale.order'].search([('name', '=', line.origin)])
            if sol:
                for i in sol:
                    line.update({'origin1': i.id})


class SaleReport(models.Model):
    _inherit = "sale.report"

    single_unit = fields.Integer(string="Single Unit",store=True)
    category_id_new = fields.Char(string='Customer Tag', related='partner_id.category_id.name')
    zip_new = fields.Char(string='Customer Zip', related='partner_id.zip')
    city_new = fields.Char(string='Customer City', related='partner_id.city')
    state_new = fields.Char(string='Customer Federal State', related='partner_id.state_id.name')
    product_type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Storable Product'),
        ], string='Product Type',readonly=True,default='consu',related='product_id.type')


    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['single_unit'] = ', l.single_unit as single_unit'

        groupby += ', l.single_unit'

        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)


class Custominvoicereportfilter(models.Model):
    _inherit = "account.invoice.report"

    category_id_new = fields.Char(string='Customer Tag', related='partner_id.category_id.name')
    zip_new = fields.Char(string='Customer Zip', related='partner_id.zip')
    city_new = fields.Char(string='Customer City', related='partner_id.city')
    state_new = fields.Char(string='Customer Federal State', related='partner_id.state_id.name')

class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    min_quantity = fields.Integer(
        'Min. total net (EUR)', default=0,
        help="For the rule to apply, bought/sold quantity must be greater "
             "than or equal to the minimum quantity specified in this field.\n"
             "Expressed in the default unit of measure of the product.")

