# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models


def context(args):
    pass


class procurement_order(models.Model):
    _inherit='purchase.order'
    
    def run(self):                
        new_ids = [x.id for x in self.browse() if x.state not in ('running', 'done', 'cancel')]
        context = dict(context or {}, procurement_auto_defer=True) #When creating
        res = super(procurement_order, self).run()

        #after all the procurements are run, check if some created a draft stock move that needs to be confirmed
        #(we do that in batch because it fasts the picking assignation and the picking state computation)
        move_to_confirm_ids = []
        for procurement in self.browse():
            if procurement.state == "running" and procurement.rule_id and procurement.rule_id.action == "move":
                move_to_confirm_ids += [m.id for m in procurement.move_ids if m.state == 'draft' or m.state=='to_pay']
        if move_to_confirm_ids:
            self.env.get('stock.move').action_confirm()
        # If procurements created other procurements, run the created in batch
        procurement_ids = self.search([('move_dest_id.procurement_id', 'in', new_ids)])
        if procurement_ids:
            res = res and self.run(procurement_ids, autocommit=autocommit)
        return res
    
    def _run_move_create(self, procurement,values):
        ''' Returns a dictionary of values that will be used to create a stock move from a procurement.
        This function assumes that the given procurement has a rule (action == 'move') set on it.

        :param procurement: browse record
        :rtype: dictionary
        '''
                
        newdate = (datetime.strptime(procurement.date_planned, '%Y-%m-%d %H:%M:%S') - relativedelta(days=procurement.rule_id.delay or 0)).strftime('%Y-%m-%d %H:%M:%S')
        group_id = False
        if procurement.rule_id.group_propagation_option == 'propagate':
            group_id = procurement.group_id and procurement.group_id.id or False
        elif procurement.rule_id.group_propagation_option == 'fixed':
            group_id = procurement.rule_id.group_id and procurement.rule_id.group_id.id or False
        #it is possible that we've already got some move done, so check for the done qty and create
        #a new move with the correct qty
        already_done_qty = 0
        for move in procurement.move_ids:
            already_done_qty += move.product_uom_qty if move.state == 'done' else 0
        qty_left = max(procurement.product_qty - already_done_qty, 0)
        vals = {
            'name': procurement.name,
            'company_id': procurement.rule_id.company_id.id or procurement.rule_id.location_src_id.company_id.id or procurement.rule_id.location_id.company_id.id or procurement.company_id.id,
            'product_id': procurement.product_id.id,
            'product_uom': procurement.product_uom.id,
            'product_uom_qty': qty_left,
            'partner_id': procurement.rule_id.partner_address_id.id or (procurement.group_id and procurement.group_id.partner_id.id) or False,
            'location_id': procurement.rule_id.location_src_id.id,
            'location_dest_id': procurement.location_id.id,
            'move_dest_id': procurement.move_dest_id and procurement.move_dest_id.id or False,
            'procurement_id': procurement.id,
            'rule_id': procurement.rule_id.id,
            'procure_method': procurement.rule_id.procure_method,
            'origin': procurement.origin,
            'picking_type_id': procurement.rule_id.picking_type_id.id,
            'group_id': group_id,
            'route_ids': [(4, x.id) for x in procurement.route_ids],
            'warehouse_id': procurement.rule_id.propagate_warehouse_id.id or procurement.rule_id.warehouse_id.id,
            'date': newdate,
            'date_expected': newdate,
            'propagate': procurement.rule_id.propagate,
            'priority': procurement.priority,
        }
 
        sale_order=False
#        sale_order=procurement.sale_line_id.order_id
#         if not(sale_order):        
        poids=self.env.get('procurement.order').search([('id', '!=', procurement.id),('group_id','=',procurement.group_id.id)])
        for poid in poids:
            po= self.env.get('procurement.order').browse()
            if po.sale_line_id.order_id:
                sale_order=po.sale_line_id.order_id
        
        if (sale_order and not(sale_order.payment_method_id)) or (sale_order and not(sale_order.payment_method_id.save)):
            vals['state']='to_pay'
        
        #print vals
        
        return vals
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: