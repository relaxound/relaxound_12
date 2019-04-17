# -*- coding: utf-8 -*-

from odoo import models, api
from odoo import fields
from odoo.exceptions import UserError


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

    def _picking_assign(self):
        cr = self.env.cr
        ids = self.ids
        uid = self._uid
        context = self._context
        """Try to assign the moves to an existing picking
        that has not been reserved yet and has the same
        procurement group, locations and picking type  (moves should already have them identical)
         Otherwise, create a new picking to assign them to.
        """
        move = self.browse(move_ids)[0]
        pick_obj = self.env.get("stock.picking")
        picks = pick_obj.search(cr, uid, [
            ('group_id', '=', move.group_id.id),
            ('location_id', '=', move.location_id.id),
            ('location_dest_id', '=', move.location_dest_id.id),
            ('picking_type_id', '=', move.picking_type_id.id),
            ('printed', '=', False),
            ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned', 'to_pay'])], limit=1,
                                )
        if picks:
            pick = picks[0]
        else:
            values = self._prepare_picking_assign(cr, uid, move, context=context)
            pick = pick_obj.create(cr, uid, values, context=context)
        return self.write(cr, uid, move_ids, {'picking_id': pick}, context=context)

    def action_payed(self):
        """ Confirms stock move or put it in waiting if it's linked to another move.
        @return: List of ids.
        """
        cr = self.env.cr
        ids = self.ids
        uid = self._uid
        item_id = self.item_id
        context = self._context
        if not context:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        states = {
            'confirmed': [],
            'waiting': [],
            'to_pay': []
        }
        to_assign = {}
        for move in self.browse():
            self.attribute_price(move)
            state = 'confirmed'

            if move.state == 'to_pay':
                state = move.state
            else:
                # if the move is preceeded, then it's waiting (if preceeding move is done, then action_assign has been called already and its state is already available)
                if move.move_orig_ids:
                    state = 'waiting'
                # if the move is split and some of the ancestor was preceeded, then it's waiting as well
                elif move.split_from:
                    move2 = move.split_from
                    while move2 and state != 'waiting':
                        if move2.move_orig_ids:
                            state = 'waiting'
                        move2 = move2.split_from
            states[state].append(move.id)

            if not move.picking_id and move.picking_type_id:
                key = (move.group_id.id, move.location_id.id, move.location_dest_id.id)
                if key not in to_assign:
                    to_assign[key] = []
                to_assign[key].append(move.id)
        #         moves = [move for move in self.browse(cr, uid, states['confirmed'], context=context) if move.procure_method == 'make_to_order']
        #         self._create_procurements(cr, uid, moves, context=context)
        #         for move in moves:
        #             states['waiting'].append(move.id)
        #             states['confirmed'].remove(move.id)
        #         moves = [move for move in self.browse(cr, uid, states['to_pay'], context=context) if move.procure_method == 'make_to_order']
        #         self._create_procurements(cr, uid, moves, context=context)
        moves = [move for move in self.browse(states['to_pay']) if
                 move.procure_method == 'make_to_stock']
        for move in moves:
            states['confirmed'].append(move.id)
            states['to_pay'].remove(move.id)

        for state, write_ids in states.items():
            if len(write_ids):
                self.write(write_ids, {'state': state})
        # assign picking in batch for all confirmed move that share the same details
        for key, move_ids in to_assign.items():
            self._picking_assign(move_ids)
        moves = self.browse()
        self._push_apply(moves)
        return ids

    def action_confirm(self):
        """ Confirms stock move or put it in waiting if it's linked to another move.
        @return: List of ids.
        """
        cr = self.env.cr
        ids = self.ids
        uid = self._uid
        item_id = self.item_id
        context = self._context
        if not context:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        states = {
            'confirmed': [],
            'waiting': [],
            'to_pay': []
        }
        to_assign = {}
        for move in self.browse():
            self.attribute_price(move)
            state = 'confirmed'

            if move.state == 'to_pay':
                state = move.state
            else:
                # if the move is preceeded, then it's waiting (if preceeding move is done, then action_assign has been called already and its state is already available)
                if move.move_orig_ids:
                    state = 'waiting'
                # if the move is split and some of the ancestor was preceeded, then it's waiting as well
                elif move.split_from:
                    move2 = move.split_from
                    while move2 and state != 'waiting':
                        if move2.move_orig_ids:
                            state = 'waiting'
                        move2 = move2.split_from
            states[state].append(move.id)

            if not move.picking_id and move.picking_type_id:
                key = (move.group_id.id, move.location_id.id, move.location_dest_id.id)
                if key not in to_assign:
                    to_assign[key] = []
                to_assign[key].append(move.id)
        moves = [move for move in self.browse(states['confirmed']) if
                 move.procure_method == 'make_to_order']
        self._create_procurements(moves)
        for move in moves:
            states['waiting'].append(move.id)
            states['confirmed'].remove(move.id)
        moves = [move for move in self.browse(states['to_pay']) if
                 move.procure_method == 'make_to_order']
        self._create_procurements(moves)
        moves = [move for move in self.browse(states['to_pay']) if
                 move.procure_method == 'make_to_stock']
        #         for move in moves:
        #             states['waiting'].append(move.id)
        #             states['to_pay'].remove(move.id)

        for state, write_ids in states.items():
            if len(write_ids):
                self.write(write_ids, {'state': state})
        # assign picking in batch for all confirmed move that share the same details
        for key, move_ids in to_assign.items():
            self._picking_assign(move_ids)
        moves = self.browse()
        self._push_apply(moves)
        return ids


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
        cr = self.env.cr
        ids = self.ids
        uid = self._uid
        # item_id = self.item_id
        context = self._context
        todo = []
        todo_force_assign = []
        for picking in self.browse():
            if not picking.move_lines:
                self.launch_packops([picking.id])
            if picking.location_id.usage in ('supplier', 'inventory', 'production'):
                todo_force_assign.append(picking.id)
            for r in picking.move_lines:
                if r.state == 'draft':  # or r.state=='to_pay':
                    todo.append(r.id)
        if len(todo):
            self.env('stock.move').action_confirm(todo)

        if todo_force_assign:
            self.force_assign(todo_force_assign)
        return True

    def action_payed(self):
        self.mapped('package_level_ids').filtered(lambda pl: pl.state == 'to_pay' and not pl.move_ids)._generate_moves()
        # call `_action_confirm` on every draft move
        self.mapped('move_lines') \
            .filtered(lambda move: move.state == 'to_pay')\
            ._action_confirm()
        # call `_action_assign` on every confirmed move which location_id bypasses the reservation
        self.filtered(lambda picking: picking.location_id.usage in ('supplier', 'inventory', 'production') and picking.state == 'confirmed') \
            .mapped('move_lines')._action_assign()
        return True

    @api.multi
    def action_assign(self):
        """ Check availability of picking moves.
        This has the effect of changing the state and reserve quants on available moves, and may
        also impact the state of the picking as it is computed based on move's states.
        @return: True
        """
        self.filtered(lambda picking: picking.state == 'draft').action_confirm()
        moves = self.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))
        if not moves:
            raise UserError('Nothing to check the availability for.')
        # If a package level is done when confirmed its location can be different than where it will be reserved.
        # So we remove the move lines created when confirmed to set quantity done to the new reserved ones.
        package_level_done = self.mapped('package_level_ids').filtered(
            lambda pl: pl.is_done and pl.state == 'confirmed')
        package_level_done.write({'is_done': False})
        moves._action_assign()
        package_level_done.write({'is_done': True})
        return True

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
