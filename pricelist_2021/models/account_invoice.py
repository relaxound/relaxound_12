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
    untaxed_total = fields.Float('Amount After Discount',compute='_compute_total_untaxed')
    amount_total_new = fields.Float('Total',compute='_compute_total')
    amount_tax_new = fields.Float('Taxes',compute='_compute_tax_new')
    discount_2 = fields.Float(compute='_compute_discount_2')
    set_desription = fields.Char('Note',compute='_set_description')
    set_desription1 = fields.Text('Note',compute='_set_description')

    today_date = fields.Date('Today Date',compute='_get_today_date')
    # super_spl_discount = fields.Boolean('Super Special Discount')

    hide = fields.Boolean(string='Hide', compute="_compute_hide")
    hide_spl_discount = fields.Boolean(string='Hide discount' ,compute='_compute_hide_discount')
    hide_2_discount = fields.Boolean(string='Hide 2% discount' ,compute='_compute_hide_2_discount')
    hide_france_note = fields.Boolean(string='Hide france desc', compute='_compute_hide_france_desc')

    date_invoice_compute = fields.Boolean(string='Date of the order',
                                  compute='date_invoice_compute')

    @api.depends('partner_id.property_product_pricelist')
    def date_invoice_compute(self):
        intial_date = date(2021, 1, 1)
        for rec in self:
            if (rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (
                    rec.partner_id.property_product_pricelist.name == 'Preismodell 2021') and (intial_date >= date.today() or rec.date_invoice >= date.today()):
                rec.date_invoice_compute = True
            else:
                rec.date_invoice_compute = False




    @api.depends('partner_id.property_product_pricelist')
    def _compute_hide_france_desc(self):
        # simple logic, but you can do much more here
        for rec in self:
            # datetime.strptime('1/1/2021', "%m/%d/%y")
            if rec.partner_id.is_retailer and rec.partner_id.country_id.name == 'France' and ((rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (rec.partner_id.property_product_pricelist.name == 'Preismodell 2021')):
                rec.hide_france_note = True
            else:
                rec.hide_france_note = False


    def _get_today_date(self):
        for rec in self:
            rec.today_date = date.today().strftime('%Y-%m-%d')

    @api.depends('partner_id.property_product_pricelist')
    def _compute_hide_2_discount(self):
        # simple logic, but you can do much more here
        for rec in self:
            # datetime.strptime('1/1/2021', "%m/%d/%y")
            if rec.partner_id.is_retailer and rec.partner_id.country_id.name != 'France' and ((rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (rec.partner_id.property_product_pricelist.name == 'Preismodell 2021')):
                rec.hide_2_discount = True
            else:
                rec.hide_2_discount = False


    @api.onchange('origin1.super_spl_discount','partner_id.property_product_pricelist')
    def _compute_hide_discount(self):
        for rec in self:
            if rec.partner_id.is_retailer and rec.origin1.super_spl_discount and ((rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or rec.partner_id.property_product_pricelist.name == 'Preismodell 2021'):
                rec.hide_spl_discount = True
            else:
                rec.hide_spl_discount = False


    @api.depends('partner_id.property_product_pricelist')
    def _compute_hide(self):
        # simple logic, but you can do much more here
        for rec in self:
            # datetime.strptime('1/1/2021', "%m/%d/%y")
            if (rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (rec.partner_id.property_product_pricelist.name == 'Preismodell 2021'):
                rec.hide = True
            else:
                rec.hide = False

    @api.multi
    @api.onchange('partner_id','invoice_line_ids')
    def _compute_discount(self):
        for rec in self:
            if (rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (rec.partner_id.property_product_pricelist.name == 'Preismodell 2021') :
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
            if (rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (rec.partner_id.property_product_pricelist.name == 'Preismodell 2021'):
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
            if (rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (rec.partner_id.property_product_pricelist.name == 'Preismodell 2021'):
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
    @api.onchange('invoice_line_ids')
    def _compute_tax_new(self):
        for rec in self:
            if (rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (rec.partner_id.property_product_pricelist.name == 'Preismodell 2021'):
                for o_line in rec:
                    if o_line.invoice_line_ids:
                        if o_line.invoice_line_ids[0].invoice_line_tax_ids.name == "16% Corona Tax" or o_line.invoice_line_ids[0].invoice_line_tax_ids.name == "16% abgesenkte MwSt":
                            rec.amount_tax_new = (16 * (rec.amount_untaxed - rec.discount - rec.spl_discount)) / 100

                        elif o_line.invoice_line_ids[0].invoice_line_tax_ids.name == "19% Umsatzsteuer" or o_line.invoice_line_ids[0].invoice_line_tax_ids.name == "19 % Umsatzsteuer EU Lieferung" or o_line.invoice_line_ids[0].invoice_line_tax_ids.name == "MwSt._(19.0 % included T)_Relaxound GmbH":
                            rec.amount_tax_new = (19 * (rec.amount_untaxed - rec.discount - rec.spl_discount)) / 100

                        elif o_line.invoice_line_ids[0].invoice_line_tax_ids.name == "Steuerfreie innergem. Lieferung (§4 Abs. 1b UStG)" or o_line.invoice_line_ids[0].invoice_line_tax_ids.name == "Steuerfreie Ausfuhr (§4 Nr. 1a UStG)":
                            rec.amount_tax_new = (0 * (rec.amount_untaxed - rec.discount - rec.spl_discount)) / 100


    @api.multi
    @api.onchange('partner_id', 'invoice_line_ids')
    def _compute_total_untaxed(self):
        for rec in self:
            if (rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (rec.partner_id.property_product_pricelist.name == 'Preismodell 2021'):
                if rec.amount_untaxed >= 500 and rec.amount_untaxed < 1000:
                    rec.untaxed_total = rec.amount_untaxed - rec.discount - rec.spl_discount

                elif rec.amount_untaxed >= 1000 and rec.amount_untaxed < 1500:
                    rec.untaxed_total = rec.amount_untaxed - rec.discount - rec.spl_discount

                elif rec.amount_untaxed >= 1500:
                    rec.untaxed_total = rec.amount_untaxed - rec.discount - rec.spl_discount

                elif rec.amount_untaxed < 500:
                    rec.untaxed_total = rec.amount_untaxed - rec.discount - rec.spl_discount

    @api.multi
    @api.onchange('partner_id','invoice_line_ids')
    def _compute_untaxed_amount(self):
        for rec in self:
            if (rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (rec.partner_id.property_product_pricelist.name == 'Preismodell 2021'):
                if rec.amount_untaxed >= 500 and rec.amount_untaxed < 1000:
                    rec.untaxed_amount_new = rec.total_new+rec.shipping_amount_new+rec.amount_tax_new

                elif rec.amount_untaxed >= 1000 and rec.amount_untaxed < 1500:
                    rec.untaxed_amount_new = rec.total_new+rec.shipping_amount_new+rec.amount_tax_new

                elif rec.amount_untaxed >=1500:
                    rec.untaxed_amount_new = rec.total_new+rec.shipping_amount_new+rec.amount_tax_new

                elif rec.amount_untaxed < 500:
                    rec.untaxed_amount_new = rec.total_new+rec.shipping_amount_new+rec.amount_tax_new

    @api.multi
    @api.onchange('partner_id','invoice_line_ids')
    def _compute_spl_discount(self):
        for rec in self:
            if (rec.origin1.super_spl_discount) and ((rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (rec.partner_id.property_product_pricelist.name == 'Preismodell 2021')):
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
            if (rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (rec.partner_id.property_product_pricelist.name == 'Preismodell 2021'):
                rec.amount_total_new = rec.untaxed_amount_new - rec.spl_discount - rec.shipping_amount_new
            else:
                rec.amount_total_new = rec.untaxed_amount_new - rec.spl_discount - rec.shipping_amount_new


    @api.multi
    @api.onchange('partner_id','invoice_line_ids','amount_total_new')
    def _compute_discount_2(self):
        for rec in self:
            if (rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (rec.partner_id.property_product_pricelist.name == 'Preismodell 2021'):
                rec.discount_2 = rec.amount_total_new - 2*rec.amount_total_new/100


    @api.multi
    @api.onchange('partner_id','invoice_line_ids','amount_total_new')
    def _set_description(self):
        for rec in self:
            if rec.partner_id.is_retailer and rec.partner_id.country_id.name != 'France' and ((rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (rec.partner_id.property_product_pricelist.name == 'Preismodell 2021')):
                if rec.date_invoice and rec.partner_id.lang in ['de_CH','de_DE'] and (rec.origin1.pricelist_id.name == 'Preismodell 2021' or rec.partner_id.property_product_pricelist.name == 'Preismodell 2021'):
                    rec.set_desription ='2% Skonto bei Zahlungseingang bis ' + str((rec.date_invoice + timedelta(days=14)).strftime('%d.%m.%Y'))
                elif rec.partner_id.is_retailer and rec.partner_id.lang in ['de_CH','de_DE'] and (rec.origin1.pricelist_id.name == 'Preismodell 2021' or rec.partner_id.property_product_pricelist.name == 'Preismodell 2021') and not rec.date_invoice and date.today() >= date(2021,1,1) :
                    rec.set_desription ='2% Skonto bei Zahlungseingang bis ' + str((date.today() + timedelta(days=14)).strftime('%d.%m.%Y'))

                elif rec.date_invoice and rec.partner_id.lang not in ['de_CH','de_DE'] and (rec.origin1.pricelist_id.name == 'Preismodell 2021' or rec.partner_id.property_product_pricelist.name == 'Preismodell 2021'):
                    rec.set_desription ='2% discount - payment by ' + str((rec.date_invoice + timedelta(days=14)).strftime('%d.%m.%Y'))
                elif rec.partner_id.is_retailer and rec.partner_id.lang not in ['de_CH','de_DE'] and (rec.origin1.pricelist_id.name == 'Preismodell 2021' or rec.partner_id.property_product_pricelist.name == 'Preismodell 2021') and not rec.date_invoice and date.today() >= date(2021,1,1) :
                    rec.set_desription ='2% discount - payment by ' + str((date.today() + timedelta(days=14)).strftime('%d.%m.%Y'))
                elif (rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name != 'Preismodell 2021') or (rec.partner_id.property_product_pricelist.name != 'Preismodell 2021'):
                    pass

            elif rec.partner_id.is_retailer and rec.partner_id.country_id.name == 'France' and ((rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (rec.partner_id.property_product_pricelist.name == 'Preismodell 2021')):
                if rec.date_invoice and (rec.origin1.pricelist_id.name == 'Preismodell 2021' or rec.partner_id.property_product_pricelist.name == 'Preismodell 2021'):
                    rec.set_desription1 = 'ESCOMPTE DE 2 %\nVous pouvez payer dans un délai de 30 jours nets par prélèvement bancaire/SEPA.\n En cas de paiement anticipé, vous bénéficiez d’une réduction supplémentaire de\n 2 % etla valeur de votre commende est réduit à '
                elif rec.partner_id.is_retailer and (rec.origin1.pricelist_id.name == 'Preismodell 2021' or rec.partner_id.property_product_pricelist.name == 'Preismodell 2021') and not rec.date_invoice and date.today() >= date(2021, 1, 1):
                    rec.set_desription1 = 'ESCOMPTE DE 2 %\nVous pouvez payer dans un délai de 30 jours nets par prélèvement bancaire/SEPA.\n En cas de paiement anticipé, vous bénéficiez d’une réduction supplémentaire de\n 2 % etla valeur de votre commende est réduit à '
                elif (rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name != 'Preismodell 2021') or (rec.partner_id.property_product_pricelist.name != 'Preismodell 2021'):
                    pass
            else:
                pass


    @api.depends('date_invoice')
    def _get_date_invoice(self):
        for rec in self:
            if rec.date_invoice:
                date_invoice = (rec.date_invoice + timedelta(days=14)).strftime('%d.%m.%Y')
                return date_invoice
            else:
                date_invoice = (date.today() + timedelta(days=14)).strftime('%d.%m.%Y')
                return date_invoice


    @api.one
    @api.depends('tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        if (self.origin1.pricelist_id.name and self.origin1.pricelist_id.name == 'Preismodell 2021') or (
                self.partner_id.property_product_pricelist.name == 'Preismodell 2021'):
            self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
            # self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
            # self.amount_total = self.amount_untaxed + self.amount_tax

            if self.amount_untaxed >= 500 and self.amount_untaxed < 1000:
                discount = (5 * (self.amount_untaxed)) / 100

            elif self.amount_untaxed >= 1000 and self.amount_untaxed < 1500:
                discount = (7 * (self.amount_untaxed)) / 100

            elif self.amount_untaxed >= 1500:
                discount = (10 * (self.amount_untaxed)) / 100

            elif self.amount_untaxed < 500:
                discount = 0

            if self.origin1.super_spl_discount:
                if self.partner_id.is_retailer and self.amount_untaxed >= 500 and self.amount_untaxed < 1000:
                    spl_discount = (5 * (self.amount_untaxed)) / 100
                elif self.partner_id.is_retailer and self.amount_untaxed >= 1000 and self.amount_untaxed < 1500:
                    spl_discount = (3 * (self.amount_untaxed)) / 100
                elif self.partner_id.is_retailer and self.amount_untaxed < 500:
                    spl_discount = (10 * (self.amount_untaxed)) / 100
                else:
                    spl_discount = 0
            else:
                spl_discount = 0

            for line in self.invoice_line_ids:
                if line.invoice_line_tax_ids.name == "16% Corona Tax" or \
                        line.invoice_line_tax_ids.name == "16% abgesenkte MwSt":
                    self.amount_tax = (16 * (self.amount_untaxed - discount - spl_discount)) / 100

                elif line.invoice_line_tax_ids.name == "19% Umsatzsteuer" or \
                        line.invoice_line_tax_ids.name == "19 % Umsatzsteuer EU Lieferung" or \
                        line.invoice_line_tax_ids.name == "MwSt._(19.0 % included T)_Relaxound GmbH":
                    self.amount_tax = (19 * (self.amount_untaxed - discount - spl_discount)) / 100

                elif line.invoice_line_tax_ids.name == "Steuerfreie innergem. Lieferung (§4 Abs. 1b UStG)" or \
                        line.invoice_line_tax_ids.name == "Steuerfreie Ausfuhr (§4 Nr. 1a UStG)":
                    self.amount_tax = (0 * (self.amount_untaxed - discount - spl_discount)) / 100

                self.amount_total = self.amount_untaxed + self.amount_tax - discount - spl_discount
            amount_total_company_signed = self.amount_total
            amount_untaxed_signed = self.amount_untaxed
            if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
                currency_id = self.currency_id
                amount_total_company_signed = currency_id._convert(self.amount_total, self.company_id.currency_id,
                                                                   self.company_id,
                                                                   self.date_invoice or fields.Date.today())
                amount_untaxed_signed = currency_id._convert(self.amount_untaxed, self.company_id.currency_id,
                                                             self.company_id, self.date_invoice or fields.Date.today())
            sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
            self.amount_total_company_signed = amount_total_company_signed * sign
            self.amount_total_signed = self.amount_total * sign
            self.amount_untaxed_signed = amount_untaxed_signed * sign
        else:
            self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
            self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
            self.amount_total = self.amount_untaxed + self.amount_tax

            amount_total_company_signed = self.amount_total
            amount_untaxed_signed = self.amount_untaxed
            if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
                currency_id = self.currency_id
                amount_total_company_signed = currency_id._convert(self.amount_total, self.company_id.currency_id,
                                                                   self.company_id,
                                                                   self.date_invoice or fields.Date.today())
                amount_untaxed_signed = currency_id._convert(self.amount_untaxed, self.company_id.currency_id,
                                                             self.company_id, self.date_invoice or fields.Date.today())
            sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
            self.amount_total_company_signed = amount_total_company_signed * sign
            self.amount_total_signed = self.amount_total * sign
            self.amount_untaxed_signed = amount_untaxed_signed * sign
