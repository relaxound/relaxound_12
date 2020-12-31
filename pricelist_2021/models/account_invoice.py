from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from dateutil.relativedelta import relativedelta
from datetime import datetime , timedelta,date


class CustomInvoiceOrderform(models.Model):
    _inherit = "account.invoice"

    discount = fields.Float('Discount',compute='_compute_discount')
    total_new = fields.Float('Total',compute='_compute_total_new')
    shipping_amount_new = fields.Float('Shipping',compute='_compute_shipping_amount')
    spl_discount = fields.Float('Special Discount',compute='_compute_spl_discount')
    untaxed_amount_new = fields.Float('Total',compute='_compute_untaxed_amount')
    amount_total_new = fields.Float('Total',compute='_compute_total')
    discount_2 = fields.Float(compute='_compute_discount_2')
    set_desription = fields.Char('Note',compute='_set_description')
    today_date = fields.Date('Today Date',compute='_get_today_date')
    # super_spl_discount = fields.Boolean('Super Special Discount')

    hide = fields.Boolean(string='Hide', compute="_compute_hide")
    hide_spl_discount = fields.Boolean(string='Hide discount' ,compute='_compute_hide_discount')

    def _compute_hide_discount(self):
        for rec in self:
            if rec.partner_id.is_retailer and rec.origin1.super_spl_discount and (rec.origin1.pricelist_id.name and (rec.origin1.pricelist_id.name == 'Preismodell 2021') or ((rec.payment_term_id.name == '30 days after receipt of invoice') and ((rec.date_invoice and rec.date_invoice >= date(2021,1,1)) or (not rec.date_invoice and date.today() >= date(2021,1,1))))):
                rec.hide_spl_discount = True
            else:
                rec.hide_spl_discount = False

    def _get_today_date(self):
        for rec in self:
            rec.today_date = date.today().strftime('%Y-%m-%d')

    def _compute_hide(self):
        # simple logic, but you can do much more here
        for rec in self:
            # datetime.strptime('1/1/2021', "%m/%d/%y")
            if (rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or ((rec.payment_term_id.name == '30 days after receipt of invoice') and ((rec.date_invoice and rec.date_invoice >= date(2021,1,1)) or (not rec.date_invoice and date.today() >= date(2021,1,1)))):
                rec.hide = True
            else:
                rec.hide = False

    @api.multi
    @api.onchange('partner_id','invoice_line_ids')
    def _compute_discount(self):
        for rec in self:
            if (rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or ((rec.payment_term_id.name == '30 days after receipt of invoice') and ((rec.date_invoice and rec.date_invoice >= date(2021,1,1)) or (not rec.date_invoice and date.today() >= date(2021,1,1)))):
                if rec.amount_untaxed >= 500 and rec.amount_untaxed < 1000:
                    rec.discount = (5 * (rec.amount_untaxed)) / 100

                elif rec.amount_untaxed >= 1000 and rec.amount_untaxed < 1500:
                    rec.discount = (7 * (rec.amount_untaxed)) / 100

                elif rec.amount_untaxed >= 1500:
                    rec.discount = (10 * (rec.amount_untaxed)) / 100

                elif rec.amount_untaxed < 500:
                    rec.discount = 0
            else:
                pass

    @api.multi
    @api.onchange('partner_id','invoice_line_ids')
    def _compute_total_new(self):
        for rec in self:
            if (rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or ((rec.payment_term_id.name == '30 days after receipt of invoice') and ((rec.date_invoice and rec.date_invoice >= date(2021,1,1)) or (not rec.date_invoice and date.today() >= date(2021,1,1)))):
                if rec.amount_untaxed >= 500 and rec.amount_untaxed < 1000:
                    rec.total_new = rec.amount_untaxed - ((5 * rec.amount_untaxed) / 100)

                elif rec.amount_untaxed >= 1000 and rec.amount_untaxed < 1500:
                    rec.total_new = rec.amount_untaxed - ((7 * rec.amount_untaxed) / 100)

                elif rec.amount_untaxed >= 1500:
                    rec.total_new = rec.amount_untaxed - ((10 * rec.amount_untaxed) / 100)

                elif rec.amount_untaxed < 500:
                    rec.total_new = rec.amount_untaxed

    @api.multi
    @api.onchange('partner_id','invoice_line_ids')
    def _compute_shipping_amount(self):
        for rec in self:
            if (rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or ((rec.payment_term_id.name == '30 days after receipt of invoice') and ((rec.date_invoice and rec.date_invoice >= date(2021,1,1)) or (not rec.date_invoice and date.today() >= date(2021,1,1)))):
                # Compute delivery cost
                delivery_cost = 0
                for line in rec.invoice_line_ids:
                    if line.product_id.type == 'service':
                        delivery_cost = delivery_cost + line.price_subtotal
                if rec.amount_untaxed >= 250 and rec.partner_id.country_id.name in ['Germany','Deutschland','Allemagne']:
                    rec.shipping_amount_new = 0
                else:
                    rec.shipping_amount_new = delivery_cost


    @api.multi
    @api.onchange('partner_id','invoice_line_ids')
    def _compute_untaxed_amount(self):
        for rec in self:
            if (rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or ((rec.payment_term_id.name == '30 days after receipt of invoice') and ((rec.date_invoice and rec.date_invoice >= date(2021,1,1)) or (not rec.date_invoice and date.today() >= date(2021,1,1)))):
                if rec.amount_untaxed >= 500 and rec.amount_untaxed < 1000:
                    rec.untaxed_amount_new = rec.total_new+rec.shipping_amount_new+rec.amount_tax

                elif rec.amount_untaxed >= 1000 and rec.amount_untaxed < 1500:
                    rec.untaxed_amount_new = rec.total_new+rec.shipping_amount_new+rec.amount_tax

                elif rec.amount_untaxed >=1500:
                    rec.untaxed_amount_new = rec.total_new+rec.shipping_amount_new+rec.amount_tax

                elif rec.amount_untaxed < 500:
                    rec.untaxed_amount_new = rec.total_new+rec.shipping_amount_new+rec.amount_tax

    @api.multi
    @api.onchange('partner_id','invoice_line_ids')
    def _compute_spl_discount(self):
        for rec in self:
            if (rec.origin1.super_spl_discount) and ((rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or ((rec.payment_term_id.name == '30 days after receipt of invoice') and ((rec.date_invoice and rec.date_invoice >= date(2021,1,1)) or (not rec.date_invoice and date.today() >= date(2021,1,1))))):
                if rec.partner_id.is_retailer and rec.amount_untaxed >= 500 and rec.amount_untaxed < 1000:
                    rec.spl_discount = (5 * (rec.amount_untaxed)) / 100
                    # rec.spl_discount = (10*rec.untaxed_amount_new)/100
                elif rec.partner_id.is_retailer and rec.amount_untaxed >= 1000 and rec.amount_untaxed < 1500:
                    rec.spl_discount = (3 * (rec.amount_untaxed)) / 100
                elif rec.partner_id.is_retailer and rec.amount_untaxed < 500:
                    rec.spl_discount = (10 * (rec.amount_untaxed)) /100
                else:
                    rec.spl_discount = 0

    @api.multi
    @api.onchange('partner_id','invoice_line_ids')
    def _compute_total(self):
        for rec in self:
            if (rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or ((rec.payment_term_id.name == '30 days after receipt of invoice') and ((rec.date_invoice and rec.date_invoice >= date(2021,1,1)) or (not rec.date_invoice and date.today() >= date(2021,1,1)))):
                rec.amount_total_new = rec.untaxed_amount_new - rec.spl_discount - rec.shipping_amount_new
            else:
                rec.amount_total_new = rec.untaxed_amount_new - rec.spl_discount - rec.shipping_amount_new


    @api.multi
    @api.onchange('partner_id','invoice_line_ids','amount_total_new')
    def _compute_discount_2(self):
        for rec in self:
            if (rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or ((rec.payment_term_id.name == '30 days after receipt of invoice') and ((rec.date_invoice and rec.date_invoice >= date(2021,1,1)) or (not rec.date_invoice and date.today() >= date(2021,1,1)))):
                rec.discount_2 = rec.amount_total_new - 2*rec.amount_total_new/100


    @api.multi
    @api.onchange('partner_id','invoice_line_ids','amount_total_new')
    def _set_description(self):
        for rec in self:
            if rec.payment_term_id.name == '30 days after receipt of invoice':
                if rec.date_invoice and rec.origin1.pricelist_id.name == 'Preismodell 2021':
                    rec.set_desription ='2% discount - payment by ' + str((rec.date_invoice + timedelta(days=14)).strftime('%d-%m-%Y'))
                elif rec.origin1.pricelist_id.name == 'Preismodell 2021' and not rec.date_invoice and date.today() >= date(2021,1,1):
                    rec.set_desription ='2% discount - payment by ' + str((date.today() + timedelta(days=14)).strftime('%d-%m-%Y'))
                else:
                    rec.set_desription ='2% discount - payment by ' + str((date.today() + timedelta(days=14)).strftime('%d-%m-%Y'))
