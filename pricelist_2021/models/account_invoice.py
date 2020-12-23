from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from dateutil.relativedelta import relativedelta
from datetime import datetime , timedelta,date


class CustomInvoiceOrderform(models.Model):
    _inherit = "account.invoice"

    discount = fields.Float('Discount',compute='_compute_discount')
    total_new = fields.Float('Total',compute='_compute_total_new')
    shipping_amount_new = fields.Float('Shipping',compute='_compute_shipping_amount')
    spl_discount = fields.Float('Special 10% Discount',compute='_compute_spl_discount')
    untaxed_amount_new = fields.Float('Total',compute='_compute_untaxed_amount')
    amount_total_new = fields.Float('Total',compute='_compute_total')
    discount_2 = fields.Float(compute='_compute_discount_2')
    set_desription = fields.Char('Note',compute='_set_description')


    hide = fields.Boolean(string='Hide', compute="_compute_hide")


    def _compute_hide(self):
        # simple logic, but you can do much more here
        for rec in self:
            if rec.origin1.pricelist_id.name == 'New Pricing Model for 2021' or rec.date_invoice >= datetime.date(2021,1,1):
                rec.hide = True
            else:
                rec.hide = False



    @api.multi
    def _compute_discount(self):
        for rec in self:
            if rec.origin1.pricelist_id.name == 'New Pricing Model for 2021' or rec.date_invoice >= datetime.date(2021,1,1):
                if rec.amount_untaxed >= 500 and rec.amount_untaxed < 1000:
                    rec.discount = (5 * (rec.amount_untaxed)) / 100

                elif rec.amount_untaxed >= 1000 and rec.amount_untaxed < 1500:
                    rec.discount = (7 * (rec.amount_untaxed)) / 100

                elif rec.amount_untaxed >= 1500:
                    rec.discount = (10 * (rec.amount_untaxed)) / 100

                elif rec.amount_untaxed < 500:
                    rec.discount = 0

    @api.multi
    def _compute_total_new(self):
        for rec in self:
            if rec.origin1.pricelist_id.name == 'New Pricing Model for 2021' or rec.date_invoice >= datetime.date(2021,1,1):
                if rec.amount_untaxed >= 500 and rec.amount_untaxed < 1000:
                    rec.total_new = rec.amount_untaxed - ((5 * rec.amount_untaxed) / 100)

                elif rec.amount_untaxed >= 1000 and rec.amount_untaxed < 1500:
                    rec.total_new = rec.amount_untaxed - ((7 * rec.amount_untaxed) / 100)

                elif rec.amount_untaxed >= 1500:
                    rec.total_new = rec.amount_untaxed - ((10 * rec.amount_untaxed) / 100)

                elif rec.amount_untaxed < 500:
                    rec.total_new = rec.amount_untaxed

    @api.multi
    def _compute_shipping_amount(self):
        for rec in self:
            if rec.origin1.pricelist_id.name == 'New Pricing Model for 2021' or rec.date_invoice >= datetime.date(2021,1,1):
                # Compute delivery cost
                delivery_cost = 0
                for line in rec.invoice_line_ids:
                    if line.product_id.type == 'service':
                        delivery_cost = delivery_cost + line.price_subtotal
                if rec.amount_untaxed >= 200:
                    rec.shipping_amount_new = 0
                else:
                    rec.shipping_amount_new = delivery_cost


    @api.multi
    def _compute_untaxed_amount(self):
        for rec in self:
            if rec.origin1.pricelist_id.name == 'New Pricing Model for 2021' or rec.date_invoice >= datetime.date(2021,1,1):
                if rec.amount_untaxed >= 500 and rec.amount_untaxed < 1000:
                    rec.untaxed_amount_new = rec.total_new+rec.shipping_amount_new+rec.amount_tax

                elif rec.amount_untaxed >= 1000 and rec.amount_untaxed < 1500:
                    rec.untaxed_amount_new = rec.total_new+rec.shipping_amount_new+rec.amount_tax

                elif rec.amount_untaxed >=1500:
                    rec.untaxed_amount_new = rec.total_new+rec.shipping_amount_new+rec.amount_tax

                elif rec.amount_untaxed < 500:
                    rec.untaxed_amount_new = rec.total_new+rec.shipping_amount_new+rec.amount_tax

    @api.multi
    def _compute_spl_discount(self):
        for rec in self:
            if rec.origin1.pricelist_id.name == 'New Pricing Model for 2021'or rec.date_invoice >= datetime.date(2021,1,1):
                if rec.partner_id.is_retailer:
                    rec.spl_discount = (10*rec.untaxed_amount_new)/100
                else:
                    rec.spl_discount = 0

    @api.multi
    def _compute_total(self):
        for rec in self:
            if rec.origin1.pricelist_id.name == 'New Pricing Model for 2021' or rec.date_invoice >= datetime.date(2021,1,1):
                rec.amount_total_new = rec.untaxed_amount_new - rec.spl_discount
            else:
                rec.amount_total_new = rec.untaxed_amount_new - rec.spl_discount


    @api.multi
    def _compute_discount_2(self):
        for rec in self:
            if rec.origin1.pricelist_id.name == 'New Pricing Model for 2021' or rec.date_invoice >= datetime.date(2021,1,1):
                rec.discount_2 = rec.amount_total_new - 2*rec.amount_total_new/100

    @api.multi
    def _set_description(self):
        for rec in self:
            if (rec.origin1.pricelist_id.name == 'New Pricing Model for 2021' and rec.date_invoice) or (rec.date_invoice >= datetime.date(2021,1,1)):
                rec.set_desription ='2% discount - payment by ' + str((rec.date_invoice + timedelta(days=14)).strftime('%d-%m-%Y')) + " " + str(rec.discount_2)
            elif (rec.origin1.pricelist_id.name == 'New Pricing Model for 2021' and not rec.date_invoice) or rec.date_invoice >= datetime.date(2021,1,1):
                rec.set_desription ='2% discount - payment by ' + str((date.today() + timedelta(days=14)).strftime('%d-%m-%Y')) + " " + str(rec.discount_2)
            else:
                rec.set_desription ='2% discount - payment by ' + str((date.today() + timedelta(days=14)).strftime('%d-%m-%Y')) + " " + str(rec.discount_2)
