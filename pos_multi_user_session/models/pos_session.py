

from odoo import models, fields, api,tools,_
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero

class PosSession(models.Model):
    _inherit = 'pos.session'


    def open_frontend_cb(self):
        """Open the pos interface with config_id as an extra argument.

        In vanilla PoS each user can only have one active session, therefore it was not needed to pass the config_id
        on opening a session. It is also possible to login to sessions created by other users.

        :returns: dict
        """
        if not self.ids:
            return {}
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': '/pos/web?config_id=%d' % self.config_id.id,
        }

