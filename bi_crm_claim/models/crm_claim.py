# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

from odoo.addons import decimal_precision as dp

from werkzeug.urls import url_encode


class crm_claim_stage(models.Model):
    _name = "crm.claim.stage"
    _description = "Claim stages"
    _rec_name = 'name'
    _order = "sequence"

    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', help="Used to order stages. Lower is better.", default=lambda *args: 1)
    team_ids = fields.Many2many('crm.team', 'crm_team_claim_stage_rel', 'stage_id', 'team_id', string='Teams',
                                help="Link between stages and sales teams. When set, this limitate the current stage to the selected sales teams.")
    case_default = fields.Boolean('Common to All Teams',
                                  help="If you check this field, this stage will be proposed by default on each sales team. It will not assign this stage to existing teams.")

    _defaults = {
        'sequence': lambda *args: 1
    }


class crm_claim_tags(models.Model):
    _name = "crm.claim.tag"
    _description = "Claim Tages"
    _rec_name = 'name'
    _order = "sequence"

    name = fields.Char('Tag Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', help="Used to order stages. Lower is better.", default=lambda *args: 1)
    description = fields.Text('Reason')

    _defaults = {
        'sequence': lambda *args: 1
    }


class crm_claim(models.Model):
    _name = "crm.claim"
    _description = "Claim"
    _order = "priority,date desc"
    _inherit = ['mail.thread']

    @api.multi
    def _get_default_stage_id(self):
        """ Gives default stage_id """
        team_id = self.env['crm.team'].sudo()._get_default_team_id()
        return self._stage_find(team_id=team_id.id, domain=[('sequence', '=', '1')])

    @api.depends('claim_order_line.subtotal')
    def calculation_amount_all(self):
        # import pdb;pdb.set_trace()
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.claim_order_line:
                amount_untaxed += line.subtotal
                amount_tax += line.tax_amount
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    id = fields.Integer('ID', readonly=True)
    name = fields.Char('Claim Subject', required=True)
    active = fields.Boolean('Active', default=lambda *a: 1)
    action_next = fields.Char('Next Action')
    date_action_next = fields.Datetime('Next Action Date')
    description = fields.Text('Description')
    resolution = fields.Text('Resolution')
    create_date = fields.Datetime('Creation Date', readonly=True)
    write_date = fields.Datetime('Update Date', readonly=True)
    date_deadline = fields.Datetime('Deadline')
    date_closed = fields.Datetime('Closed', readonly=True)
    date = fields.Datetime('Claim Date', index=True,
                           default=lambda self: self._context.get('date', fields.Datetime.now()))
    categ_id = fields.Many2one('crm.claim.category', 'Category')
    priority = fields.Selection([('0', 'Low'), ('1', 'Normal'), ('2', 'High')], 'Priority', default='1')
    type_action = fields.Selection([('correction', 'Corrective Action'), ('prevention', 'Preventive Action')],
                                   'Action Type')
    user_id = fields.Many2one('res.users', 'Responsible', track_visibility='always',
                              default=lambda self: self.env['res.users'].browse(self._context['uid']))
    user_fault = fields.Char('Trouble Responsible')
    team_id = fields.Many2one('crm.team', 'Sales Team', oldname='section_id', \
                              index=True, help="Responsible sales team." \
                                               " Define Responsible user and Email account for" \
                                               " mail gateway.")  # ,default=lambda self: self.env['crm.team']._get_default_team_id()
    currency_id = fields.Many2one("res.currency", related='partner_id.currency_id', string="Currency", readonly=True,
                                  required=True)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('crm.case'))
    partner_id = fields.Many2one('res.partner', 'Partner')
    email_cc = fields.Text('Watchers Emails', size=252,
                           help="These email addresses will be added to the CC field of all inbound and outbound emails for this record before being sent. Separate multiple email addresses with a comma")
    email_from = fields.Char('Email', size=128, help="Destination email for email gateway.")
    partner_phone = fields.Char('Phone')
    stage_id = fields.Many2one('crm.claim.stage', 'Stage',
                               track_visibility='onchange')  # domain="['|', ('team_ids', '=', team_id), ('case_default', '=', True)]",default=lambda self:self.env['crm.claim']._get_default_stage_id()
    cause = fields.Text('Root Cause')
    ref = fields.Reference(
        selection=[('res.partner', 'Partner'), ('product.product', 'Product'), ('account.invoice', 'Invoice'),
                   ('sale.order', 'Sales Order'),
                   ('stock.production.lot', 'Serial Number'),
                   ('purchase.order', 'Purchase Order'),
                   ('stock.picking', 'Delivery Order'),
                   ('project.project', 'Project'),
                   ('project.task', 'Project task')], string="Reference")
    claim_order_line = fields.One2many('claim.order.line', 'claim_order_id', string='Order Lines',
                                       states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True,
                                       auto_join=True)
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True,
                                     compute='calculation_amount_all', track_visibility='onchange', track_sequence=5)
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='calculation_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='calculation_amount_all',
                                   track_visibility='always', track_sequence=6)

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self, email=False):
        # import pdb;
        # pdb.set_trace()
        if not self.partner_id:
            return {'value': {'email_from': False, 'partner_phone': False}}
        address = self.pool.get('res.partner').browse(self.partner_id)
        return {'value': {'email_from': address.email, 'partner_phone': address.phone}}

    @api.model
    def create(self, vals):
        context = dict(self._context or {})
        if vals.get('team_id') and not self._context.get('default_team_id'):
            context['default_team_id'] = vals.get('team_id')

        # context: no_log, because subtype already handle this
        return super(crm_claim, self).create(vals)

    @api.multi
    def message_new(self, msg, custom_values=None):
        if custom_values is None:
            custom_values = {}
        desc = html2plaintext(msg.get('body')) if msg.get('body') else ''
        defaults = {
            'name': msg.get('subject') or _("No Subject"),
            'description': desc,
            'email_from': msg.get('from'),
            'email_cc': msg.get('cc'),
            'partner_id': msg.get('author_id', False),
        }
        if msg.get('priority'):
            defaults['priority'] = msg.get('priority')
        defaults.update(custom_values)
        return super(crm_claim, self).message_new(msg, custom_values=defaults)


class crm_claim_line(models.Model):
    _name = 'claim.order.line'
    _description = 'Claim Order Line'
    _order = 'claim_order_id,id'

    @api.multi
    def get_product_ids(self):
        product_ids = {}
        for order_lines in self.reference.order_line:
            product_ids[order_lines.product_id.id] = order_lines.product_id.id
        product_ids = product_ids.keys()
        return product_ids

    @api.multi
    def auto_fill_data(self):

        orders = self.env['sale.order.line'].search(
            [('product_id', '=', self.product_id.id), ('order_id', '=', self.reference.id)])
        if orders:
            vals = {'claim_qty': orders.product_uom_qty,
                    'tax_id': orders.tax_id,
                    'single_unit': orders.single_unit,
                    'subtotal': orders.price_subtotal,
                    'tax_amount': orders.price_tax
                    }
            print("&" * 20)
            print(orders)
            print(vals)
            self.update(vals)
        else:
            product_price = 0

            for i in self.claim_order_id.partner_id.property_product_pricelist.item_ids:
                if i.categ_id == self.product_id.categ_id:
                    product_price = i.price.replace(" EUR", '')
                elif i.product_id.default_code == self.product_id.default_code:
                    product_price = i.price.replace(" EUR", '')

            custom_claim_qty = 1
            taxes_id = self.product_id.product_tmpl_id.taxes_id

            vals = {'claim_qty': custom_claim_qty,
                    'tax_id': taxes_id,
                    'single_unit': custom_claim_qty,
                    'subtotal': custom_claim_qty * product_price,
                    # 'tax_amount': orders.price_tax,
                    }

            print(vals)
            self.update(vals)

    @api.multi
    def product_existance_checking(self, exist_product):
        if exist_product:
            if self.product_id.id not in exist_product:
                raise UserError(_('Product is not exist in Selected SO!!!'))
        else:
            pass
        self.auto_fill_data()
        return True

    @api.onchange('product_id', 'reference')
    def get_values(self):
        for lines in self:
            if (lines.product_id):
                products = lines.get_product_ids()
                lines.product_existance_checking(products)

    claim_order_id = fields.Many2one('crm.claim', string='Order Reference', required=True, ondelete='cascade',
                                     index=True, copy=False)
    product_id = fields.Many2one('product.product', string='Product', readonly=False, change_default=False,
                                 ondelete='restrict')
    stage_id = fields.Text(string='State', default='1')
    currency_id = fields.Many2one(related='claim_order_id.currency_id', depends=['claim_order_id'], store=True,
                                  string='Currency', readonly=True)
    company_id = fields.Many2one(related='claim_order_id.company_id', string='Company', store=True, readonly=True)
    claim_qty = fields.Float(string='Claimed Qty', readonly=False)
    single_unit = fields.Float(string='Single Unit', required=True)
    tags = fields.Many2one('crm.claim.tag', string='Tags', required=True)
    type_action = fields.Selection([('correction', 'Corrective Action'), ('prevention', 'Preventive Action')],
                                   'Action Type')
    reference = fields.Many2one('sale.order', string='Order Reference', ondelete='cascade', index=True, copy=False)
    subtotal = fields.Monetary(string='Subtotal', store=True)
    tax_amount = fields.Float(string='Total Tax', store=True)
    tax_id = fields.Many2many('account.tax', string='Taxes', readonly=False)


class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _claim_count(self):
        for claim in self:
            claim_ids = self.env['crm.claim'].search([('partner_id', '=', claim.id)])
            claim.claim_count = len(claim_ids)

    @api.multi
    def claim_button(self):
        self.ensure_one()
        return {
            'name': 'Partner Claim',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'crm.claim',
            'domain': [('partner_id', '=', self.id)],
        }

    claim_count = fields.Integer(string='# Claims', compute='_claim_count')


class crm_claim_category(models.Model):
    _name = "crm.claim.category"
    _description = "Category of claim"

    name = fields.Char('Name', required=True, translate=True)
    team_id = fields.Many2one('crm.team', 'Sales Team')