# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Yannick Gouin <yannick.gouin@elico-corp.com>
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
##############################################################################

#from openerp import netsvc
from unittest import result
# from unittest.mock import result

from odoo import models, fields, api
from odoo.tools.float_utils import float_round
from odoo import fields as fields2
import odoo.addons.decimal_precision as dp
import math

class product_item(models.Model):
    _name = "product.item"
    _description = "Product Item for Bundle products"

    sequence=   fields.Integer('Sequence')
    product_id= fields.Many2one('product.product', 'Bundle Product')
    template_id=fields.Many2one('product.template', 'Bundle Product')
    item_id=    fields.Many2one('product.product', 'Item', required=True)
    uom_id=     fields.Many2one('uom.uom', 'UoM', required=True)
    qty_uom=    fields.Integer('Quantity', required=True)
    #revenue=    fields.Float('Revenue repartition (%)', help="Define when you sell a Bundle product, how many percent of the sale price is applied to this item.")
    #editable=   fields.Boolean('Allow changes in DO ?', help="Allow the user to change this item (quantity or item itself) in the Delivery Orders.")

    _defaults = {
        'editable': lambda *a: True,
    }

    # def onchange_item_id(self, cr, uid, ids, item_id, context=None):
    def onchange_item_id(self):

        cr = self.env.cr
        ids = self.ids
        uid = self._uid
        item_id = self.item_id
        context = self._context
        # context = context or {}
        # domain = {}
        # result = {}
        #
        item=None
        if item_id:
            item = self.env('product.product').browse()

        if item:
            result.update({'uom_id': item.uom_id.id})
            domain = {'uom_id': [('category_id', '=', item.uom_id.category_id.id)]}

        return {'value': result, 'domain': domain}



class product_template(models.Model):
    _inherit = "product.template"
    pitem_ids= fields.One2many('product.item', 'template_id', 'Item sets')
    bundle=fields.Boolean('Bundle')

    @api.model
    def create(self,values):

        res_id=super(product_template,self).create(values)

        for variant in res_id.product_variant_ids:
            items=[]
            for pitem in variant.pitem_ids:
                pitem.unlink()
            for pitem in res_id.pitem_ids:
                res=self.env['product.item'].create({'sequence':pitem.sequence,'product_id':variant.id,'item_id':pitem.item_id.id,'uom_id':pitem.uom_id.id,'qty_uom':pitem.qty_uom})
                items.append(res)
                pass
            variant.write({'pitem_ids':items})

        return res_id

    @api.one
    def write(self, vals):
        res_id=super(product_template,self).write(vals)

        if self.product_variant_count==1:
            for variant in self.product_variant_ids:
                items=[]
                for pitem in variant.pitem_ids:
                    pitem.unlink()

                for pitem in self.pitem_ids:
                    res=self.env['product.item'].create({'sequence':pitem.sequence,'product_id':variant.id,'item_id':pitem.item_id.id,'uom_id':pitem.uom_id.id,'qty_uom':pitem.qty_uom})
                    items.append(res)
                #variant.write({'pitem_ids':[]})

        return res_id


class UserError(object):
    pass


class product_product(models.Model):
    _inherit = "product.product"
    #pitem_ids= fields.One2many('product.item', 'product_id', 'Item sets')
    #bundle=fields.Boolean('Bundle')


    @api.one
    def write(self, vals):
        res_id=super(product_product,self).write(vals)
        if self.product_tmpl_id.product_variant_count==1:
            for pitem in self.product_tmpl_id.pitem_ids:
                pitem.unlink()

            for pitem in self.pitem_ids:
                res=self.env['product.item'].create({'sequence':pitem.sequence,'template_id':self.product_tmpl_id.id,'item_id':pitem.item_id.id,'uom_id':pitem.uom_id.id,'qty_uom':pitem.qty_uom})

            pass

        return res_id


    def _product_quantity_bundle(self, product, context,domain_quant_loc):
    # def _product_quantity_bundle(self, cr, uid, product, context, domain_quant_loc):

        domain_quant=[]

        ids=[]
        pitem_ids=filter(None, map(lambda x:x, product.pitem_ids))
        for pitem_id in pitem_ids:
            ids.append(pitem_id.item_id.id)
        domain_products = [('product_id', 'in', ids)]
        domain_quant += domain_products

        if context.get('lot_id'):
            domain_quant.append(('lot_id', '=', context['lot_id']))
        if context.get('owner_id'):
            domain_quant.append(('owner_id', '=', context['owner_id']))
        if context.get('package_id'):
            domain_quant.append(('package_id', '=', context['package_id']))
        domain_quant += domain_quant_loc

        quants = self.env('stock.quant').read_group(domain_quant, ['product_id', 'qty'], ['product_id'])
        quants = dict(map(lambda x: (x['product_id'][0], x['qty']), quants))
        return quants
#
    def _product_move_in_bundle(self, product,context,domain_move_in_loc):
        domain_move_in=[]

        ids=[]
        pitem_ids=filter(None, map(lambda x:x, product.pitem_ids))
        for pitem_id in pitem_ids:
            ids.append(pitem_id.item_id.id)
        domain_products = [('product_id', 'in', ids)]

        domain_move_in +=  self._compute_quantities_dict() + [('state', 'not in', ('done', 'cancel', 'draft'))] + domain_products


        if context.get('owner_id'):
            owner_domain = ('restrict_partner_id', '=', context['owner_id'])
            domain_move_in.append(owner_domain)

        domain_move_in += domain_move_in_loc
        moves_in = self.env('stock.move').read_group(domain_move_in, ['product_id', 'product_qty'], ['product_id'])
        moves_in = dict(map(lambda x: (x['product_id'][0], x['product_qty']), moves_in))
        return moves_in
#
    def _product_move_out_bundle(self, product,context,domain_move_out_loc):
        domain_move_out=[]

        ids=[]
        pitem_ids=filter(None, map(lambda x:x, product.pitem_ids))
        for pitem_id in pitem_ids:
            ids.append(pitem_id.item_id.id)
        domain_products = [('product_id', 'in', ids)]

        domain_move_out +=  self._compute_quantities_dict() + [('state', 'not in', ('done', 'cancel', 'draft'))] + domain_products

        if context.get('owner_id'):
            owner_domain = ('restrict_partner_id', '=', context['owner_id'])
            domain_move_out.append(owner_domain)

        domain_move_out += domain_move_out_loc
        moves_out = self.env('stock.move').read_group( domain_move_out, ['product_id', 'product_qty'], ['product_id'])
        moves_out = dict(map(lambda x: (x['product_id'][0], x['product_qty']), moves_out))
        return moves_out

#     def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
#             context = context or {}
#             field_names = field_names or []
#             domain_products = [('product_id', 'in', ids)]
#             domain_quant, domain_move_in, domain_move_out = [], [], []
#             domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations(cr, uid, ids,
#                                                                                                    context=context)
#             domain_move_in += self._get_domain_dates(cr, uid, ids, context=context) + [
#                 ('state', 'not in', ('done', 'cancel', 'draft'))] + domain_products
#             domain_move_out += self._get_domain_dates(cr, uid, ids, context=context) + [
#                 ('state', 'not in', ('done', 'cancel', 'draft'))] + domain_products
#             domain_quant += domain_products
#
#             if context.get('lot_id'):
#                 domain_quant.append(('lot_id', '=', context['lot_id']))
#             if context.get('owner_id'):
#                 domain_quant.append(('owner_id', '=', context['owner_id']))
#                 owner_domain = ('restrict_partner_id', '=', context['owner_id'])
#                 domain_move_in.append(owner_domain)
#                 domain_move_out.append(owner_domain)
#             if context.get('package_id'):
#                 domain_quant.append(('package_id', '=', context['package_id']))
#
#             domain_move_in += domain_move_in_loc
#             domain_move_out += domain_move_out_loc
#             moves_in = self.pool.get('stock.move').read_group(cr, uid, domain_move_in, ['product_id', 'product_qty'],
#                                                               ['product_id'], context=context)
#             moves_out = self.pool.get('stock.move').read_group(cr, uid, domain_move_out, ['product_id', 'product_qty'],
#                                                                ['product_id'], context=context)
#
#             domain_quant += domain_quant_loc
#             quants = self.pool.get('stock.quant').read_group(cr, uid, domain_quant, ['product_id', 'qty'],
#                                                              ['product_id'], context=context)
#             quants = dict(map(lambda x: (x['product_id'][0], x['qty']), quants))
#
#             moves_in = dict(map(lambda x: (x['product_id'][0], x['product_qty']), moves_in))
#             moves_out = dict(map(lambda x: (x['product_id'][0], x['product_qty']), moves_out))
#             res = {}
#             for product in self.browse(cr, uid, ids, context=context):
#                 id = product.id
#                 if product.bundle:
#
#                     bundle_quants = self._product_quantity_bundle(cr, uid, product, context, domain_quant_loc)
#                     bundle_moves_in = self._product_move_in_bundle(cr, uid, product, context, domain_move_in_loc)
#                     bundle_moves_out = self._product_move_out_bundle(cr, uid, product, context, domain_move_out_loc)
#
#                     pitem_ids = filter(None, map(lambda x: x, product.pitem_ids))
#
#                     qty_available = 0
#                     incoming_qty = 0
#                     outgoing_qty = 0
#
#                     if len(pitem_ids) > 0:
#                         pitem_id = pitem_ids[0]
#                         if pitem_id.qty_uom > 0:
#                             qty_available = int(float_round(bundle_quants.get(pitem_id.item_id.id, 0.0),
#                                                             precision_rounding=product.uom_id.rounding) / pitem_id.qty_uom)
#                             incoming_qty = int(float_round(bundle_moves_in.get(pitem_id.item_id.id, 0.0),
#                                                            precision_rounding=product.uom_id.rounding) / pitem_id.qty_uom)
#                             outgoing_qty = int(math.ceil(float_round(bundle_moves_out.get(pitem_id.item_id.id, 0.0),
#                                                                      precision_rounding=product.uom_id.rounding) / pitem_id.qty_uom))
#                             # erg= int(float_round(pitem_id.item_id.qty_available, precision_rounding=product.uom_id.rounding)/pitem_id.qty_uom)
#                         for pitem_id in pitem_ids[1:]:
#                             if pitem_id.qty_uom <= 0:
#                                 continue
#                             erg = int(float_round(bundle_quants.get(pitem_id.item_id.id, 0.0),
#                                                   precision_rounding=product.uom_id.rounding) / pitem_id.qty_uom)
#                             # erg= int(float_round(pitem_id.item_id.qty_available, precision_rounding=product.uom_id.rounding)/pitem_id.qty_uom)
#                             if erg < qty_available:
#                                 qty_available = erg
#                             erg = int(float_round(bundle_moves_in.get(pitem_id.item_id.id, 0.0),
#                                                   precision_rounding=product.uom_id.rounding) / pitem_id.qty_uom)
#                             # erg= int(float_round(pitem_id.item_id.incoming_qty, precision_rounding=product.uom_id.rounding)/pitem_id.qty_uom)
#                             if erg < incoming_qty:
#                                 incoming_qty = erg
#                             erg = int(math.ceil(float_round(bundle_moves_out.get(pitem_id.item_id.id, 0.0),
#                                                             precision_rounding=product.uom_id.rounding) / pitem_id.qty_uom))
#                             # erg= int(math.ceil(float_round(pitem_id.item_id.outgoing_qty, precision_rounding=product.uom_id.rounding)/pitem_id.qty_uom))
#                             if erg < outgoing_qty:
#                                 outgoing_qty = erg
#
#                     virtual_available = qty_available + incoming_qty - outgoing_qty
#
#                 #                 virtual_available = 99999991
#                 #                 for pitem_id in pitem_ids:
#                 #                     if pitem_id.qty_uom<=0:
#                 #                         continue
#                 #                     #erg= int(math.ceil(float_round(bundle_moves_out.get(pitem_id.item_id.id, 0.0), precision_rounding=product.uom_id.rounding)/pitem_id.qty_uom))
#                 #                     erg= int(float_round(pitem_id.item_id.virtual_available, precision_rounding=product.uom_id.rounding)/pitem_id.qty_uom)
#                 #                     if erg<virtual_available:
#                 #                         virtual_available=erg
#                 #                 if virtual_available == 99999991:
#                 #                     virtual_available=0
#
#                 else:
#                     qty_available = float_round(quants.get(id, 0.0), precision_rounding=product.uom_id.rounding)
#                     incoming_qty = float_round(moves_in.get(id, 0.0), precision_rounding=product.uom_id.rounding)
#                     outgoing_qty = float_round(moves_out.get(id, 0.0), precision_rounding=product.uom_id.rounding)
#                     virtual_available = float_round(
#                         quants.get(id, 0.0) + moves_in.get(id, 0.0) - moves_out.get(id, 0.0),
#                         precision_rounding=product.uom_id.rounding)
#                 res[id] = {
#                     'qty_available': qty_available,
#                     'incoming_qty': incoming_qty,
#                     'outgoing_qty': outgoing_qty,
#                     'virtual_available': virtual_available,
#                 }
#             return res
# # #
    def _search_product_quantity(self, operator, value, field, OPERATORS=None):
        # TDE FIXME: should probably clean the search methods
        # to prevent sql injections
        if field not in ('qty_available', 'virtual_available', 'incoming_qty', 'outgoing_qty'):
            raise UserError(_('Invalid domain left operand %s') % field)
        if operator not in ('<', '>', '=', '!=', '<=', '>='):
            raise UserError(_('Invalid domain operator %s') % operator)
        if not isinstance(value, (float, int)):
            raise UserError(_('Invalid domain right operand %s') % value)

        # TODO: Still optimization possible when searching virtual quantities
        ids = []
        for product in self.with_context(prefetch_fields=False).search([]):
            if OPERATORS[operator](product[field], value):
                ids.append(product.id)
        return [('id', 'in', ids)]

    _columns = {
        'qty_available': fields2.Integer(compute='_product_available', multi='qty_available',
            type='float', digits=dp.get_precision('Product Unit of Measure'),
            string='Quantity On Hand',
            fnct_search=_search_product_quantity,
            help="Current quantity of products.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods stored at this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods stored in the Stock Location of this Warehouse, or any "
                 "of its children.\n"
                 "stored in the Stock Location of the Warehouse of this Shop, "
                 "or any of its children.\n"
                 "Otherwise, this includes goods stored in any Stock Location "
                 "with 'internal' type."),
        'virtual_available': fields2.Integer(compute='_product_available', multi='qty_available',
            type='float', digitse=dp.get_precision('Product Unit of Measure'),
            string='Forecast Quantity',
            fnct_search=_search_product_quantity,
            help="Forecast quantity (computed as Quantity On Hand "
                 "- Outgoing + Incoming)\n"
                 "In a context with a single Stock Location, this includes "
                 "goods stored in this location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods stored in the Stock Location of this Warehouse, or any "
                 "of its children.\n"
                 "Otherwise, this includes goods stored in any Stock Location "
                 "with 'internal' type."),
        'incoming_qty': fields2.Integer(compute='_product_available', multi='qty_available',
            type='float', digitse=dp.get_precision('Product Unit of Measure'),
            string='Incoming',
            fnct_search=_search_product_quantity,
            help="Quantity of products that are planned to arrive.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods arriving to this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods arriving to the Stock Location of this Warehouse, or "
                 "any of its children.\n"
                 "Otherwise, this includes goods arriving to any Stock "
                 "Location with 'internal' type."),
        'outgoing_qty': fields2.Integer(compute='_product_available', multi='qty_available',
            type='float', digitse=dp.get_precision('Product Unit of Measure'),
            string='Outgoing',
            fnct_search=_search_product_quantity,
            help="Quantity of products that are planned to leave.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods leaving this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods leaving the Stock Location of this Warehouse, or "
                 "any of its children.\n"
                 "Otherwise, this includes goods leaving any Stock "
                 "Location with 'internal' type."),
    }

    pitem_ids= fields.One2many('product.item', 'product_id', 'Item sets')
    #pitem_ids= fields.One2many(related='product_tmpl_id.pitem_ids',store=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
