from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils


class CustomSaleOrder(models.Model):
    _inherit = 'sale.order.line'


    @api.multi
    def _compute_tax_id(self):

        start_date = date(2020,7,1)
        end_date = date(2020,12,31)

        import pdb;
        pdb.set_trace()

        for line in self:
            # ---------------------- base code ---------------------------------
            # fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            # # If company_id is set, always filter taxes by the company
            # taxes = line.product_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
            # line.tax_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_shipping_id) if fpos else taxes
            # ----------------------------------------------------------------------------------------------

            # 1. Scenario 1: Customer having country as Germany and Fiscal Position Contains EU -------->
            # 2. Scenario 2: Customer having country as Germany and  Fiscal Position Contains Other value or null ---------------->
            # 3. Scenario 3: customer is a retailer outside of Germany and within EU it needs a VAT ---------------->
            # 4. Scenario 4: customer is a retailer outside of Germany and within EU it needs a VAT is missing  --------->

            if not line.order_id.partner_id:
                raise ValidationError("Please select the customer name!")


            # if (not line.order_id.order_date and start_date <= date.today() <= end_date) or (line.order_id.order_date and start_date <= line.order_id.order_date <= end_date):
            #     flag = True
            # else:
            #     flag = False
            if line.order_id.partner_id.country_id or line.order_id.partner_id.property_account_position_id.name:
                fiscal_position_name = line.order_id.partner_id.property_account_position_id.name
                # change code ['Germany','Deutschland','Allemagne']#
                if line.order_id.partner_id.country_id.name in ['Germany','Deutschland','Allemagne']:
                    if fiscal_position_name:
                        if 'EU' in fiscal_position_name: # Scenario 1 ---->
                            tax_id = self.env['account.tax'].search(['|',('name', '=', "16% Corona Tax") , ('name', '=', "16% abgesenkte MwSt")],limit=1)
                            if tax_id not in self.tax_id:
                                line.update({'tax_id':tax_id})

                        if 'EU' not in fiscal_position_name: # Scenario 2 ---->
                            tax_id = self.env['account.tax'].search(['|',('name', '=', "16% Corona Tax") , ('name', '=', "16% abgesenkte MwSt")],limit=1)
                            if tax_id not in self.tax_id:
                                line.update({'tax_id':tax_id})
                    else: # Scenario 2 ---->
                        tax_id = self.env['account.tax'].search(['|',('name', '=', "16% Corona Tax") , ('name', '=', "16% abgesenkte MwSt")],limit=1)
                        if tax_id not in self.tax_id:
                            line.update({'tax_id':tax_id})


                elif line.order_id.partner_id.country_id.name in ['Belgium','Bulgaria','Denmark','Estonia','Finnland','France','Greece','United Kingdom','Netherlands','Italy','Ireland','Crotia','Latvia','Lithunia','Luxembourg','Malta','Austria','Poland','Portugal','Romania','Sweden','Slovakia','Slovenia','Spain','Czech Republic','Hungary','Cypress'] or line.order_id.partner_id.country_id.name in ['Belgien','Bulgarien','Dänemark','Estland','Finnland','Frankreich','Griechenland','Vereinigtes Königreich','Niederlande','Italien','Irland','Crotia','Lettland','Lithunien','Luxemburg','Malta','Österreich','Polen','Portugal','Rumänien','Schweden','Slowakei','Slowenien','Spanien','Tschechien Republik ','Ungarn','Zypresse','Lithunia','Tschechische Republik'] or line.order_id.partner_id.country_id.name in ['Belgique','Bulgarie','Danemark','Estonie','Finlande','France','Grèce','Royaume-Uni','Pays-Bas','Italie','Irlande','Crotie',' Lettonie','Lithunie','Luxembourg','Malte','Autriche','Pologne','Portugal','Roumanie','Suède','Slovaquie','Slovénie','Espagne','République tchèque','Hongrie','Cyprès']:
                    if fiscal_position_name:
                        if 'EU' in fiscal_position_name: # Scenario 1 ---->
                            tax_id=self.env['account.tax'].search([('name', '=', "Steuerfreie innergem. Lieferung (§4 Abs. 1b UStG)")],limit=1)
                            if tax_id not in self.tax_id:
                                line.update({'tax_id':tax_id})

                        if 'EU' not in fiscal_position_name: # Scenario 2 ---->
                            tax_id=self.env['account.tax'].search([('name', '=', "Steuerfreie innergem. Lieferung (§4 Abs. 1b UStG)")],limit=1)
                            if tax_id not in self.tax_id:
                                line.update({'tax_id':tax_id})
                    else: # Scenario 2 ---->
                        tax_id=self.env['account.tax'].search([('name', '=', "Steuerfreie innergem. Lieferung (§4 Abs. 1b UStG)")],limit=1)
                        if tax_id not in self.tax_id:
                            line.update({'tax_id':tax_id})

                else:
                    if fiscal_position_name:
                        if 'EU' in fiscal_position_name: # Scenario 1 ---->
                            tax_id=self.env['account.tax'].search([('name', '=', "Steuerfreie Ausfuhr (§4 Nr. 1a UStG)")],limit=1)
                            if tax_id not in self.tax_id:
                                line.update({'tax_id':tax_id})

                        if 'EU' not in fiscal_position_name: # Scenario 2 ---->
                            tax_id=self.env['account.tax'].search([('name', '=', "Steuerfreie Ausfuhr (§4 Nr. 1a UStG)")],limit=1)
                            if tax_id not in self.tax_id:
                                line.update({'tax_id':tax_id})
                    else: # Scenario 2 ---->
                        tax_id=self.env['account.tax'].search([('name', '=', "Steuerfreie Ausfuhr (§4 Nr. 1a UStG)")],limit=1)
                        if tax_id not in self.tax_id:
                            line.update({'tax_id':tax_id})

    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.
        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {}
        product = self.product_id.with_context(force_company=self.company_id.id)
        #change logic of the code
        account = self.tax_id.account_id or self.product_id.taxes_id.account_id or product.categ_id.property_account_income_categ_id
        # account = product.property_account_income_id or product.categ_id.property_account_income_categ_id
        if not account and self.product_id:
            raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))
        fpos = self.order_id.fiscal_position_id or self.order_id.partner_id.property_account_position_id
        if fpos and account:
            account = fpos.map_account(account)
        # Trial
        # account_invoice_line_obj=self.env['account.invoice.tax'].search([('name','=',account_id_name)],limit=1)
        res = {
            'name': self.name,
            'sequence': self.sequence,
            'origin': self.order_id.name,
            'account_id': account.id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'discount': self.discount,
            'uom_id': self.product_uom.id,
            'product_id': self.product_id.id or False,
            'invoice_line_tax_ids': [(6, 0, self.tax_id.ids)],
            'account_analytic_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'display_type': self.display_type,
        }
        return res


class Customtax(models.Model):
    _inherit = 'account.tax'

    @api.model
    def _fix_tax_included_price(self, price, prod_taxes, line_taxes):
        """Subtract tax amount from price when corresponding "price included" taxes do not apply"""
        # FIXME get currency in param?
        incl_tax = prod_taxes.filtered(lambda tax: tax not in prod_taxes and tax.price_include)
        if incl_tax:
            return incl_tax.compute_all(price)['total_excluded']
        return price

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"


    @api.onchange('account_id')
    def _onchange_account_id(self):
        if not self.account_id:
            return
        if not self.product_id:
            fpos = self.invoice_id.fiscal_position_id
            if self.invoice_id.type in ('out_invoice', 'out_refund'):
                default_tax = self.invoice_id.company_id.account_sale_tax_id
            else:
                default_tax = self.invoice_id.company_id.account_purchase_tax_id
            self.invoice_line_tax_ids = fpos.map_tax(self.invoice_line_tax_ids or self.account_id.tax_ids or default_tax, partner=self.partner_id)
        elif not self.price_unit:
            self._set_taxes()



    @api.onchange('product_id')
    def _onchange_product_id(self):
        domain = {}
        if not self.invoice_id:
            return

        part = self.invoice_id.partner_id
        fpos = self.invoice_id.fiscal_position_id or self.invoice_id.partner_id.property_account_position_id
        # fpos = self.invoice_id.fiscal_position_id
        company = self.invoice_id.company_id
        currency = self.invoice_id.currency_id
        type = self.invoice_id.type

        if not part:
            warning = {
                    'title': _('Warning!'),
                    'message': _('You must first select a partner.'),
                }
            return {'warning': warning}

        if not self.product_id:
            if type not in ('in_invoice', 'in_refund'):
                self.price_unit = 0.0
            domain['uom_id'] = []

            for line in self:

                if not line.invoice_id.partner_id:
                    raise ValidationError("Please select the customer name!")

                # if (not line.order_id.order_date and start_date <= date.today() <= end_date) or (line.order_id.order_date and start_date <= line.order_id.order_date <= end_date):
                #     flag = True
                # else:
                #     flag = False
                if line.invoice_id.partner_id.country_id or line.invoice_id.partner_id.property_account_position_id.name:
                    fiscal_position_name = line.invoice_id.partner_id.property_account_position_id.name
                    # change code ['Germany','Deutschland','Allemagne']#
                    if line.invoice_id.partner_id.country_id.name in ['Germany', 'Deutschland', 'Allemagne']:
                        if fiscal_position_name:
                            if 'EU' in fiscal_position_name:  # Scenario 1 ---->
                                invoice_line_tax_ids = self.env['account.tax'].search(
                                    ['|', ('name', '=', "16% Corona Tax"), ('name', '=', "16% abgesenkte MwSt")],limit=1)
                                if invoice_line_tax_ids not in self.invoice_line_tax_ids:
                                    line.update({'invoice_line_tax_ids': invoice_line_tax_ids})

                            if 'EU' not in fiscal_position_name:  # Scenario 2 ---->
                                invoice_line_tax_ids = self.env['account.tax'].search(
                                    ['|', ('name', '=', "16% Corona Tax"), ('name', '=', "16% abgesenkte MwSt")],limit=1)
                                if invoice_line_tax_ids not in self.invoice_line_tax_ids:
                                    line.update({'invoice_line_tax_ids': invoice_line_tax_ids})
                        else:  # Scenario 2 ---->
                            invoice_line_tax_ids = self.env['account.tax'].search(
                                ['|', ('name', '=', "16% Corona Tax"), ('name', '=', "16% abgesenkte MwSt")],limit=1)
                            if invoice_line_tax_ids not in self.invoice_line_tax_ids:
                                line.update({'invoice_line_tax_ids': invoice_line_tax_ids})


                    elif line.invoice_id.partner_id.country_id.name in ['Belgium', 'Bulgaria', 'Denmark', 'Estonia',
                                                                        'Finnland',
                                                                        'France', 'Greece', 'United Kingdom',
                                                                        'Netherlands',
                                                                        'Italy', 'Ireland', 'Crotia', 'Latvia',
                                                                        'Lithunia',
                                                                        'Luxembourg', 'Malta', 'Austria', 'Poland',
                                                                        'Portugal',
                                                                        'Romania', 'Sweden', 'Slovakia', 'Slovenia',
                                                                        'Spain',
                                                                        'Czech Republic', 'Hungary',
                                                                        'Cypress'] or line.invoice_id.partner_id.country_id.name in [
                        'Belgien', 'Bulgarien', 'Dänemark', 'Estland', 'Finnland', 'Frankreich', 'Griechenland',
                        'Vereinigtes Königreich', 'Niederlande', 'Italien', 'Irland', 'Crotia', 'Lettland', 'Lithunien',
                        'Luxemburg', 'Malta', 'Österreich', 'Polen', 'Portugal', 'Rumänien', 'Schweden', 'Slowakei',
                        'Slowenien', 'Spanien', 'Tschechien Republik ', 'Ungarn', 'Zypresse', 'Lithunia',
                        'Tschechische Republik'] or line.invoice_id.partner_id.country_id.name in ['Belgique',
                                                                                                   'Bulgarie',
                                                                                                   'Danemark',
                                                                                                   'Estonie',
                                                                                                   'Finlande', 'France',
                                                                                                   'Grèce',
                                                                                                   'Royaume-Uni',
                                                                                                   'Pays-Bas',
                                                                                                   'Italie', 'Irlande',
                                                                                                   'Crotie',
                                                                                                   ' Lettonie',
                                                                                                   'Lithunie',
                                                                                                   'Luxembourg',
                                                                                                   'Malte',
                                                                                                   'Autriche',
                                                                                                   'Pologne',
                                                                                                   'Portugal',
                                                                                                   'Roumanie',
                                                                                                   'Suède', 'Slovaquie',
                                                                                                   'Slovénie',
                                                                                                   'Espagne',
                                                                                                   'République tchèque',
                                                                                                   'Hongrie', 'Cyprès']:
                        if fiscal_position_name:
                            if 'EU' in fiscal_position_name:  # Scenario 1 ---->
                                invoice_line_tax_ids = self.env['account.tax'].search(
                                    [('name', '=', "Steuerfreie innergem. Lieferung (§4 Abs. 1b UStG)")],limit=1)
                                if invoice_line_tax_ids not in self.invoice_line_tax_ids:
                                    line.update({'invoice_line_tax_ids': invoice_line_tax_ids})

                            if 'EU' not in fiscal_position_name:  # Scenario 2 ---->
                                invoice_line_tax_ids = self.env['account.tax'].search(
                                    [('name', '=', "Steuerfreie innergem. Lieferung (§4 Abs. 1b UStG)")],limit=1)
                                if invoice_line_tax_ids not in self.invoice_line_tax_ids:
                                    line.update({'invoice_line_tax_ids': invoice_line_tax_ids})
                        else:  # Scenario 2 ---->
                            invoice_line_tax_ids = self.env['account.tax'].search(
                                [('name', '=', "Steuerfreie innergem. Lieferung (§4 Abs. 1b UStG)")],limit=1)
                            if invoice_line_tax_ids not in self.invoice_line_tax_ids:
                                line.update({'invoice_line_tax_ids': invoice_line_tax_ids})

                    else:
                        if fiscal_position_name:
                            if 'EU' in fiscal_position_name:  # Scenario 1 ---->
                                invoice_line_tax_ids = self.env['account.tax'].search(
                                    [('name', '=', "Steuerfreie Ausfuhr (§4 Nr. 1a UStG)")],limit=1)
                                if invoice_line_tax_ids not in self.invoice_line_tax_ids:
                                    line.update({'invoice_line_tax_ids': invoice_line_tax_ids})

                            if 'EU' not in fiscal_position_name:  # Scenario 2 ---->
                                invoice_line_tax_ids = self.env['account.tax'].search(
                                    [('name', '=', "Steuerfreie Ausfuhr (§4 Nr. 1a UStG)")],limit=1)
                                if invoice_line_tax_ids not in self.invoice_line_tax_ids:
                                    line.update({'invoice_line_tax_ids': invoice_line_tax_ids})
                        else:  # Scenario 2 ---->
                            invoice_line_tax_ids = self.env['account.tax'].search(
                                [('name', '=', "Steuerfreie Ausfuhr (§4 Nr. 1a UStG)")],limit=1)
                            if invoice_line_tax_ids not in self.invoice_line_tax_ids:
                                line.update({'invoice_line_tax_ids': invoice_line_tax_ids})

            self.account_id = fpos.map_account(invoice_line_tax_ids.account_id)


            # if fpos:
            #     self.account_id = fpos.map_account(self.account_id)

        else:
            self_lang = self
            if part.lang:
                self_lang = self.with_context(lang=part.lang)

            product = self_lang.product_id

            if self.partner_id.supplier:
                account = self.get_invoice_line_account(type, product, fpos, company)
            else:
                account = self.invoice_line_tax_ids.account_id

            if account:
                self.account_id = account.id
            self._set_taxes()

            product_name = self_lang._get_invoice_line_name_from_product()
            if product_name != None:
                self.name = product_name

            if not self.uom_id or product.uom_id.category_id.id != self.uom_id.category_id.id:
                self.uom_id = product.uom_id.id
            domain['uom_id'] = [('category_id', '=', product.uom_id.category_id.id)]

            if company and currency:

                if self.uom_id and self.uom_id.id != product.uom_id.id:
                    self.price_unit = product.uom_id._compute_price(self.price_unit, self.uom_id)
        return {'domain': domain}


    def _set_taxes(self):
        """ Used in on_change to set taxes and price"""
        self.ensure_one()
        # Keep only taxes of the company
        company_id = self.company_id or self.env.user.company_id

        # change code logic
        # if self.invoice_id.type in ('out_invoice', 'out_refund'):
        #     taxes = self.invoice_line_tax_ids or self.product_id.taxes_id.filtered(lambda r: r.company_id == company_id) or self.account_id.tax_ids or self.invoice_id.company_id.account_sale_tax_id
        # else:
        #     taxes = self.product_id.supplier_taxes_id.filtered(lambda r: r.company_id == company_id) or self.account_id.tax_ids or self.invoice_id.company_id.account_purchase_tax_id

        for line in self:

            if not line.invoice_id.partner_id:
                raise ValidationError("Please select the customer name!")

            if line.invoice_id.partner_id.country_id or line.invoice_id.partner_id.property_account_position_id.name:
                fiscal_position_name = line.invoice_id.partner_id.property_account_position_id.name
                # change code ['Germany','Deutschland','Allemagne']#
                if line.invoice_id.partner_id.country_id.name in ['Germany', 'Deutschland', 'Allemagne']:
                    if fiscal_position_name:
                        if 'EU' in fiscal_position_name:  # Scenario 1 ---->
                            invoice_line_tax_ids = self.env['account.tax'].search(
                                ['|', ('name', '=', "16% Corona Tax"), ('name', '=', "16% abgesenkte MwSt")],limit=1)
                            if invoice_line_tax_ids not in self.invoice_line_tax_ids:
                                line.update({'invoice_line_tax_ids': invoice_line_tax_ids})

                        if 'EU' not in fiscal_position_name:  # Scenario 2 ---->
                            invoice_line_tax_ids = self.env['account.tax'].search(
                                ['|', ('name', '=', "16% Corona Tax"), ('name', '=', "16% abgesenkte MwSt")],limit=1)
                            if invoice_line_tax_ids not in self.invoice_line_tax_ids:
                                line.update({'invoice_line_tax_ids': invoice_line_tax_ids})
                    else:  # Scenario 2 ---->
                        invoice_line_tax_ids = self.env['account.tax'].search(
                            ['|', ('name', '=', "16% Corona Tax"), ('name', '=', "16% abgesenkte MwSt")],limit=1)
                        if invoice_line_tax_ids not in self.invoice_line_tax_ids:
                            line.update({'invoice_line_tax_ids': invoice_line_tax_ids})


                elif line.invoice_id.partner_id.country_id.name in ['Belgium', 'Bulgaria', 'Denmark', 'Estonia', 'Finnland',
                                                                  'France', 'Greece', 'United Kingdom', 'Netherlands',
                                                                  'Italy', 'Ireland', 'Crotia', 'Latvia', 'Lithunia',
                                                                  'Luxembourg', 'Malta', 'Austria', 'Poland', 'Portugal',
                                                                  'Romania', 'Sweden', 'Slovakia', 'Slovenia', 'Spain',
                                                                  'Czech Republic', 'Hungary',
                                                                  'Cypress'] or line.invoice_id.partner_id.country_id.name in [
                    'Belgien', 'Bulgarien', 'Dänemark', 'Estland', 'Finnland', 'Frankreich', 'Griechenland',
                    'Vereinigtes Königreich', 'Niederlande', 'Italien', 'Irland', 'Crotia', 'Lettland', 'Lithunien',
                    'Luxemburg', 'Malta', 'Österreich', 'Polen', 'Portugal', 'Rumänien', 'Schweden', 'Slowakei',
                    'Slowenien', 'Spanien', 'Tschechien Republik ', 'Ungarn', 'Zypresse', 'Lithunia',
                    'Tschechische Republik'] or line.invoice_id.partner_id.country_id.name in ['Belgique', 'Bulgarie',
                                                                                             'Danemark', 'Estonie',
                                                                                             'Finlande', 'France', 'Grèce',
                                                                                             'Royaume-Uni', 'Pays-Bas',
                                                                                             'Italie', 'Irlande', 'Crotie',
                                                                                             ' Lettonie', 'Lithunie',
                                                                                             'Luxembourg', 'Malte',
                                                                                             'Autriche', 'Pologne',
                                                                                             'Portugal', 'Roumanie',
                                                                                             'Suède', 'Slovaquie',
                                                                                             'Slovénie', 'Espagne',
                                                                                             'République tchèque',
                                                                                             'Hongrie', 'Cyprès']:
                    if fiscal_position_name:
                        if 'EU' in fiscal_position_name:  # Scenario 1 ---->
                            invoice_line_tax_ids = self.env['account.tax'].search(
                                [('name', '=', "Steuerfreie innergem. Lieferung (§4 Abs. 1b UStG)")],limit=1)
                            if invoice_line_tax_ids not in self.invoice_line_tax_ids:
                                line.update({'invoice_line_tax_ids': invoice_line_tax_ids})

                        if 'EU' not in fiscal_position_name:  # Scenario 2 ---->
                            invoice_line_tax_ids = self.env['account.tax'].search(
                                [('name', '=', "Steuerfreie innergem. Lieferung (§4 Abs. 1b UStG)")],limit=1)
                            if invoice_line_tax_ids not in self.invoice_line_tax_ids:
                                line.update({'invoice_line_tax_ids': invoice_line_tax_ids})
                    else:  # Scenario 2 ---->
                        invoice_line_tax_ids = self.env['account.tax'].search(
                            [('name', '=', "Steuerfreie innergem. Lieferung (§4 Abs. 1b UStG)")],limit=1)
                        if invoice_line_tax_ids not in self.invoice_line_tax_ids:
                            line.update({'invoice_line_tax_ids': invoice_line_tax_ids})

                else:
                    if fiscal_position_name:
                        if 'EU' in fiscal_position_name:  # Scenario 1 ---->
                            invoice_line_tax_ids = self.env['account.tax'].search([('name', '=', "Steuerfreie Ausfuhr (§4 Nr. 1a UStG)")],limit=1)
                            if invoice_line_tax_ids not in self.invoice_line_tax_ids:
                                line.update({'invoice_line_tax_ids': invoice_line_tax_ids})

                        if 'EU' not in fiscal_position_name:  # Scenario 2 ---->
                            invoice_line_tax_ids = self.env['account.tax'].search([('name', '=', "Steuerfreie Ausfuhr (§4 Nr. 1a UStG)")],limit=1)
                            if invoice_line_tax_ids not in self.invoice_line_tax_ids:
                                line.update({'invoice_line_tax_ids': invoice_line_tax_ids})
                    else:  # Scenario 2 ---->
                        invoice_line_tax_ids = self.env['account.tax'].search([('name', '=', "Steuerfreie Ausfuhr (§4 Nr. 1a UStG)")],limit=1)
                        if invoice_line_tax_ids not in self.invoice_line_tax_ids:
                            line.update({'invoice_line_tax_ids': invoice_line_tax_ids})

        self.invoice_line_tax_ids = fp_taxes = self.invoice_id.fiscal_position_id.map_tax(invoice_line_tax_ids, self.product_id, self.invoice_id.partner_id)

        fix_price = self.env['account.tax']._fix_tax_included_price
        if self.invoice_id.type in ('in_invoice', 'in_refund'):
            prec = self.env['decimal.precision'].precision_get('Product Price')
            if not self.price_unit or float_compare(self.price_unit, self.product_id.standard_price, precision_digits=prec) == 0:
                self.price_unit = fix_price(self.product_id.standard_price, invoice_line_tax_ids, fp_taxes)
                self._set_currency()
        else:
            self.price_unit = fix_price(self.product_id.lst_price, invoice_line_tax_ids, fp_taxes)
            self._set_currency()


    # @api.multi

	# @api.onchange('tax_id')
	# def custom_tax(self):
	# 	import pdb;pdb.set_trace()
	# 	# if self.order_line:
	# 	if self.order_id.partner_id.country_id or self.order_id.partner_id.property_account_position_id.name:
	# 		if self.order_id.partner_id.country_id.name=='Germany':
	# 			# taxx=self.env['account.tax'].search([])
	# 			# for item in taxx:
	# 			tax_id=self.env['account.tax'].search([('name','=',"19% Umsatzsteuer")])
	# 			if tax_id not in self.tax_id:
	# 				# if item.name=="19% Umsatzsteuer":
	# 					# self.order_line.update({'tax_id':item and [(6,0,self.env['account.tax'].search([]))] })
	# 					self.update({'tax_id':tax_id})
	# 					# _compute_tax_id()

	# 			# elif self.order_id.partner_id.vat:
	# 			# 	if self.order_id.partner_id.country_id and self.partner_id.property_account_position_id.name and self.partner_id.vat: 
	# 			# 		if self.order_id.partner_id.country_id.name!='Germany' and 'EU' in self.partner_id.property_account_position_id.name and self.partner_id.vat:
	# 			# 			self.update({'tax_id':None})


	# 			# elif not self.order_id.partner_id.vat:
	# 			# 	if self.order_id.partner_id.country_id and self.order_id.partner_id.property_account_position_id.name and self.partner_id.is_retailer:
	# 			# 		if self.order_id.partner_id.country_id.name!='Germany' and 'EU' in self.order_id.partner_id.property_account_position_id.name and self.partner_id.is_retailer:
	# 			# 			# taxx=self.env['account.tax'].search([])
	# 			# 			# for item in taxx:
	# 			# 			# 	if item.name=="19% Umsatzsteuer":
	# 			# 			tax_id=self.env['account.tax'].search([('name','=',"19% Umsatzsteuer")])
	# 			# 			if tax_id not in self.tax_id:
	# 			# 					self.update({'tax_id':item})


	# @api.multi
	# def action_view_invoice(self):
	# 	res=super(CustomSaleOrder,self).action_view_invoice()
	# 	if self.partner_id.country_id or self.partner_id.property_account_position_id:
	# 		if self.partner_id.country_id.name=='Germany':
	# 			res1=self.env['account.invoice'].search([])
	# 			for cust in res1:
	# 				if cust.partner_id==self.partner_id:
	# 					taxx=self.env['account.tax'].search([])
	# 					for item in taxx:
	# 						if item.name=="19% Umsatzsteuer":
	# 							cust.invoice_line_ids.update({'invoice_line_tax_ids':item})

	# 		elif self.partner_id.vat:
	# 			if self.partner_id.country_id and self.partner_id.property_account_position_id.name and self.partner_id.vat and self.partner_id.is_retailer:
	# 				if self.partner_id.country_id.name!='Germany' and 'EU' in self.partner_id.property_account_position_id.name and self.partner_id.vat and self.partner_id.is_retailer:
	# 					res1=self.env['account.invoice'].search([])
	# 					for cust in res1:
	# 						if cust.partner_id==self.partner_id:
	# 							cust.invoice_line_ids.update({'invoice_line_tax_ids':None})


	# 		elif not self.partner_id.vat:
	# 			if self.partner_id.country_id and self.partner_id.property_account_position_id.name and self.partner_id.is_retailer:
	# 				if self.partner_id.country_id.name!='Germany' and 'EU' in self.partner_id.property_account_position_id.name and self.partner_id.is_retailer:
	# 					res1=self.env['account.invoice'].search([])
	# 					for cust in res1:
	# 						if cust.partner_id==self.partner_id:
	# 							taxx=self.env['account.tax'].search([])
	# 							for item in taxx:
	# 								if item.name=="19% Umsatzsteuer":
	# 									cust.invoice_line_ids.update({'invoice_line_tax_ids':item})

	# 	return res



