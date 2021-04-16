from odoo import api, fields, models, _ ,tools
from odoo.addons.mail.wizard.mail_compose_message import _reopen
# from odoo import _, api, fields, models, SUPERUSER_ID, tools
# from odoo.tools import pycompat
# from odoo.tools.safe_eval import safe_eval



class SaleOrderSends(models.TransientModel):
    _name = 'multiple.sale.order.email'
    _inherits = {'mail.compose.message':'composer_id'}
    _batch_size = 500

    is_email = fields.Boolean('Email', default=lambda self: self.env.user.company_id.sale_order_is_email)
    is_print = fields.Boolean('Print', default=lambda self: self.env.user.company_id.sale_order_is_email)
    snailmail_is_letter = fields.Boolean('Send by Post',
                                         help='Allows to send the document by snail mail (coventional posting delivery service)',
                                         default=lambda self: self.env.user.company_id.sale_order_is_snailmail)
    composer_id = fields.Many2one('mail.compose.message', string='Composer', required=True, ondelete='cascade')

    template_id = fields.Many2one('mail.template', 'Email Template',
                                  domain="[('model', '=', 'sale.order')]",
                                  config_parameter='sale.default_email_template',
                                  default=lambda self: self.env.ref('sale.email_template_edi_sale', False))

    printed = fields.Boolean('Is Printed', default=False)

    order_without_email = fields.Text(compute='_compute_order_without_email', string='order(s) that will not be sent')

    order_id = fields.Many2many('sale.order')
    color = fields.Boolean(string='Color', default=lambda self: self.env.user.company_id.snailmail_color)


    @api.model
    def default_get(self, fields):
        res = super(SaleOrderSends, self).default_get(fields)
        res_ids = self._context.get('active_ids')
        composer = self.env['mail.compose.message'].create({
            'composition_mode': 'comment' if len(res_ids) == 1 else 'mass_mail',
        })
        res.update({
            'order_id': res_ids,
            'composer_id': composer.id,
        })
        return res

    @api.multi
    @api.onchange('order_id')
    def _compute_composition_mode(self):
        for wizard in self:
            wizard.composition_mode = 'comment' if len(wizard.order_id) == 1 else 'mass_mail'


    @api.multi
    @api.onchange('template_id')
    def onchange_template_id(self):
        if self.composer_id:
            self.composer_id.template_id = self.template_id.id
            self.composer_id.onchange_template_id_wrapper()

    @api.onchange('is_email')
    def _compute_order_without_email(self):
        for wizard in self:
            if wizard.is_email and len(wizard.order_id) > 1:
                orders = self.env['sale.order'].search([
                    ('id', 'in', self.env.context.get('active_ids')),
                    ('partner_id.email', '=', False)
                ])
                if orders:
                    wizard.order_without_email = "%s\n%s" % (
                        _(
                            "The following order(s) will not be sent by email, because the customers don't have email address."),
                        "\n".join([i.reference or i.display_name for i in orders])
                    )
                else:
                    wizard.order_without_email = False

    @api.multi
    def _send_email(self):
        if self.is_email:
            self.composer_id.send_mail()
            if self.env.context.get('mark_so_as_sent'):
                for order in self.mapped('order_id'):
                    order.write({'sent': True})

    @api.multi
    def _print_document(self):
        """ to override for each type of models that will use this composer."""
        self.ensure_one()
        action = self.order_id.print_quotation()
        action.update({'close_on_report_download': True})
        return action

    @api.multi
    def snailmail_print_action(self):
        for wizard in self:
            letters = wizard._fetch_letters()
            letters.write({'state': 'pending'})
            wizard.order_id.filtered(lambda inv: not inv.sent).write({'sent': True})
            if len(letters) == 1:
                letters._snailmail_print()

    @api.multi
    def action_send_mail(self):
        self.ensure_one()
        # Send the mails in the correct language by splitting the ids per lang.
        # This should ideally be fixed in mail_compose_message, so when a fix is made there this whole commit should be reverted.
        # basically self.body (which could be manually edited) extracts self.template_id,
        # which is then not translated for each customer.

        if self.template_id and self.composition_mode == 'mass_mail':
            active_ids = self.env.context.get('active_ids')
            active_records = self.env[self.model].browse(active_ids)
            langs = active_records.mapped('partner_id.lang')
            default_lang = self.env.context.get('lang', 'en_US')
            for lang in (set(langs) or [default_lang]):
                active_ids_lang = active_records.filtered(lambda r: r.partner_id.lang == lang).ids
                self_lang = self.with_context(active_ids=active_ids_lang, lang=lang)
                self_lang.onchange_template_id()
                self_lang._send_email()

        else:
            self._send_email()
        if self.is_print:
            return self._print_document()
        if self.snailmail_is_letter:
            self.snailmail_print_action()
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def save_as_template(self):
        self.ensure_one()
        self.composer_id.save_as_template()
        self.template_id = self.composer_id.template_id.id
        action = _reopen(self, self.id, self.model, context=self._context)
        action.update({'name': _('Send Order')})
        return action



