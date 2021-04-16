from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin','sale.order']
    _description = "Sale Order"


    name = fields.Char('Sales Team', translate=True)
    currency_id = fields.Many2one(
        "res.currency", related='company_id.currency_id',
        string="Currency", readonly=True)
    user_id = fields.Many2one('res.users', string='Team Leader')
    member_ids = fields.One2many('res.users', 'sale_team_id', string='Channel Members')

    reply_to = fields.Char(string='Reply-To',
                           help="The email address put in the 'Reply-To' of all emails sent by Odoo about cases in this Sales Team")
    color = fields.Integer(string='Color Index', help="The color of the channel")

    dashboard_graph_model = fields.Selection([], string="Content",
                                             help='The graph this channel will display in the Dashboard.\n')
    dashboard_graph_period = fields.Selection([
        ('week', 'Last Week'),
        ('month', 'Last Month'),
        ('year', 'Last Year'),
    ], string='Scale', default='month', help="The time period this channel's dashboard graph will consider.")
    message_follower_ids = fields.One2many(
        'mail.followers', 'res_id', string='Followers',
        domain=lambda self: [('res_model', '=', self._name)])
    message_ids = fields.One2many(
        'mail.message', 'res_id', string='Messages',
        domain=lambda self: [('model', '=', self._name)], auto_join=True)

    name = fields.Char(string='Name', required=True, translate=True)
    user_ids = fields.Many2many('res.users', string='Recipients', domain="[('share', '=', False)]")

    next_run_date = fields.Date(string='Next Send Date')
    template_id = fields.Many2one('mail.template', string='Email Template',
                                  domain="[('model','=','digest.digest')]",
                                  default=lambda self: self.env.ref('digest.digest_mail_template'),
                                  required=True)
    currency_id = fields.Many2one(related="company_id.currency_id", string='Currency', readonly=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)

    kpi_res_users_connected = fields.Boolean('Connected Users')
    kpi_mail_message_total = fields.Boolean('Messages')
    color = fields.Boolean(string='Color', default=lambda self: self.env.user.company_id.snailmail_color)
