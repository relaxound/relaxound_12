# -*- coding: utf-8 -*-

from odoo import models, fields, api,tools,_
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero

class pos_config(models.Model):
    _inherit = 'pos.config'

    @api.depends('session_ids', 'session_ids.state')
    def _compute_current_session(self):
        """If there is an open session, store it to current_session_id / current_session_State.
        """
        for pos_config in self:
            session = pos_config.session_ids.filtered(lambda s: s.user_id.id == self.env.uid and \
                    not s.state == 'closed' and not s.rescue)
            # sessions ordered by id desc
            pos_config.current_session_id = session and session[0].id or False
            pos_config.current_session_state = session and session[0].state or False

    # Methods to open the POS
    def open_ui(self):
        """Open the pos interface with config_id as an extra argument.

        In vanilla PoS each user can only have one active session, therefore it was not needed to pass the config_id
        on opening a session. It is also possible to login to sessions created by other users.

        :returns: dict
        """
        # import pdb;
        # pdb.set_trace()
        # self.ensure_one()
        # check all constraints, raises if any is not met
        self._validate_fields(set(self._fields) - {"cash_control"})
        return {
            'type': 'ir.actions.act_url',
            'url': '/pos/web?config_id=%d' % self.id,
            'target': 'self',
        }

    def open_session_cb(self):
        """ new session button

        create one if none exist
        access cash control interface if enabled or start a session
        """
        # self.ensure_one()
        if not self.current_session_id:
            self._check_company_journal()
            self._check_company_invoice_journal()
            self._check_company_payment()
            self._check_currencies()
            self.current_session_id = self.env['pos.session'].create({
                'user_id': self.env.uid,
                'config_id': self.id
            })
            if self.current_session_id.state == 'opened':
                return self.open_ui()
        return self._open_session(self.current_session_id.id)


    def get_tables_order_count(self):
        """         """
        # self.ensure_one()
        result = []
        for table in self.floor_ids.table_ids.filtered(lambda t: t.active ==  True):
            result.append({'id': table.id, 'orders': self.env['pos.order'].search_count([('state', '=', 'draft'), ('table_id', '=', table.id)])})
        return result

