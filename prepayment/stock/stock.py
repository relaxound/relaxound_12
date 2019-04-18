from odoo import models, api
from odoo import fields


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
                move_waiting |= move
            else:
                if move.procure_method == 'make_to_order':
                    move_to_pay |= move
                else:
                    move_to_confirm |= move
            if move._should_be_assigned():
                key = (move.group_id.id, move.location_id.id, move.location_dest_id.id)
                if key not in to_assign:
                    to_assign[key] = self.env['stock.move']
                to_assign[key] |= move

        # create procurements for make to order moves
        # for move in move_create_proc:
        #     values = move._prepare_procurement_values()
        #     origin = (move.group_id and move.group_id.name or (move.origin or move.picking_id.name or "/"))
        #     # self.env['procurement.group'].run(move.product_id, move.product_uom_qty, move.product_uom, move.location_id,
        #     #                                   move.rule_id and move.rule_id.name or "/", origin,
        #     #                                   values)

        move_to_confirm.write({'state': 'confirmed'})
        move_to_pay.write({'state': 'to_pay'})
        (move_waiting | move_create_proc | move_to_pay).write({'state': 'waiting'})

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
        move_to_pay = self.env['stock.move']
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
        # for move in move_create_proc:
        #     values = move._prepare_procurement_values()
        #     origin = (move.group_id and move.group_id.name or (move.origin or move.picking_id.name or "/"))
        #     # self.env['procurement.group'].run(move.product_id, move.product_uom_qty, move.product_uom, move.location_id,
        #     #                                   move.rule_id and move.rule_id.name or "/", origin,
        #     #                                   values)

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

    @api.multi
    def action_confirm(self):
        self.mapped('package_level_ids').filtered(lambda pl: pl.state == 'draft' and not pl.move_ids)._generate_moves()
        # call `_action_confirm` on every draft move
        self.mapped('move_lines') \
            .filtered(lambda move: move.state == 'draft') \
            ._action_confirm()
        # call `_action_assign` on every confirmed move which location_id bypasses the reservation
        self.filtered(lambda picking: picking.location_id.usage in (
        'supplier', 'inventory', 'production') and picking.state == 'confirmed') \
            .mapped('move_lines')._action_assign()
        return True

    def action_payed(self):
        self.mapped('package_level_ids').filtered(lambda pl: pl.state == 'to_pay' and not pl.move_ids)._generate_moves()
        # call `_action_confirm` on every draft move
        self.mapped('move_lines') \
            .filtered(lambda move: move.state == 'to_pay') \
            ._action_payed()
        # call `_action_assign` on every confirmed move which location_id bypasses the reservation
        self.filtered(lambda picking: picking.location_id.usage in (
            'supplier', 'inventory', 'production') and picking.state == 'confirmed') \
            .mapped('move_lines')._action_assign()
        return True

    @api.depends('move_type', 'move_lines.state', 'move_lines.picking_id')
    @api.one
    def _compute_state(self):
        ''' State of a picking depends on the state of its related stock.move
        - Draft: only used for "planned pickings"
        - Waiting: if the picking is not ready to be sent so if
          - (a) no quantity could be reserved at all or if
          - (b) some quantities could be reserved and the shipping policy is "deliver all at once"
        - Waiting another move: if the picking is waiting for another move
        - Ready: if the picking is ready to be sent so if:
          - (a) all quantities are reserved or if
          - (b) some quantities could be reserved and the shipping policy is "as soon as possible"
        - Done: if the picking is done.
        - Cancelled: if the picking is cancelled
        '''
        if not self.move_lines:
            self.state = 'draft'
        elif any(move.state == 'draft' for move in self.move_lines):  # TDE FIXME: should be all ?
            self.state = 'draft'
        elif all(move.state == 'to_pay' for move in self.move_lines):
            self.state = 'to_pay'
        elif all(move.state == 'cancel' for move in self.move_lines):
            self.state = 'cancel'
        elif all(move.state in ['cancel', 'done'] for move in self.move_lines):
            self.state = 'done'
        else:
            relevant_move_state = self.move_lines._get_relevant_state_among_moves()
            if relevant_move_state == 'partially_available':
                self.state = 'assigned'
            else:
                self.state = relevant_move_state

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