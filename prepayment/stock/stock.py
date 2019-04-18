# -*- coding: utf-8 -*-

from odoo import models, api
from odoo import fields
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_round, float_is_zero


class stock_move(models.Model):
    _inherit = 'stock.move'

    state = fields.Selection([
        ('draft', 'New'), ('to_pay', 'Waiting Payment'),
        ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Move'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('assigned', 'Available'),
        ('done', 'Done')], string='Status',
        copy=False, default='draft', index=True, readonly=True, track_visibility='onchange',
        help="* New: When the stock move is created and not yet confirmed.\n"
             "* Waiting Another Move: This state can be seen when a move is waiting for another one, for example in a chained flow.\n"
             "* Waiting Availability: This state is reached when the procurement resolution is not straight forward. It may need the scheduler to run, a component to be manufactured...\n"
             "* Available: When products are reserved, it is set to \'Available\'.\n"
             "* Done: When the shipment is processed, the state is \'Done\'.")

    def _search_picking_for_assignation(self):
        self.ensure_one()
        picking = self.env['stock.picking'].search([
            ('group_id', '=', self.group_id.id),
            ('location_id', '=', self.location_id.id),
            ('location_dest_id', '=', self.location_dest_id.id),
            ('picking_type_id', '=', self.picking_type_id.id),
            ('printed', '=', False),
            ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available','to_pay'])], limit=1)
        return picking

    # def _picking_assign(self, move_ids):
    #     cr = self.env.cr
    #     ids = self.ids
    #     uid = self._uid
    #     context = self._context
    #     """Try to assign the moves to an existing picking
    #     that has not been reserved yet and has the same
    #     procurement group, locations and picking type  (moves should already have them identical)
    #      Otherwise, create a new picking to assign them to.
    #     """
    #     move = self.browse(move_ids)[0]
    #     pick_obj = self.env.get("stock.picking")
    #     picks = pick_obj.search(cr, uid, [
    #         ('group_id', '=', move.group_id.id),
    #         ('location_id', '=', move.location_id.id),
    #         ('location_dest_id', '=', move.location_dest_id.id),
    #         ('picking_type_id', '=', move.picking_type_id.id),
    #         ('printed', '=', False),
    #         ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned', 'to_pay'])], limit=1,
    #                             )
    #     if picks:
    #         pick = picks[0]
    #     else:
    #         values = self._prepare_picking_assign(cr, uid, move, context=context)
    #         pick = pick_obj.create(cr, uid, values, context=context)
    #     return self.write(cr, uid, move_ids, {'picking_id': pick}, context=context)

    def _action_payed(self, merge=True, merge_into=False):
        """ Confirms stock move or put it in waiting if it's linked to another move.
        :param: merge: According to this boolean, a newly confirmed move will be merged
        in another move of the same picking sharing its characteristics.
        """
        move_create_proc = self.env['stock.move']
        move_to_confirm = self.env['stock.move']
        move_waiting = self.env['stock.move']
        move_to_pay = self.env['stock.move']

        to_assign = {}
        for move in self:
            # if the move is preceeded, then it's waiting (if preceeding move is done, then action_assign has been called already and its state is already available)
            if move.move_orig_ids:
                move_to_pay |= move

            else:
                if move.procure_method == 'make_to_order':
                    move_create_proc |= move
                else:
                    move_to_confirm |= move
            if move._should_be_assigned():
                key = (move.group_id.id, move.location_id.id, move.location_dest_id.id)
                if key not in to_assign:
                    to_assign[key] = self.env['stock.move']
                to_assign[key] |= move

        # create procurements for make to order moves
        for move in move_create_proc:
            values = move._prepare_procurement_values()
            origin = (move.group_id and move.group_id.name or (move.origin or move.picking_id.name or "/"))
            self.env['procurement.group'].run(move.product_id, move.product_uom_qty, move.product_uom, move.location_id,
                                              move.rule_id and move.rule_id.name or "/", origin,
                                              values)

        move_to_confirm.write({'state': 'confirmed'})
        move_to_pay.write({'state': 'to_pay'})
        (move_waiting | move_create_proc).write({'state': 'waiting'})


        # assign picking in batch for all confirmed move that share the same details
        for moves in to_assign.values():
            moves._assign_picking()
        self._push_apply()
        if merge:
            return self._merge_moves(merge_into=merge_into)
        return self

    def _action_confirm(self, merge=True, merge_into=False):
        """ Confirms stock move or put it in waiting if it's linked to another move.
        :param: merge: According to this boolean, a newly confirmed move will be merged
        in another move of the same picking sharing its characteristics.
        """
        move_create_proc = self.env['stock.move']
        move_to_confirm = self.env['stock.move']
        move_waiting = self.env['stock.move']

        to_assign = {}
        for move in self:
            # if the move is preceeded, then it's waiting (if preceeding move is done, then action_assign has been called already and its state is already available)
            if move.move_orig_ids:
                move_waiting |= move
            else:
                if move.procure_method == 'make_to_order':
                    move_create_proc |= move
                else:
                    move_to_confirm |= move
            if move._should_be_assigned():
                key = (move.group_id.id, move.location_id.id, move.location_dest_id.id)
                if key not in to_assign:
                    to_assign[key] = self.env['stock.move']
                to_assign[key] |= move

        # create procurements for make to order moves
        for move in move_create_proc:
            values = move._prepare_procurement_values()
            origin = (move.group_id and move.group_id.name or (move.origin or move.picking_id.name or "/"))
            self.env['procurement.group'].run(move.product_id, move.product_uom_qty, move.product_uom, move.location_id,
                                              move.rule_id and move.rule_id.name or "/", origin,
                                              values)

        move_to_confirm.write({'state': 'confirmed'})
        (move_waiting | move_create_proc).write({'state': 'waiting'})

        # assign picking in batch for all confirmed move that share the same details
        for moves in to_assign.values():
            moves._assign_picking()
        self._push_apply()
        if merge:
            return self._merge_moves(merge_into=merge_into)
        return self

class stock_picking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def run_prepayment_cron(self):

        order_obj = self.env['sale.order']

        for picking in self.search([('state', '=like', 'to_pay')]):
            for sale in order_obj.search([]):
                if picking in sale.picking_ids:
                    paid = True
                    for inv in sale.invoice_ids:
                        if inv.state != 'paid':
                            paid = False
                            break

                    if paid:
                        picking.action_payed()

    def action_confirm(self):
        self.mapped('package_level_ids').filtered(lambda pl: pl.state == 'draft' and not pl.move_ids)
        self.mapped('move_lines') \
            .filtered(lambda move: move.state == 'draft') \
            ._action_confirm()

        self.filtered(lambda picking: picking.location_id.usage in (
            'supplier', 'inventory', 'production') and picking.state == 'confirmed') \
            .mapped('move_lines')._action_assign()
        return True


    def action_payed(self):
        self.mapped('package_level_ids').filtered(lambda pl: pl.state == 'to_pay' and not pl.move_ids)
        # call `_action_confirm` on every draft move
        self.mapped('move_lines') \
            .filtered(lambda move: move.state == 'to_pay') \
            ._action_payed()
        self.filtered(lambda picking: picking.location_id.usage in (
            'supplier', 'inventory', 'production') and picking.state == 'confirmed') \
            .mapped('move_lines')._action_assign()

        return True

    # def _compute_state(self):
    #     ''' State of a picking depends on the state of its related stock.move
    #     - Draft: only used for "planned pickings"
    #     - Waiting: if the picking is not ready to be sent so if
    #       - (a) no quantity could be reserved at all or if
    #       - (b) some quantities could be reserved and the shipping policy is "deliver all at once"
    #     - Waiting another move: if the picking is waiting for another move
    #     - Ready: if the picking is ready to be sent so if:
    #       - (a) all quantities are reserved or if
    #       - (b) some quantities could be reserved and the shipping policy is "as soon as possible"
    #     - Done: if the picking is done.
    #     - Cancelled: if the picking is cancelled
    #     '''
    #     if not self.move_lines:
    #         self.state = 'draft'
    #     elif any(move.state == 'draft' for move in self.move_lines):  # TDE FIXME: should be all ?
    #         self.state = 'draft'
    #     elif all(move.state == 'to_pay' for move in self.move_lines):
    #         self.state = 'to_pay'
    #     elif all(move.state == 'cancel' for move in self.move_lines):
    #         self.state = 'cancel'
    #     elif all(move.state in ['cancel', 'done'] for move in self.move_lines):
    #         self.state = 'done'
    #     else:
    #         relevant_move_state = self.move_lines._get_relevant_state_among_moves()
    #         if relevant_move_state == 'partially_available':
    #             self.state = 'assigned'
    #         else:
    #             self.state = relevant_move_state

    def _state_get(self):
        '''The state of a picking depends on the state of its related stock.move
            draft: the picking has no line or any one of the lines is draft
            done, draft, cancel: all lines are done / draft / cancel
            confirmed, waiting, assigned, partially_available depends on move_type (all at once or partial)
        '''
        res = {}
        for pick in self.browse():
            if not pick.move_lines:
                res[pick.id] = pick.launch_pack_operations and 'assigned' or 'draft'
                continue
            if any([x.state == 'draft' for x in pick.move_lines]):
                res[pick.id] = 'draft'
                continue
            if any([x.state == 'to_pay' for x in pick.move_lines]):
                res[pick.id] = 'to_pay'
                continue
            if all([x.state == 'cancel' for x in pick.move_lines]):
                res[pick.id] = 'cancel'
                continue
            if all([x.state in ('cancel', 'done') for x in pick.move_lines]):
                res[pick.id] = 'done'
                continue
    
            order = {'confirmed': 0, 'waiting': 1, 'assigned': 2}
            order_inv = {0: 'confirmed', 1: 'waiting', 2: 'assigned'}
            lst = [order[x.state] for x in pick.move_lines if x.state not in ('cancel', 'done')]
            if pick.move_type == 'one':
                res[pick.id] = order_inv[min(lst)]
            else:
                # we are in the case of partial delivery, so if all move are assigned, picking
                # should be assign too, else if one of the move is assigned, or partially available, picking should be
                # in partially available state, otherwise, picking is in waiting or confirmed state
                res[pick.id] = order_inv[max(lst)]
                if not all(x == 2 for x in lst):
                    if any(x == 2 for x in lst):
                        res[pick.id] = 'partially_available'
                    else:
                        # if all moves aren't assigned, check if we have one product partially available
    
                        for move in pick.move_lines:
                            if move.partially_available:
                                res[pick.id] = 'partially_available'
                                break
        return res

    def _get_pickings(self):
        res = set()
        for move in self.browse():
            if move.picking_id:
                res.add(move.picking_id.id)
        return list(res)

    state = fields.Selection([('draft', 'New'),
                              ('draft', 'Draft'),
                              ('to_pay', 'Waiting Payment'),
                              ('cancel', 'Cancelled'),
                              ('waiting', 'Waiting Another Operation'),
                              ('confirmed', 'Waiting Availability'),
                              ('partially_available', 'Partially Available'),
                              ('assigned', 'Available'),
                              ('done', 'Done'),
                              ], string='Status', readonly=True, index=True, track_visibility='onchange',
                             help="""
                * Draft: not confirmed yet and will not be scheduled until confirmed\n
                * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n
                * Waiting Availability: still waiting for the availability of products\n
                * Partially Available: some products are available and reserved\n
                * Ready to Transfer: products reserved, simply waiting for confirmation.\n
                * Transferred: has been processed, can't be modified or cancelled anymore\n
                * Cancelled: has been cancelled, can't be confirmed anymore"""
                             )

    @api.one
    def action_to_pay(self):
        for ml in self.move_lines:
            ml.state = 'to_pay'

        return True
