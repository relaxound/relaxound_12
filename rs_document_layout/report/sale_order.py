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
    # partner_invoice_id = fields.Many2one('res.partner',compute='_partner_invoice_address_change')
    # partner_shipping_id_new = fields.Many2one('res.partner',compute='_partner_shipping_address_change')

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

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment terms
        - Invoice address
        - Delivery address
        """
        for rec in self:
            addr = rec.partner_id.address_get(['invoice', 'delivery'])
            if not rec.partner_id:
                rec.update({
                    'partner_invoice_id': False,
                    'partner_shipping_id': False,
                    'payment_term_id': False,
                    'fiscal_position_id': False,
                })
                return

            if rec.partner_id.child_ids:
                for child in rec.partner_id.child_ids[0]:
                    if child.type == 'contact':
                        values = {
                            'pricelist_id': rec.partner_id.property_product_pricelist and rec.partner_id.property_product_pricelist.id or False,
                            'payment_term_id': rec.partner_id.property_payment_term_id and rec.partner_id.property_payment_term_id.id or False,
                            'partner_invoice_id': rec.partner_id.id,
                            'partner_shipping_id': rec.partner_id.id,
                            'user_id': rec.partner_id.user_id.id or rec.partner_id.commercial_partner_id.user_id.id or rec.env.uid
                        }
                    elif child.type == 'invoice' or child.type == 'delivery':
                        values = {
                            'pricelist_id': rec.partner_id.property_product_pricelist and rec.partner_id.property_product_pricelist.id or False,
                            'payment_term_id': rec.partner_id.property_payment_term_id and rec.partner_id.property_payment_term_id.id or False,
                            'partner_invoice_id': addr['contact'] and addr.get('invoice'),
                            'partner_shipping_id': addr['contact'] and addr.get('delivery'),
                            'user_id': rec.partner_id.user_id.id or rec.partner_id.commercial_partner_id.user_id.id or rec.env.uid
                        }
                    elif child.type == 'other' or child.type == 'private':
                        values = {
                            'pricelist_id': rec.partner_id.property_product_pricelist and rec.partner_id.property_product_pricelist.id or False,
                            'payment_term_id': rec.partner_id.property_payment_term_id and rec.partner_id.property_payment_term_id.id or False,
                            'partner_invoice_id': rec.partner_id.id,
                            'partner_shipping_id': rec.partner_id.id,
                            'user_id': rec.partner_id.user_id.id or rec.partner_id.commercial_partner_id.user_id.id or rec.env.uid
                        }
                    else:
                        values = {
                                'pricelist_id': rec.partner_id.property_product_pricelist and rec.partner_id.property_product_pricelist.id or False,
                                'payment_term_id': rec.partner_id.property_payment_term_id and rec.partner_id.property_payment_term_id.id or False,
                                'partner_invoice_id': rec.partner_id.id,
                                'partner_shipping_id': rec.partner_id.id,
                                'user_id': rec.partner_id.user_id.id or rec.partner_id.commercial_partner_id.user_id.id or rec.env.uid
                            }

            else:
                values = {
                    'pricelist_id': rec.partner_id.property_product_pricelist and rec.partner_id.property_product_pricelist.id or False,
                    'payment_term_id': rec.partner_id.property_payment_term_id and rec.partner_id.property_payment_term_id.id or False,
                    'partner_invoice_id': addr['invoice'],
                    'partner_shipping_id': addr['delivery'],
                    'user_id': rec.partner_id.user_id.id or rec.partner_id.commercial_partner_id.user_id.id or rec.env.uid
                }

            # Change code logic
            # addr = rec.partner_id.address_get(['delivery', 'invoice'])
            # values = {
            #     'pricelist_id': rec.partner_id.property_product_pricelist and rec.partner_id.property_product_pricelist.id or False,
            #     'payment_term_id': rec.partner_id.property_payment_term_id and rec.partner_id.property_payment_term_id.id or False,
            #     'partner_invoice_id': addr['invoice'],
            #     'partner_shipping_id': addr['delivery'],
            #     'user_id': rec.partner_id.user_id.id or rec.partner_id.commercial_partner_id.user_id.id or rec.env.uid
            # }

            if rec.env['ir.config_parameter'].sudo().get_param(
                    'sale.use_sale_note') and rec.env.user.company_id.sale_note:
                values['note'] = rec.with_context(lang=rec.partner_id.lang).env.user.company_id.sale_note

            if rec.partner_id.team_id:
                values['team_id'] = rec.partner_id.team_id.id
            rec.update(values)


    @api.onchange('partner_shipping_id')
    def _onchange_partner_shipping_id(self):
        pass
        # res = {}
        # pickings = self.picking_ids.filtered(
        #     lambda p: p.state not in ['done', 'cancel'] and p.partner_id != self.partner_shipping_id
        # )
        # if pickings:
        #     res['warning'] = {
        #         'title': _('Warning!'),
        #         'message': _(
        #             'Do not forget to change the partner on the following delivery orders: %s'
        #         ) % (','.join(pickings.mapped('name')))
        #     }
        # return res






    # @api.multi
    # @api.onchange('partner_id')
    # def _partner_invoice_address_change(self):
    #     for rec in self:
    #         if rec.partner_id.child_ids:
    #             for child in rec.partner_id.child_ids:
    #                 if child.type == 'contact':
    #                     rec.update({'partner_invoice_id':rec.partner_id})
    #                 elif child.type == 'invoice' or child.type == 'delivery':
    #                     addr = rec.partner_id.address_get(['invoice','delivery'])
    #                     rec.update({'partner_invoice_id':addr and addr.get('invoice')})
    #                 else:
    #                     rec.update({'partner_invoice_id':rec.partner_id})
    #         else:
    #             rec.update({'partner_invoice_id': rec.partner_id})

    # @api.onchange('partner_shipping_id')
    # def _partner_shipping_address_change(self):
    #     for rec in self:
    #         if rec.partner_id.child_ids:
    #             for child in rec.partner_id.child_ids:
    #                 if child.type == 'contact':
    #                     rec.partner_shipping_id_new= rec.partner_id
    #                 elif child.type == 'invoice' or child.type == 'delivery':
    #                     addr = rec.partner_id.address_get(['invoice','delivery'])
    #                     rec.partner_shipping_id_new = addr and addr.get('delivery')
    #                 else:
    #                     rec.partner_shipping_id_new = rec.partner_id
    #         else:
    #             rec.partner_shipping_id_new = rec.partner_id


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

    tag_ids = fields.Char(string='Tags',readonly=True,related='order_id.tag_ids.name')
    carrier_id = fields.Char(string='Delivery Method',readonly=True,related='order_id.carrier_id.name')

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

