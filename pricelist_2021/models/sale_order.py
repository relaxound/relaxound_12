from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from dateutil.relativedelta import relativedelta
from datetime import datetime , timedelta,date


class CustomSaleOrderform(models.Model):
    _inherit = "sale.order"

    discount = fields.Float('Discount',compute='_compute_discount')
    total_new = fields.Float('Total',compute='_compute_total_new')
    shipping_amount_new = fields.Float('Shipping',compute='_compute_shipping_amount')
    spl_discount = fields.Float('Special Discount',compute='_compute_spl_discount')
    untaxed_amount_new = fields.Float('Total',compute='_compute_untaxed_amount')
    untaxed_total = fields.Float('Amount After Discount',compute='_compute_total_untaxed')
    amount_total_new = fields.Float('Total',compute='_compute_total')
    amount_tax_new = fields.Float('Taxes',compute='_compute_tax_new')
    discount_2 = fields.Float(compute='_compute_discount_2')
    set_desription = fields.Char('Note',compute='_set_description')
    set_desription1 = fields.Text('Note',compute='_set_description')

    super_spl_discount = fields.Boolean('Super Special Discount')
    hide = fields.Boolean(string='Hide', compute="_compute_hide")
    hide_spl_discount = fields.Boolean(string='Hide discount' ,compute='_compute_hide_discount')
    hide_2_discount = fields.Boolean(string='Hide 2% discount' ,compute='_compute_hide_2_discount')
    hide_france_note = fields.Boolean(string='Hide france desc' ,compute='_compute_hide_france_desc')

    date_order_compute = fields.Boolean(string='Date of the order',
                                  compute='_date_order_compute')

    @api.depends('pricelist_id')
    def _date_order_compute(self):
        for rec in self:
            # if rec.pricelist_id.name == 'Preismodell 2021' and ((rec.date_order and rec.date_order >= date(2021, 1, 1)) or (not rec.date_order and date.today() >= date(2021, 1, 1))):
            if rec.pricelist_id.name == 'Preismodell 2021':
                rec.date_order_compute = True
            else:
                rec.date_order_compute = False

    @api.depends('pricelist_id')
    def _compute_hide_france_desc(self):
        # simple logic, but you can do much more here
        for rec in self:
            # datetime.strptime('1/1/2021', "%m/%d/%y")
            if rec.date_order_compute and rec.partner_id.is_retailer and rec.partner_id.country_id.name == 'France' and rec.pricelist_id.name == 'Preismodell 2021':
                rec.hide_france_note = True
            else:
                rec.hide_france_note = False



    @api.depends('pricelist_id')
    def _compute_hide_2_discount(self):
        # simple logic, but you can do much more here
        for rec in self:
            # datetime.strptime('1/1/2021', "%m/%d/%y")
            if rec.date_order_compute and rec.partner_id.is_retailer and rec.pricelist_id.name == 'Preismodell 2021' and rec.partner_id.country_id.name != 'France':
                rec.hide_2_discount = True
            else:
                rec.hide_2_discount = False

    @api.depends('super_spl_discount','pricelist_id')
    def _compute_hide_discount(self):
        for rec in self:
            if rec.date_order_compute and rec.partner_id.is_retailer and rec.super_spl_discount and rec.pricelist_id.name == 'Preismodell 2021':
                rec.hide_spl_discount = True
            else:
                rec.hide_spl_discount = False


    @api.depends('pricelist_id')
    def _compute_hide(self):
        # simple logic, but you can do much more here
        for rec in self:
            if rec.date_order_compute and rec.pricelist_id.name == 'Preismodell 2021':
                rec.hide = True
            else:
                rec.hide = False

    @api.multi
    @api.onchange('partner_id','order_line')
    def _compute_discount(self):
        for rec in self:
            if rec.date_order_compute and rec.pricelist_id.name == 'Preismodell 2021':
                if rec.amount_untaxed >= 500 and rec.amount_untaxed < 1000:
                    rec.discount = (5 * (rec.amount_untaxed)) / 100

                elif rec.amount_untaxed >= 1000 and rec.amount_untaxed < 1500:
                    rec.discount = (7 * (rec.amount_untaxed)) / 100

                elif rec.amount_untaxed >= 1500:
                    rec.discount = (10 * (rec.amount_untaxed)) / 100

                elif rec.amount_untaxed < 500:
                    rec.discount = 0

    @api.multi
    @api.onchange('partner_id','order_line')
    def _compute_total_new(self):
        for rec in self:
            if rec.date_order_compute and rec.pricelist_id.name == 'Preismodell 2021':
                if rec.amount_untaxed >= 500 and rec.amount_untaxed < 1000:
                    rec.total_new = rec.amount_untaxed - ((5 * rec.amount_untaxed) / 100)

                elif rec.amount_untaxed >= 1000 and rec.amount_untaxed < 1500:
                    rec.total_new = rec.amount_untaxed - ((7 * rec.amount_untaxed) / 100)

                elif rec.amount_untaxed >= 1500:
                    rec.total_new = rec.amount_untaxed - ((10 * rec.amount_untaxed) / 100)

                elif rec.amount_untaxed < 500:
                    rec.total_new = rec.amount_untaxed

    @api.multi
    @api.onchange('partner_id','order_line')
    def _compute_shipping_amount(self):
        for rec in self:
            # Compute delivery cost
            delivery_cost = 0
            for line in rec.order_line:
                if line.product_id.type == 'service':
                    delivery_cost = delivery_cost + line.price_subtotal
            if rec.date_order_compute and rec.pricelist_id.name == 'Preismodell 2021':
                if rec.amount_untaxed >= 250 and rec.partner_id.country_id.name in ['Germany','Deutschland','Allemagne']:
                    rec.shipping_amount_new = 0
                else:
                    rec.shipping_amount_new = delivery_cost
            else:
                rec.shipping_amount_new = delivery_cost

    @api.multi
    @api.onchange('partner_id', 'order_line')
    def _compute_spl_discount(self):
        for rec in self:
            if rec.date_order_compute and rec.pricelist_id.name == 'Preismodell 2021' and rec.super_spl_discount:
                if rec.partner_id.is_retailer and rec.amount_untaxed >= 500 and rec.amount_untaxed < 1000:
                    rec.spl_discount = (5 * (rec.amount_untaxed)) / 100
                    # rec.spl_discount = (10*rec.untaxed_amount_new)/100
                elif rec.partner_id.is_retailer and rec.amount_untaxed >= 1000 and rec.amount_untaxed < 1500:
                    rec.spl_discount = (3 * (rec.amount_untaxed)) / 100
                elif rec.partner_id.is_retailer and rec.amount_untaxed < 500:
                    rec.spl_discount = (10 * (rec.amount_untaxed)) / 100
                else:
                    rec.spl_discount = 0

    @api.multi
    @api.onchange('order_line')
    def _compute_tax_new(self):
        for rec in self:
            if rec.date_order_compute and rec.pricelist_id.name == 'Preismodell 2021':
                for o_line in rec:
                    if o_line.order_line:
                        if o_line.order_line[0].tax_id.name == "16% Corona Tax" or o_line.order_line[0].tax_id.name == "16% abgesenkte MwSt":
                            rec.amount_tax_new = (16 * (rec.amount_untaxed - rec.discount - rec.spl_discount)) / 100
                        elif o_line.order_line[0].tax_id.name == "19% Umsatzsteuer" or o_line.order_line[0].tax_id.name == "19 % Umsatzsteuer EU Lieferung" or o_line.order_line[0].tax_id.name == "MwSt._(19.0 % included T)_Relaxound GmbH":
                            rec.amount_tax_new = (19 * (rec.amount_untaxed - rec.discount - rec.spl_discount)) / 100
                        elif not o_line.order_line[0].tax_id or o_line.order_line[0].tax_id.name == "Steuerfreie innergem. Lieferung (§4 Abs. 1b UStG)" or o_line.order_line[0].tax_id.name == "Steuerfreie Ausfuhr (§4 Nr. 1a UStG)":
                            rec.amount_tax_new = (0 * (rec.amount_untaxed - rec.discount - rec.spl_discount)) / 100

    @api.multi
    @api.onchange('partner_id','order_line')
    def _compute_total_untaxed(self):
        for rec in self:
            if rec.date_order_compute and rec.pricelist_id.name == 'Preismodell 2021':
                if rec.amount_untaxed >= 500 and rec.amount_untaxed < 1000:
                    rec.untaxed_total= rec.amount_untaxed - rec.discount - rec.spl_discount

                elif rec.amount_untaxed >= 1000 and rec.amount_untaxed < 1500:
                    rec.untaxed_total = rec.amount_untaxed - rec.discount - rec.spl_discount

                elif rec.amount_untaxed >=1500:
                    rec.untaxed_total = rec.amount_untaxed - rec.discount - rec.spl_discount

                elif rec.amount_untaxed < 500:
                    rec.untaxed_total = rec.amount_untaxed - rec.discount - rec.spl_discount


    @api.multi
    @api.onchange('partner_id','order_line')
    def _compute_untaxed_amount(self):
        for rec in self:
            if rec.date_order_compute and rec.pricelist_id.name == 'Preismodell 2021':
                if rec.amount_untaxed >= 500 and rec.amount_untaxed < 1000:
                    rec.untaxed_amount_new = rec.total_new+rec.shipping_amount_new+rec.amount_tax_new

                elif rec.amount_untaxed >= 1000 and rec.amount_untaxed < 1500:
                    rec.untaxed_amount_new = rec.total_new+rec.shipping_amount_new+rec.amount_tax_new

                elif rec.amount_untaxed >=1500:
                    rec.untaxed_amount_new = rec.total_new+rec.shipping_amount_new+rec.amount_tax_new

                elif rec.amount_untaxed < 500:
                    rec.untaxed_amount_new = rec.total_new+rec.shipping_amount_new+rec.amount_tax_new

    @api.multi
    @api.onchange('partner_id','order_line')
    def _compute_total(self):
        for rec in self:
            if rec.date_order_compute and rec.pricelist_id.name == 'Preismodell 2021':
                rec.amount_total_new = rec.untaxed_amount_new - rec.spl_discount - rec.shipping_amount_new
            else:
                rec.amount_total_new = rec.untaxed_amount_new - rec.spl_discount - rec.shipping_amount_new


    @api.multi
    @api.onchange('partner_id','order_line','amount_total_new')
    def _compute_discount_2(self):
        for rec in self:
            if rec.date_order_compute and rec.pricelist_id.name == 'Preismodell 2021':
                rec.discount_2 = rec.amount_total_new - ((2*rec.amount_total_new)/100)

    @api.multi
    @api.onchange('partner_id','order_line','amount_total')
    def _set_description(self):
        for rec in self:
            if rec.date_order_compute and rec.partner_id.is_retailer and rec.partner_id.lang in ['de_CH','de_DE'] and rec.partner_id.country_id.name != 'France' and rec.pricelist_id.name == 'Preismodell 2021' and rec.date_order:
                rec.set_desription ='2% Skonto bei SEPA-Einzug oder Zahlungseingang bis ' + str((rec.date_order + timedelta(days=14)).strftime('%d.%m.%Y'))
            elif rec.date_order_compute and rec.partner_id.is_retailer and rec.partner_id.lang in ['de_CH','de_DE'] and rec.partner_id.country_id.name != 'France' and rec.pricelist_id.name == 'Preismodell 2021' and not rec.date_order:
                rec.set_desription ='2% Skonto bei SEPA-Einzug oder Zahlungseingang bis ' + str((date.today() + timedelta(days=14)).strftime('%d.%m.%Y'))

            elif rec.date_order_compute and rec.partner_id.is_retailer and rec.partner_id.lang not in ['de_CH','de_DE'] and rec.partner_id.country_id.name != 'France' and rec.pricelist_id.name == 'Preismodell 2021' and rec.date_order:
                rec.set_desription ='2% discount - payment by ' + str((rec.date_order + timedelta(days=14)).strftime('%d.%m.%Y'))
            elif rec.date_order_compute and rec.partner_id.is_retailer and rec.partner_id.lang not in ['de_CH','de_DE'] and rec.partner_id.country_id.name != 'France' and rec.pricelist_id.name == 'Preismodell 2021' and not rec.date_order:
                rec.set_desription ='2% discount - payment by ' + str((date.today() + timedelta(days=14)).strftime('%d.%m.%Y'))

            elif rec.date_order_compute and rec.partner_id.is_retailer and rec.partner_id.country_id.name == 'France' and rec.pricelist_id.name == 'Preismodell 2021' and rec.date_order:
                rec.set_desription1 ='ESCOMPTE DE 2 %\nVous pouvez payer dans un délai de 30 jours nets par prélèvement bancaire/ SEPA.\nEn cas de paiement anticipé, vous bénéficiez d’une réduction supplémentaire de\n 2 % etla valeur de votre commande est réduite à '
            elif rec.date_order_compute and rec.partner_id.is_retailer and rec.partner_id.country_id.name == 'France' and rec.pricelist_id.name == 'Preismodell 2021' and not rec.date_order :
                rec.set_desription1 ='ESCOMPTE DE 2 %\nVous pouvez payer dans un délai de 30 jours nets par prélèvement bancaire/ SEPA.\nEn cas de paiement anticipé, vous bénéficiez d’une réduction supplémentaire de\n 2 % etla valeur de votre commande est réduite à '
            else:
                pass



    @api.depends('order_date')
    def _get_date_order(self):
        for rec in self:
            if rec.date_order:
                order_date = (rec.date_order + timedelta(days=14)).strftime('%d.%m.%Y')
                return order_date
            else:
                order_date = (date.today() + timedelta(days=14)).strftime('%d.%m.%Y')
                return order_date

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            if order.pricelist_id.name == 'Preismodell 2021':
                amount_untaxed = amount_tax = 0.0
                for line in order.order_line:
                    amount_untaxed += line.price_subtotal

                if amount_untaxed >= 500 and amount_untaxed < 1000:
                    discount = (5 * (amount_untaxed)) / 100

                elif amount_untaxed >= 1000 and amount_untaxed < 1500:
                    discount = (7 * (amount_untaxed)) / 100

                elif amount_untaxed >= 1500:
                    discount = (10 * (amount_untaxed)) / 100

                elif amount_untaxed < 500:
                    discount = 0

                if order.super_spl_discount:
                    if order.partner_id.is_retailer and amount_untaxed >= 500 and amount_untaxed < 1000:
                        spl_discount = (5 * (amount_untaxed)) / 100
                    elif order.partner_id.is_retailer and amount_untaxed >= 1000 and amount_untaxed < 1500:
                        spl_discount = (3 * (amount_untaxed)) / 100
                    elif order.partner_id.is_retailer and amount_untaxed < 500:
                        spl_discount = (10 * (amount_untaxed)) / 100
                    else:
                        spl_discount = 0
                else:
                    spl_discount = 0

                for line in order.order_line:
                    if line.tax_id.name == "16% Corona Tax" or line.tax_id.name == "16% abgesenkte MwSt" or line.tax_id.name == "MwSt._(16.0 % included T)_Relaxound GmbH":
                        amount_tax = (16 * (amount_untaxed - discount - spl_discount)) / 100
                    elif line.tax_id.name == "19% Umsatzsteuer" or line.tax_id.name == "19 % Umsatzsteuer EU Lieferung" or line.tax_id.name == "MwSt._(19.0 % included T)_Relaxound GmbH":
                        amount_tax = (19 * (amount_untaxed - discount - spl_discount)) / 100
                    elif not line.tax_id or line.tax_id.name == "Steuerfreie innergem. Lieferung (§4 Abs. 1b UStG)" or line.tax_id.name == "Steuerfreie Ausfuhr (§4 Nr. 1a UStG)":
                        amount_tax = (0 * (amount_untaxed - discount - spl_discount)) / 100

                order.update({
                    'amount_untaxed': amount_untaxed,
                    'amount_tax': amount_tax,
                    'amount_total': (amount_untaxed - discount - spl_discount) + amount_tax,
                })
            else:
                amount_untaxed = amount_tax = 0.0
                for line in order.order_line:
                    amount_untaxed += line.price_subtotal
                    amount_tax += line.price_tax
                order.update({
                    'amount_untaxed': amount_untaxed,
                    'amount_tax': amount_tax,
                    'amount_total': amount_untaxed + amount_tax,
                })
