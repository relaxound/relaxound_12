from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    iface_create_sale_order = fields.Boolean(
        string="Create Sale Orders",
        compute="_compute_iface_create_sale_order",
        store=True)

    iface_create_draft_sale_order = fields.Boolean(
        string="Create Draft Sale Orders",
        default=True,
        help="If checked, the cashier will have the possibility to create"
        " a draft Sale Order, based on the current draft PoS Order.",
    )

    iface_create_confirmed_sale_order = fields.Boolean(
        string="Create Confirmed Sale Orders",
        default=True,
        help="If checked, the cashier will have the possibility to create"
        " a confirmed Sale Order, based on the current draft PoS Order.",
    )

    iface_create_delivered_sale_order = fields.Boolean(
        string="Create Delivered Sale Orders",
        default=True,
        help="If checked, the cashier will have the possibility to create"
        " a confirmed sale Order, based on the current draft PoS Order.\n"
        " the according picking will be marked as delivered. Only invoices"
        " process will be possible.",
    )
    # View sale order
    iface_view_pos_order = fields.Boolean(string="View POS Sale Orders",default=True,help="View pos sale orders.")

    @api.depends(
        "iface_create_draft_sale_order",
        "iface_create_confirmed_sale_order",
        "iface_create_delivered_sale_order",
        "iface_view_pos_order"
    )
    def _compute_iface_create_sale_order(self):
        for config in self:
            config.iface_create_sale_order = any([
                config.iface_create_draft_sale_order,
                config.iface_create_confirmed_sale_order,
                config.iface_create_delivered_sale_order,
                config.iface_view_pos_order,
            ])

