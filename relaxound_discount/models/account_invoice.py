from odoo import models, fields, api
from datetime import datetime , timedelta,date

class InvoiceOrderDiscount(models.Model):
	"""docstring for InvoiceOrderDiscount"""
	_inherit  = "account.invoice"

	is_custom_relax_discount = 	fields.Boolean(default=False, string='Realxond Discount')

	percentage = fields.Char(compute='_compute_percentage', select=False, invisible="1")
	discount1 = fields.Float(compute='_compute_discount_line')
	discount_2 = fields.Float(string='Amount After 2% Discount',compute='_compute_discount_2')
	spl_discount = fields.Float(compute='_compute_spl_discount')
	spl_percentage = fields.Char(compute='_compute_spl_percentage', select=False, invisible="1")
	amount_before_discount = fields.Float('Untaxed Amount',compute='_compute_discount_line')
	amount_after_discount = fields.Float(compute='_compute_discount_line')
	set_desription = fields.Char('Note', compute='_set_description')
	set_desription1 = fields.Text('Note', compute='_set_description')

	super_spl_discount = fields.Boolean('Super Special Discount')
	hide_amount_untaxed = fields.Boolean(compute='_compute_hide_amount_untaxed')
	hide = fields.Boolean(string='Hide', compute="_compute_hide")
	hide_spl_discount = fields.Boolean(string='Hide discount', compute='_compute_hide_discount')
	hide_2_discount = fields.Boolean(string='Hide 2% discount', compute='_compute_hide_2_discount')
	hide_france_note = fields.Boolean(string='Hide france desc', compute='_compute_hide_france_desc')

	date_invoice_compute = fields.Boolean(string='Date of the order',
										  compute='_date_invoice_compute')
	
	pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')

	@api.depends('partner_id.property_product_pricelist')
	def _date_invoice_compute(self):
		for rec in self:
			if rec.type != 'out_refund':
				if ((rec.date_invoice and rec.date_invoice >= date(2021, 1, 1)) or (
						not rec.date_invoice and date.today() >= date(2021, 1, 1))):
					rec.date_invoice_compute = True
				else:
					rec.date_invoice_compute = False

	@api.depends('partner_id.property_product_pricelist')
	def _compute_hide_france_desc(self):
		# simple logic, but you can do much more here
		for rec in self:
			if rec.type != 'out_refund':
				# datetime.strptime('1/1/2021', "%m/%d/%y")
				if rec.date_invoice_compute and rec.partner_id.is_retailer and rec.partner_id.country_id.name == 'France' and (
						(rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (
						not rec.origin1 and rec.partner_id.property_product_pricelist.name == 'Preismodell 2021')):
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
			if rec.type != 'out_refund':
				# datetime.strptime('1/1/2021', "%m/%d/%y")
				if rec.date_invoice_compute and (
						rec.partner_id.is_retailer or rec.origin1.partner_id.is_retailer) and rec.partner_id.country_id.name != 'France' and (
						(rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (
						not rec.origin1 and rec.partner_id.property_product_pricelist.name == 'Preismodell 2021')):
					rec.hide_2_discount = True
				else:
					rec.hide_2_discount = False

	@api.onchange('origin1.super_spl_discount', 'partner_id.property_product_pricelist')
	def _compute_hide_discount(self):
		for rec in self:
			if rec.type != 'out_refund':
				if rec.date_invoice_compute and rec.partner_id.is_retailer and rec.origin1.super_spl_discount and (
						(rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (
						not rec.origin1 and rec.partner_id.property_product_pricelist.name == 'Preismodell 2021')):
					rec.hide_spl_discount = True
				else:
					rec.hide_spl_discount = False

	@api.depends('partner_id.property_product_pricelist')
	def _compute_hide(self):
		# simple logic, but you can do much more here
		for rec in self:
			if rec.type != 'out_refund':
				# datetime.strptime('1/1/2021', "%m/%d/%y")
				if rec.date_invoice_compute and (
						(rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (
						not rec.origin1 and rec.partner_id.property_product_pricelist.name == 'Preismodell 2021')):
					rec.hide = True
				else:
					rec.hide = False

	@api.depends('partner_id.property_product_pricelist')
	def _compute_hide_amount_untaxed(self):
		# simple logic, but you can do much more here
		for rec in self:
			if (rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name != 'Preismodell 2021') or (
					not rec.origin1 and rec.partner_id.property_product_pricelist.name != 'Preismodell 2021'):
				rec.hide_amount_untaxed = True
			else:
				rec.hide_amount_untaxed = False



	@api.multi
	@api.onchange('partner_id', 'invoice_line_ids')
	def _compute_discount_line(self):
		for rec in self:
			if rec.type != 'out_refund':
				if (rec.date_invoice_compute and rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (
						not rec.origin1 and rec.date_invoice_compute and rec.partner_id.property_product_pricelist.name == 'Preismodell 2021'):
					amount_untaxed = 0.0
					for line in rec.invoice_line_ids:
						amount_untaxed += line.subtotal
					if amount_untaxed >= 500 and amount_untaxed < 1000:
						rec.discount1 = (5 * (amount_untaxed)) / 100
						rec.amount_before_discount = amount_untaxed
						if rec.origin1.super_spl_discount:
							# rec.amount_after_discount = amount_untaxed - rec.discount1 - ((5 * (amount_untaxed)) / 100)
							rec.amount_after_discount = rec.amount_untaxed
						else:
							rec.amount_after_discount = amount_untaxed - rec.discount1


					elif amount_untaxed >= 1000 and amount_untaxed < 1500:
						rec.discount1 = (7 * (amount_untaxed)) / 100
						rec.amount_before_discount = amount_untaxed
						if rec.origin1.super_spl_discount:
							# rec.amount_after_discount = amount_untaxed - rec.discount1 - ((3 * (amount_untaxed)) / 100)
							rec.amount_after_discount = rec.amount_untaxed
						else:
							rec.amount_after_discount = amount_untaxed - rec.discount1

					elif amount_untaxed >= 1500:
						rec.discount1 = (10 * (amount_untaxed)) / 100
						rec.amount_before_discount = amount_untaxed
						if rec.origin1.super_spl_discount:
							# rec.amount_after_discount = amount_untaxed - rec.discount1 - ((0 * (amount_untaxed)) / 100)
							rec.amount_after_discount = rec.amount_untaxed
						else:
							rec.amount_after_discount = amount_untaxed - rec.discount1

					elif amount_untaxed < 500:
						rec.discount1 = 0
						rec.amount_before_discount = amount_untaxed
						if rec.origin1.super_spl_discount:
							# rec.amount_after_discount = amount_untaxed - rec.discount1 - ((10 * (amount_untaxed)) / 100)
							rec.amount_after_discount = rec.amount_untaxed
						else:
							rec.amount_after_discount = amount_untaxed - rec.discount1


	@api.multi
	@api.onchange('partner_id', 'invoice_line_ids')
	def _compute_spl_discount(self):
		for rec in self:
			if (rec.date_invoice_compute and rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (
					not rec.origin1 and rec.date_invoice_compute and rec.partner_id.property_product_pricelist.name == 'Preismodell 2021'):
				amount_untaxed = 0.0
				for line in rec.invoice_line_ids:
					amount_untaxed += line.subtotal
				if amount_untaxed >= 500 and amount_untaxed < 1000:
					rec.spl_discount = (5 * (amount_untaxed)) / 100

				elif amount_untaxed >= 1000 and amount_untaxed < 1500:
					rec.spl_discount = (3 * (amount_untaxed)) / 100

				elif amount_untaxed >= 1500:
					rec.spl_discount = (0 * (amount_untaxed)) / 100

				elif amount_untaxed < 500:
					rec.spl_discount = (0 * (amount_untaxed)) / 100

	@api.multi
	def _compute_spl_percentage(self):
		for rec in self:
			if rec.type != 'out_refund':
				if (rec.date_invoice_compute) and (rec.origin1.super_spl_discount) and (
						(rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (
						not rec.origin1 and rec.partner_id.property_product_pricelist.name == 'Preismodell 2021')):
					amount_untaxed = 0.0
					for line in rec.invoice_line_ids:
						amount_untaxed += line.subtotal
					if (
							rec.partner_id.is_retailer or rec.origin1.partner_id.is_retailer) and amount_untaxed >= 500 and amount_untaxed < 1000:
						rec.spl_percentage = '5%:'
						rec.spl_percentage = "Special Discount {}".format(rec.spl_percentage)
					elif (
							rec.partner_id.is_retailer or rec.origin1.partner_id.is_retailer) and amount_untaxed >= 1000 and amount_untaxed < 1500:
						rec.spl_percentage = '3%:'
						rec.spl_percentage = "Special Discount {}".format(rec.spl_percentage)
					elif (
							rec.partner_id.is_retailer or rec.origin1.partner_id.is_retailer) and amount_untaxed < 500 and amount_untaxed > 0:
						rec.spl_percentage = '10%:'
						rec.spl_percentage = "Special Discount {}".format(rec.spl_percentage)
					else:
						rec.spl_percentage = '0%:'
						rec.spl_percentage = "Discount {}".format(rec.spl_percentage)

	@api.multi
	@api.onchange('partner_id', 'invoice_line_ids')
	def _compute_percentage(self):
		for rec in self:
			if rec.type != 'out_refund':
				if (
						rec.date_invoice_compute and rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (
						not rec.origin1 and rec.date_invoice_compute and rec.partner_id.property_product_pricelist.name == 'Preismodell 2021'):
					amount_untaxed = 0.0
					for line in rec.invoice_line_ids:
						amount_untaxed += line.subtotal
					if amount_untaxed >= 500 and amount_untaxed < 1000:
						rec.percentage = '5%:'
						rec.percentage = "Discount {}".format(rec.percentage)
					elif amount_untaxed >= 1000 and amount_untaxed < 1500:
						rec.percentage = '7%:'
						rec.percentage = "Discount {}".format(rec.percentage)
					elif amount_untaxed >= 1500:
						rec.percentage = '10%:'
						rec.percentage = "Discount {}".format(rec.percentage)
					else:
						rec.percentage = '0%:'
						rec.percentage = "Discount {}".format(rec.percentage)

	@api.multi
	@api.onchange('partner_id', 'invoice_line_ids', 'amount_total_new')
	def _compute_discount_2(self):
		for rec in self:
			if rec.type != 'out_refund':
				if (rec.date_invoice_compute and rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (
						not rec.origin1 and rec.date_invoice_compute and rec.partner_id.property_product_pricelist.name == 'Preismodell 2021'):
					rec.discount_2 = rec.amount_total - ((2 * rec.amount_total) / 100)

	@api.multi
	@api.onchange('partner_id', 'invoice_line_ids', 'amount_total')
	def _set_description(self):
		for rec in self:
			if rec.type != 'out_refund':
				if rec.date_invoice_compute and (
						rec.partner_id.is_retailer or rec.origin1.partner_id.is_retailer) and rec.partner_id.lang in [
					'de_CH', 'de_DE'] and rec.partner_id.country_id.name != 'France' and (
						(rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (
						not rec.origin1 and rec.partner_id.property_product_pricelist.name == 'Preismodell 2021')) and rec.date_invoice:
					rec.set_desription = '2% Skonto bei SEPA-Einzug oder Zahlungseingang bis ' + str(
						(rec.date_invoice + timedelta(days=14)).strftime('%d.%m.%Y'))
				elif rec.date_invoice_compute and (
						rec.partner_id.is_retailer or rec.origin1.partner_id.is_retailer) and rec.partner_id.lang in [
					'de_CH', 'de_DE'] and rec.partner_id.country_id.name != 'France' and (
						(rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (
						not rec.origin1 and rec.partner_id.property_product_pricelist.name == 'Preismodell 2021')) and not rec.date_invoice:
					rec.set_desription = '2% Skonto bei SEPA-Einzug oder Zahlungseingang bis ' + str(
						(date.today() + timedelta(days=14)).strftime('%d.%m.%Y'))

				elif rec.date_invoice_compute and (
						rec.partner_id.is_retailer or rec.origin1.partner_id.is_retailer) and rec.partner_id.lang not in [
					'de_CH', 'de_DE'] and rec.partner_id.country_id.name != 'France' and (
						(rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (
						not rec.origin1 and rec.partner_id.property_product_pricelist.name == 'Preismodell 2021')) and rec.date_invoice:
					rec.set_desription = '2% discount - payment by ' + str(
						(rec.date_invoice + timedelta(days=14)).strftime('%d.%m.%Y'))
				elif rec.date_invoice_compute and (
						rec.partner_id.is_retailer or rec.origin1.partner_id.is_retailer) and rec.partner_id.lang not in [
					'de_CH', 'de_DE'] and rec.partner_id.country_id.name != 'France' and (
						(rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (
						not rec.origin1 and rec.partner_id.property_product_pricelist.name == 'Preismodell 2021')) and not rec.date_invoice:
					rec.set_desription = '2% discount - payment by ' + str(
						(date.today() + timedelta(days=14)).strftime('%d.%m.%Y'))

				elif rec.date_invoice_compute and (
						rec.partner_id.is_retailer or rec.origin1.partner_id.is_retailer) and rec.partner_id.country_id.name == 'France' and (
						(rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (
						not rec.origin1 and rec.partner_id.property_product_pricelist.name == 'Preismodell 2021')) and rec.date_invoice:
					rec.set_desription1 = 'ESCOMPTE DE 2 %\nVous pouvez payer dans un délai de 30 jours nets par prélèvement bancaire/SEPA.\n En cas de paiement anticipé, vous bénéficiez d’une réduction supplémentaire de\n 2 % et la valeur de votre commende est réduit à '
				elif rec.date_invoice_compute and (
						rec.partner_id.is_retailer or rec.origin1.partner_id.is_retailer) and rec.partner_id.country_id.name == 'France' and (
						(rec.origin1.pricelist_id.name and rec.origin1.pricelist_id.name == 'Preismodell 2021') or (
						not rec.origin1 and rec.partner_id.property_product_pricelist.name == 'Preismodell 2021')) and not rec.date_invoice:
					rec.set_desription1 = 'ESCOMPTE DE 2 %\nVous pouvez payer dans un délai de 30 jours nets par prélèvement bancaire/SEPA.\n En cas de paiement anticipé, vous bénéficiez d’une réduction supplémentaire de\n 2 % et la valeur de votre commende est réduit à '
				else:
					pass

	@api.depends('date_invoice')
	def _get_date_invoice(self):
		for rec in self:
			if rec.type != 'out_refund':
				if rec.date_invoice:
					date_invoice = (rec.date_invoice + timedelta(days=14)).strftime('%d.%m.%Y')
					return date_invoice
				else:
					date_invoice = (date.today() + timedelta(days=14)).strftime('%d.%m.%Y')
					return date_invoice

	@api.model
	def create(self, vals):
		if 'Preismodell 2021' == self.env['res.partner'].search(
				[('id', '=', vals.get('partner_id'))]).property_product_pricelist.name:

			TOTAL = 0.0
			DISCOUNT = 0.0

			if vals.get('invoice_line_ids'):
				for order in vals.get('invoice_line_ids'):
					TOTAL = TOTAL + (order[2].get('quantity') * order[2].get('price_unit'))

				if TOTAL >= 500.00 and TOTAL < 1000.00:
					DISCOUNT = 5
				elif TOTAL >= 1000.00 and TOTAL < 1500.00:
					DISCOUNT = 7
				elif TOTAL >= 1500.00:
					DISCOUNT = 10

				for order in vals.get('invoice_line_ids'):
					order[2]['discount'] = DISCOUNT

				if vals.get('is_custom_relax_discount'):
					vals['is_custom_relax_discount'] = True

		elif 'Preismodell 2021' == self.env['product.pricelist'].search(
				[('id', '=', vals.get('pricelist_id'))]).name:

			TOTAL = 0.0
			DISCOUNT = 0.0

			if vals.get('invoice_line_ids'):
				for order in vals.get('invoice_line_ids'):
					TOTAL = TOTAL + (order[2].get('quantity') * order[2].get('price_unit'))

				if TOTAL >= 500.00 and TOTAL < 1000.00:
					DISCOUNT = 5
				elif TOTAL >= 1000.00 and TOTAL < 1500.00:
					DISCOUNT = 7
				elif TOTAL >= 1500.00:
					DISCOUNT = 10

				for order in vals.get('invoice_line_ids'):
					order[2]['discount'] = DISCOUNT

				if vals.get('is_custom_relax_discount'):
					vals['is_custom_relax_discount'] = True
		else:
			pass

		return super(InvoiceOrderDiscount, self).create(vals)

	@api.multi
	def write(self, vals):
		PRICELIST = False
		TOTAL = 0.0
		DISCOUNT = 0.0

		for rec in self:
			if vals.get('pricelist_id') or vals.get('partner_id'):
				if vals.get('pricelist_id'):
					if (rec.origin1 and 'Preismodell 2021' == rec.origin1.pricelist_id.name) or (not rec.origin1 and 'Preismodell 2021' == rec.env['product.pricelist'].search(
							[('id', '=', vals.get('pricelist_id'))]).name):
						PRICELIST = True
					elif not vals.get('partner_id'):
						if (rec.origin1 and 'Preismodell 2021' == rec.origin1.pricelist_id.name) or (not rec.origin1 and 'Preismodell 2021' == rec.partner_id.property_product_pricelist.name):
							PRICELIST = True
	      
				if not PRICELIST and vals.get('partner_id'):
					if (rec.origin1 and 'Preismodell 2021' == rec.origin1.pricelist_id.name) or (not rec.origin1 and 'Preismodell 2021' == rec.env['res.partner'].search(
							[('id', '=', vals.get('partner_id'))]).property_product_pricelist.name):
						PRICELIST = True
					elif not vals.get('pricelist_id'):
						if (rec.origin1 and 'Preismodell 2021' == rec.origin1.pricelist_id.name) or (not rec.origin1 and 'Preismodell 2021' == rec.pricelist_id.name):
							PRICELIST = True

			elif not PRICELIST and (rec.origin1 and 'Preismodell 2021' == rec.origin1.pricelist_id.name) or (not rec.origin1 and 'Preismodell 2021' == rec.partner_id.property_product_pricelist.name):
				PRICELIST = True


			invoice_order = super(InvoiceOrderDiscount, rec).write(vals)

			if not PRICELIST and rec.is_custom_relax_discount:

				for order in rec.env['account.invoice.line'].search([('invoice_id', '=', rec.id)]):
					order.discount = DISCOUNT

			elif PRICELIST:

				for order in rec.env['account.invoice.line'].search([('invoice_id', '=', rec.id)]):
					TOTAL = TOTAL + (order.quantity * order.price_unit)

				if TOTAL >= 500.00 and TOTAL < 1000.00:
					if rec.origin1.super_spl_discount:
						DISCOUNT = 10
					else:
						DISCOUNT = 5
				elif TOTAL >= 1000.00 and TOTAL < 1500.00:
					if rec.origin1.super_spl_discount:
						DISCOUNT = 10
					else:
						DISCOUNT = 7
				elif TOTAL >= 1500.00:
					if rec.origin1.super_spl_discount:
						DISCOUNT = 10
					else:
						DISCOUNT = 10

				for order in rec.env['account.invoice.line'].search([('invoice_id', '=', rec.id)]):
					order.discount = DISCOUNT

				return invoice_order



class OrderAccountLine(models.Model):
	_inherit = 'account.invoice.line'

	subtotal = fields.Float(String='Subtotal',compute='_compute_subtotal_price')

	@api.multi
	@api.onchange('quantity', 'invoice_line_tax_ids')
	def _compute_subtotal_price(self):
		for line in self:
			if line.invoice_id.partner_id.property_product_pricelist.name != 'Preismodell 2021' and line.invoice_id.origin1.pricelist_id.name != 'Preismodell 2021':
				line.subtotal = line.price_subtotal
			else:
				if line[0].invoice_line_tax_ids.name and 'include' not in line[0].invoice_line_tax_ids.name:
					line.subtotal = line.price_unit * line.quantity
				else:
					if line[0].invoice_line_tax_ids.name and 'include' in line[0].invoice_line_tax_ids.name:
						if line.invoice_id.amount_untaxed >= 500 and line.invoice_id.amount_untaxed < 1000:
							line.subtotal = (line.price_unit * line.quantity) - (
										(line[0].invoice_line_tax_ids.amount * (line.price_unit * line.quantity)) / 100)

						if line.invoice_id.amount_untaxed >= 1000 and line.invoice_id.amount_untaxed < 1500:
							line.subtotal = (line.price_unit * line.quantity) - (
										(line[0].invoice_line_tax_ids.amount * (line.price_unit * line.quantity)) / 100)

						if line.invoice_id.amount_untaxed >= 1500:
							line.subtotal = (line.price_unit * line.quantity) - (
										(line[0].invoice_line_tax_ids.amount * (line.price_unit * line.quantity)) / 100)

