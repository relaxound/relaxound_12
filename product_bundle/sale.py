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

from datetime import datetime, timedelta
#from openerp.osv import osv
#from openerp import netsvc
# from custom.addons.relaxound_12.product_bundle.product import UserError changes
from odoo import api,models
from odoo.tools.translate import _
from odoo.tools import float_compare, DEFAULT_SERVER_DATETIME_FORMAT


class sale_order_line(models.Model):
    _inherit="sale.order.line"

    @api.multi
    def _compute_qty_delivered(self):
        """Computes the delivered quantity on sale order lines, based on done stock moves related to its procurements
        """
        for rec in self:
            super(sale_order_line, self)._compute_qty_delivered()
            if rec.product_id.bundle:
                qty = 0
                if len(rec.product_id.pitem_ids)>0:
                    pitem_id=rec.product_id.pitem_ids[0]
                    qtyItem=0.0

                    for move in rec.move_ids.filtered(lambda r: r.state == 'done' and not r.scrapped):
                        if move.location_dest_id.usage == "customer" and pitem_id.item_id.id==move.product_id.id:
                            qtyItem += rec.env['product.uom']._compute_qty_obj(move.product_uom, move.product_uom_qty, pitem_id.uom_id)/pitem_id.qty_uom
                    qty=qtyItem
                    for pitem_id in rec.product_id.pitem_ids:
                        qtyItem=0.0
                        for move in rec.move_ids.filtered(lambda r: r.state == 'done' and not r.scrapped):
                            if move.location_dest_id.usage == "customer" and pitem_id.item_id.id==move.product_id.id:
                                qtyItem += rec.env['product.uom']._compute_qty_obj(move.product_uom, move.product_uom_qty, pitem_id.uom_id)/pitem_id.qty_uom
                        if qtyItem<qty:
                            qty=qtyItem

                return qty

            qty=0.0

            # for move in self.procurement_ids.move_ids.filtered(lambda r: r.state == 'done' and not r.scrapped):
            for move in rec.move_ids.filtered(lambda r:r.state == 'done' and not r.scrapped):
                #Note that we don't decrease quantity for customer returns on purpose: these are exeptions that must be treated manually. Indeed,
                #modifying automatically the delivered quantity may trigger an automatic reinvoicing (refund) of the SO, which is definitively not wanted
                if move.location_dest_id.usage == "customer":
                    qty += rec.env['product.uom']._compute_qty_obj(move.product_uom, move.product_uom_qty, self.product_uom)

        return qty
    
    @api.multi
    def _prepare_bundle_order_line_procurement(self, bundle_item,line, group_id=False):
        # self.ensure_one()

        for rec in self:
            return {
                'name': bundle_item.item_id.name,
                'origin': rec.order_id.name,
                'date_planned': datetime.strptime(str(rec.order_id.date_order), DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(days=rec.customer_lead),
                'product_id': bundle_item.item_id.id,
                'product_qty': bundle_item.qty_uom * line.product_uom_qty,
                #'product_uom_qty': bundle_item.qty_uom * line.product_uom_qty,
                'product_uom': bundle_item.uom_id.id,
                'company_id': rec.order_id.company_id.id,
                'group_id': group_id,
                'sale_line_id': rec.id,
                'location_id': rec.order_id.partner_shipping_id.property_stock_customer.id,
                'route_ids': rec.route_id and [(4, rec.route_id.id)] or [],
                'warehouse_id': rec.order_id.warehouse_id and rec.order_id.warehouse_id.id or False,
                'partner_dest_id': rec.order_id.partner_shipping_id.id
            }
#     
#     @api.onchange('product_id', 'product_uom_qty', 'product_uom', 'route_id')
#     def _onchange_product_id_check_availability(self):
#         if not self.product_id or not self.product_uom_qty or not self.product_uom:
#             self.product_packaging = False
#             return {}
#         if self.product_id.type == 'product':
#             precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
#             product_qty = self.env['product.uom']._compute_qty_obj(self.product_uom, self.product_uom_qty, self.product_id.uom_id)
#             
#             virtual_available=self.product_id.virtual_available
#             
#             if self.product_id.bundle:
#                 min_stock=99999991
#                 for pitem_id in self.product_id.pitem_ids:
#                     erg= int(pitem_id.item_id.virtual_available/pitem_id.qty_uom)
#                     if erg<min_stock:
#                         min_stock=erg
#                 if min_stock==99999991:
#                     min_stock=0
#                 virtual_available=min_stock
#             
#             if float_compare(virtual_available, product_qty, precision_digits=precision) == -1:
#                 is_available = self._check_routing()
#                 if not is_available:
#                     warning_mess = {
#                         'title': _('Not enough inventory!'),
#                         'message' : _('You plan to sell %.2f %s but you only have %.2f %s available!\nThe stock on hand is %.2f %s.') % \
#                             (self.product_uom_qty, self.product_uom.name, virtual_available, self.product_id.uom_id.name, self.product_id.qty_available, self.product_id.uom_id.name)
#                     }
#                     return {'warning': warning_mess}
#         return {}

    @api.multi
    def _action_launch_stock_rule(self):
        """
        Launch procurement group run method with required/custom fields genrated by a
        sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
        depending on the sale order line product rule.
        """

        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        errors = []
        for line in self:
            if line.state != 'sale' or not line.product_id.type in ('consu','product'):
                continue
            qty = line._get_qty_procurement()
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            group_id = line.order_id.procurement_group_id
            if not group_id:
                group_id = self.env['procurement.group'].create({
                    'name': line.order_id.name,
                    'move_type': line.order_id.picking_policy,
                    'sale_id': line.order_id.id,
                    'partner_id': line.order_id.partner_shipping_id.id,
                })
                line.order_id.procurement_group_id = group_id
            else:
                # In case the procurement group is already created and the order was
                # cancelled, we need to update certain values of the group.
                updated_vals = {}
                if group_id.partner_id != line.order_id.partner_shipping_id:
                    updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
                if group_id.move_type != line.order_id.picking_policy:
                    updated_vals.update({'move_type': line.order_id.picking_policy})
                if updated_vals:
                    group_id.write(updated_vals)

            values = line._prepare_procurement_values(group_id=group_id)
            product_qty = line.product_uom_qty - qty

            procurement_uom = line.product_uom
            quant_uom = line.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().get_param
            if procurement_uom.id != quant_uom.id and get_param('stock.propagate_uom') != '1':
                product_qty = line.product_uom._compute_quantity(product_qty, quant_uom, rounding_method='HALF-UP')
                procurement_uom = quant_uom
            # try:
            #     self.env['procurement.group'].run(line.product_id, product_qty, procurement_uom, line.order_id.partner_shipping_id.property_stock_customer, line.name, line.order_id.name, values)
            # except UserError as error:
            #     errors.append(error.name)

        # if errors:changes
        #     raise UserError('\n'.join(errors))
        return True

    @api.model
    def run(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        """ Method used in a procurement case. The purpose is to supply the
        product passed as argument in the location also given as an argument.
        In order to be able to find a suitable location that provide the product
        it will search among stock.rule.
        """

        values.setdefault('company_id', self.env['res.company']._company_default_get('procurement.group'))
        values.setdefault('priority', '1')
        values.setdefault('date_planned', values['date_planned'])

        rule = self._get_rule(product_id, location_id, values)
        # if not rule:changes
        #     raise UserError(_('No procurement rule found in location "%s" for product "%s".\n Check routes configuration.') % (location_id.display_name, product_id.display_name))
        action = 'pull' if rule.action == 'pull_push' else rule.action
        if hasattr(rule, '_run_%s' % action):
            getattr(rule, '_run_%s' % action)(product_id, product_qty, product_uom, location_id, name, origin, values)
        return True

    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        # self.ensure_one()
        for rec in self:
            return {
                'name': rec.name,
                'origin': rec.order_id.name,
                'product_id': rec.product_id,
                'product_qty': rec.product_uom_qty,
                'product_uom': rec.product_uom,
                'company_id': rec.order_id.company_id,
                'group_id': group_id,
                'sale_line_id': rec.id,
                'date_planned': datetime.strptime(str(rec.order_id.date_order), DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(days=rec.customer_lead),
                'location_id': rec.order_id.partner_shipping_id.property_stock_customer,
                'route_ids': rec.route_id,
                'warehouse_id': rec.order_id.warehouse_id or False,
                'partner_dest_id': rec.order_id.partner_shipping_id
            }


    @api.multi
    def _prepare_procurement_values(self,group_id=False):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        new_procs = self.env['procurement.group'] #Empty recordset

        for line in self:
            # if line.state != 'sale' or not line.product_id._need_procurement():
            #above is  original statement
            if line.state != 'sale' :
                continue
            is_bundle=line.product_id.bundle
            if is_bundle:
                pitem_ids=filter(None, map(lambda x:x, line.product_id.pitem_ids))
                pitem_counts = 0
                for pitem_id in pitem_ids:
                    qty = 0.0
#                     for proc in line.procurement_ids:
#                         qty += proc.product_qty
#                     if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
#                         return False

                    if not line.order_id.procurement_group_id:
                        vals = line.order_id._prepare_procurement_group()
                        line.order_id.procurement_group_id = self.env["procurement.group"].create(vals)

                    if pitem_counts == len(line.product_id.pitem_ids):
                        return values
                    else:
                        vals = line._prepare_bundle_order_line_procurement(bundle_item=pitem_id, line=line, group_id=line.order_id.procurement_group_id.id)
                        vals['product_id'] = pitem_id.item_id
                        vals['product_uom'] = pitem_id.uom_id
                        location_id = self.order_id.partner_shipping_id.property_stock_customer
                        vals['name'] = pitem_id.item_id.name
                        vals['origin'] = self.order_id.name
                        vals['product_qty'] = pitem_id.qty_uom * line.product_uom_qty

                        values = {
                           'warehouse_id' : self.order_id.warehouse_id or False,
                           'action': 'pull_push',
                           'date_planned': vals['date_planned'],
                           'group_id':group_id,
                        }

                        new_proc = self.env["procurement.group"].create(vals)
                        new_procs += new_proc
                        new_procs.run(vals['product_id'], vals['product_qty'], vals['product_uom'], location_id, vals['name'], vals['origin'], values)
                        pitem_counts += 1
            else:
                qty = 0.0
                for proc in line.move_ids:
                    qty += proc.product_qty

                if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                    return False

                if not line.order_id.procurement_group_id:
                    vals = line.order_id._prepare_procurement_group()
                    line.order_id.procurement_group_id = self.env["procurement.group"].create(vals)

                vals = line._prepare_order_line_procurement(group_id=line.order_id.procurement_group_id.id)
                location_id = self.order_id.partner_shipping_id.property_stock_customer

                if ('20x' in vals['product_id'].name or '20X' in vals['product_id'].name) or ('20x' in vals['product_id'].default_code or '20X' in vals['product_id'].default_code):
                    default_code = self.product_id.default_code.replace('-20x', '')
                    product = self.env['product.product'].search([('default_code', '=', default_code)])
                    vals['product_id'] = product
                    vals['name'] = vals['product_id'].name
                    vals['product_qty'] = line.product_uom_qty * 20

                elif ('80x' in vals['product_id'].name or '80X' in vals['product_id']) or ('80x' in vals['product_id'].default_code or '80X' in vals['product_id'].default_code):
                    default_code = vals['product_id'].default_code.replace('-80x', '')
                    product = self.env['product.product'].search([('default_code', '=', default_code)])
                    vals['product_id'] = product
                    vals['name'] = vals['product_id'].name
                    vals['product_qty'] = line.product_uom_qty * 80

                else:
                    vals['product_qty'] = line.product_uom_qty

                values = {
                    'warehouse_id': self.order_id.warehouse_id or False,
                    'action': 'pull_push',
                    'date_planned': vals['date_planned'],
                    'group_id': group_id,
                    'name' : vals['name'],
                }

                new_proc = self.env["procurement.group"].create(vals)
                new_procs += new_proc
                new_procs.run(vals['product_id'], vals['product_qty'], vals['product_uom'], location_id, vals['name'], vals['origin'], values)

        return values


class sale_order(models.Model):
    _inherit = "sale.order"
    #_name    = "sale.order"

    def _prepare_order_picking(self, cr, uid, order, context=None):
        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
        return {
            'name': pick_name,
            'origin': order.name,
            'date': order.date_order,
            'type': 'out',
            'state': 'auto',
            'move_type': order.picking_policy,
            'sale_id': order.id,
            'partner_id': order.partner_shipping_id.id,
            'note': order.note,
            'invoice_state': (order.order_policy=='picking' and '2binvoiced') or 'none',
            'company_id': order.company_id.id,
        }
     
     
    def _create_pickings_and_procurements(self, cr, uid, order, order_lines, picking_id=False, context=None):
        """Create the required procurements to supply sales order lines, also connecting
        the procurements to appropriate stock moves in order to bring the goods to the
        sales order's requested location.
 
        If ``picking_id`` is provided, the stock moves will be added to it, otherwise
        a standard outgoing picking will be created to wrap the stock moves, as returned
        by :meth:`~._prepare_order_picking`.
 
        Modules that wish to customize the procurements or partition the stock moves over
        multiple stock pickings may override this method and call ``super()`` with
        different subsets of ``order_lines`` and/or preset ``picking_id`` values.
 
        :param browse_record order: sales order to which the order lines belong
        :param list(browse_record) order_lines: sales order line records to procure
        :param int picking_id: optional ID of a stock picking to which the created stock moves
                               will be added. A new picking will be created if ommitted.
        :return: True
        """
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        procurement_obj = self.pool.get('procurement.group')
        proc_ids = []
         
        location_id = order.shop_id.warehouse_id.lot_stock_id.id
        output_id = order.shop_id.warehouse_id.lot_output_id.id
 
        for line in order_lines:
            if line.state == 'done':
                continue
 
            date_planned = self._get_date_planned(cr, uid, order, line, order.date_order, context=context)
             
            fake_line_ids = []
            is_bundle = False
             
            if line.product_id:
                if line.product_id.bundle:
                #if line.product_id.supply_method == 'bundle':
                    fake_line_ids = filter(None, map(lambda x:x, line.product_id.pitem_ids))
                    is_bundle = True
                else:
                    fake_line_ids.append(line)
                 
                for fake_line in fake_line_ids:
                    line_vals = {}
                     
                    line_vals.update({
                        'location_id': location_id,
                        'company_id': order.company_id.id,                        
                        #move
                        'location_dest_id': output_id,
                        'date': date_planned,
                        'date_expected': date_planned,
                        'partner_id': line.address_allotment_id.id or order.partner_shipping_id.id,
                        'sale_line_id': line.id,
                        'origin': order.name,
                        'tracking_id': False,
                        'state': 'draft',
                    })
                     
                    if is_bundle:
                        line_vals.update({
                            'product_id': fake_line.item_id.id,
                            'product_qty': fake_line.qty_uom * line.product_uom_qty,
                            'product_uom': fake_line.uom_id.id,
                            'product_uos_qty': fake_line.qty_uom * ((line.product_uos and line.product_uos_qty) or line.product_uom_qty),
                            'product_uos': fake_line.uom_id.id,
                            'procure_method': fake_line.item_id.procure_method,
                            'price_unit': fake_line.item_id.standard_price or 0.0,
                            'name': fake_line.item_id.name,
                            'note': fake_line.item_id.name + ' (' + line.name + ')',
                        })
                        product_id = fake_line.item_id
                    else:
                        line_vals.update({
                            'name': line.name,
                            'note': line.name,
                            'product_id': line.product_id.id,
                            'product_qty': line.product_uom_qty,
                            'product_uom': line.product_uom.id,
                            'product_uos_qty': (line.product_uos and line.product_uos_qty) or line.product_uom_qty,
                            'product_uos': (line.product_uos and line.product_uos.id) or line.product_uom.id,
                            'procure_method': line.type,
                            'product_packaging': line.product_packaging,
                            'price_unit': line.product_id.standard_price or 0.0,
                        })
                        product_id = line.product_id
                     
                     
                    if product_id.type in ('product', 'consu'):
                        if not picking_id:
                            picking_id = picking_obj.create(cr, uid, self._prepare_order_picking(cr, uid, order, context=context))
                        line_vals.update({'picking_id': picking_id,})
                        move_id = move_obj.create(cr, uid, line_vals)
                    else:
                        # a service has no stock move
                        move_id = False
                     
                    del line_vals['location_dest_id']
                    del line_vals['date']
                    del line_vals['date_expected']
                    if 'picking_id' in line_vals:
                        del line_vals['picking_id']
                    del line_vals['partner_id']
                    del line_vals['sale_line_id']
                    del line_vals['tracking_id']
                    del line_vals['state']
                     
                    line_vals.update({
                        'move_id': move_id,
                        'date_planned': date_planned,
                    })
                     
                    proc_id = procurement_obj.create(cr, uid, line_vals)
                    proc_ids.append(proc_id)
                    line.write({'procurement_id': proc_id})
                    self.ship_recreate(cr, uid, order, line, move_id, proc_id)
 
        wf_service = netsvc.LocalService("workflow")
        if picking_id:
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        for proc_id in proc_ids:
            wf_service.trg_validate(uid, 'procurement.group', proc_id, 'button_confirm', cr)
 
        val = {}
        if order.state == 'shipping_except':
            val['state'] = 'progress'
            val['shipped'] = False
 
            if (order.order_policy == 'manual'):
                for line in order.order_line:
                    if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
                        val['state'] = 'manual'
                        break
        order.write(val)
        return True
     
     
    def action_ship_create(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context=context):
            self._create_pickings_and_procurements(cr, uid, order, order.order_line, None, context=context)
        return True
     
sale_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
