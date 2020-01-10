from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError



class CustomSaleOrder(models.Model):
    _inherit = 'sale.order.line'


    @api.multi
    def _compute_tax_id(self):
        for line in self:
            # ---------------------- base code ---------------------------------
            # fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            # # If company_id is set, always filter taxes by the company
            # taxes = line.product_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
            # line.tax_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_shipping_id) if fpos else taxes
            # ----------------------------------------------------------------------------------------------

            # 1. Scenario 1: Customer having country as Germany and Fiscal Position Contains EU --------> will get 19% tax.
            # 2. Scenario 2: Customer having country as Germany and  Fiscal Position Contains Other value or null ---------------->will get 19% tax.
            # 3. Scenario 3: customer is a retailer outside of Germany and within EU it needs a VAT ---------------->will get 0% tax.
            # 4. Scenario 4: customer is a retailer outside of Germany and within EU it needs a VAT is missing  --------->will get 19% tax.


            if not line.order_id.partner_id:
                raise ValidationError("Please select the customer name!")

            if line.order_id.partner_id.country_id or line.order_id.partner_id.property_account_position_id.name:
                
                fiscal_position_name = line.order_id.partner_id.property_account_position_id.name
                # if line.order_id.partner_id.country_id.name=='Germany':
                if line.order_id.partner_id.country_id.name in ['Germany','Deutschland','Allemagne']:
                    if fiscal_position_name:
                        if 'EU' in fiscal_position_name: # Scenario 1 ---->
                            tax_id=self.env['account.tax'].search([('name','=',"19% Umsatzsteuer")])
                            if tax_id not in self.tax_id:
                                line.update({'tax_id':tax_id})

                        if 'EU' not in fiscal_position_name: # Scenario 2 ---->  
                            tax_id=self.env['account.tax'].search([('name','=',"19% Umsatzsteuer")])
                            if tax_id not in self.tax_id:
                                line.update({'tax_id':tax_id})
                    else: # Scenario 2 ---->
                        tax_id=self.env['account.tax'].search([('name','=',"19% Umsatzsteuer")])
                        if tax_id not in self.tax_id:
                            line.update({'tax_id':tax_id})

                # if line.order_id.partner_id.country_id.name!='Germany':
                if line.order_id.partner_id.country_id.name not in ['Germany','Deutschland','Allemagne']:
                    if fiscal_position_name:
                        if line.order_id.partner_id.vat: # Scenario 3 ----->
                            if 'EU' in fiscal_position_name:
                                line.update({'tax_id':None})

                        else:  # Scenario 4 ------>
                            if 'EU' in fiscal_position_name:
                                tax_id=self.env['account.tax'].search([('name','=',"19% Umsatzsteuer")])
                                if tax_id not in self.tax_id:
                                    line.update({'tax_id':tax_id})



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



