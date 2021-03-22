# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime , timedelta,date

# class relaxound_discount(models.Model):
#     _name = 'relaxound_discount.relaxound_discount'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

class SaleOrderDiscount(models.Model):
	"""docstring for SaleOrderDiscount"""
	_inherit  = "sale.order"

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

	@api.depends('super_spl_discount', 'pricelist_id')
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
			if rec.pricelist_id.name == 'Preismodell 2021':
				rec.hide = True
			else:
				rec.hide = False

	@api.depends('pricelist_id')
	def _compute_hide_amount_untaxed(self):
		# simple logic, but you can do much more here
		for rec in self:
			if rec.pricelist_id.name != 'Preismodell 2021':
				rec.hide_amount_untaxed = True
			else:
				rec.hide_amount_untaxed = False

	def get_delivery_price(self):
		for order in self.filtered(lambda o: o.state in ('draft', 'sent') and len(o.order_line) > 0):
			# We do not want to recompute the shipping price of an already validated/done SO
			# or on an SO that has no lines yet
			order.delivery_rating_success = False
			res = order.carrier_id.rate_shipment(order)
			if res['success']:
				if self.date_order_compute and self.pricelist_id.name == 'Preismodell 2021' and self.amount_untaxed >= 250 and self.partner_id.country_id.name in ['Germany','Deutschland','Allemagne']:
					order.delivery_rating_success = True
					order.delivery_price = 0.0
					order.delivery_message = res['warning_message']
				else:
					order.delivery_rating_success = True
					order.delivery_price = res['price']
					order.delivery_message = res['warning_message']
			else:
				order.delivery_rating_success = False
				order.delivery_price = 0.0
				order.delivery_message = res['error_message']



	@api.multi
	@api.onchange('partner_id', 'order_line')
	def _compute_discount_line(self):
		for rec in self:
			if rec.date_order_compute and rec.pricelist_id.name == 'Preismodell 2021':
				amount_untaxed = 0.0
				for line in rec.order_line:
					# if 'included' not in line.tax_id.name:
					amount_untaxed += line.subtotal
				if amount_untaxed >= 500 and amount_untaxed < 1000:
					rec.discount1 = (5 * (amount_untaxed)) / 100
					rec.amount_before_discount = amount_untaxed
					if rec.super_spl_discount:
						# rec.amount_after_discount = amount_untaxed - rec.discount1 - ((5 * (amount_untaxed)) / 100)
						rec.amount_after_discount = rec.amount_untaxed

					else:
						rec.amount_after_discount = amount_untaxed - rec.discount1

				elif amount_untaxed >= 1000 and amount_untaxed < 1500:
					rec.discount1 = (7 * (amount_untaxed)) / 100
					rec.amount_before_discount = amount_untaxed
					if rec.super_spl_discount:
						# rec.amount_after_discount = amount_untaxed - rec.discount1 - ((3 * (amount_untaxed)) / 100)
						rec.amount_after_discount = rec.amount_untaxed

					else:
						rec.amount_after_discount = amount_untaxed - rec.discount1

				elif amount_untaxed >= 1500:
					rec.discount1 = (10 * (amount_untaxed)) / 100
					rec.amount_before_discount = amount_untaxed
					if rec.super_spl_discount:
						# rec.amount_after_discount = amount_untaxed - rec.discount1 - ((10 * (amount_untaxed)) / 100)
						rec.amount_after_discount = rec.amount_untaxed

					else:
						rec.amount_after_discount = amount_untaxed - rec.discount1

				elif amount_untaxed < 500:
					rec.discount1 = 0
					rec.amount_before_discount = amount_untaxed
					if rec.super_spl_discount:
						# rec.amount_after_discount = amount_untaxed - rec.discount1 - ((10 * (amount_untaxed)) / 100)
						rec.amount_after_discount = rec.amount_untaxed

					else:
						rec.amount_after_discount = amount_untaxed - rec.discount1

	@api.multi
	@api.onchange('partner_id', 'order_line')
	def _compute_spl_discount(self):
		for rec in self:
			if rec.date_order_compute and rec.pricelist_id.name == 'Preismodell 2021' and rec.super_spl_discount:
				amount_untaxed = 0.0
				for line in rec.order_line:
					amount_untaxed += line.subtotal
				if amount_untaxed >= 500 and amount_untaxed < 1000:
					rec.spl_discount = (5 * (amount_untaxed)) / 100

				elif amount_untaxed >= 1000 and amount_untaxed < 1500:
					rec.spl_discount = (3 * (amount_untaxed)) / 100

				elif amount_untaxed >= 1500:
					rec.spl_discount = (0 * (amount_untaxed)) / 100

				elif amount_untaxed < 500:
					rec.spl_discount = (10 * (amount_untaxed)) / 100

	@api.multi
	@api.onchange('partner_id', 'order_line', 'pricelist_id', 'super_spl_discount')
	def _compute_spl_percentage(self):
		for rec in self:
			if rec.date_order_compute and rec.pricelist_id.name == 'Preismodell 2021' and rec.super_spl_discount:
				amount_untaxed = 0.0
				for line in rec.order_line:
					amount_untaxed += line.subtotal
				if rec.partner_id.is_retailer and amount_untaxed >= 500 and amount_untaxed < 1000:
					rec.spl_percentage = '5%:'
					rec.spl_percentage = "Special Discount {}".format(rec.spl_percentage)
				elif rec.partner_id.is_retailer and amount_untaxed >= 1000 and amount_untaxed < 1500:
					rec.spl_percentage = '3%:'
					rec.spl_percentage = "Special Discount {}".format(rec.spl_percentage)
				elif rec.partner_id.is_retailer and amount_untaxed < 500 and amount_untaxed > 0:
					rec.spl_percentage = '10%:'
					rec.spl_percentage = "Special Discount {}".format(rec.spl_percentage)
				else:
					rec.spl_percentage = '0%:'
					rec.spl_percentage = "Special Discount {}".format(rec.spl_percentage)

	@api.multi
	@api.onchange('partner_id', 'order_line')
	def _compute_discount_2(self):
		for rec in self:
			if rec.date_order_compute and rec.pricelist_id.name == 'Preismodell 2021':
				rec.discount_2 = rec.amount_total - ((2 * rec.amount_total) / 100)

	@api.multi
	@api.onchange('partner_id', 'order_line', 'amount_total')
	def _set_description(self):
		for rec in self:
			if rec.date_order_compute and rec.partner_id.is_retailer and rec.partner_id.lang in ['de_CH',
																								 'de_DE'] and rec.partner_id.country_id.name != 'France' and rec.pricelist_id.name == 'Preismodell 2021' and rec.date_order:
				rec.set_desription = '2% Skonto bei SEPA-Einzug oder Zahlungseingang bis ' + str(
					(rec.date_order + timedelta(days=14)).strftime('%d.%m.%Y'))
			elif rec.date_order_compute and rec.partner_id.is_retailer and rec.partner_id.lang in ['de_CH',
																								   'de_DE'] and rec.partner_id.country_id.name != 'France' and rec.pricelist_id.name == 'Preismodell 2021' and not rec.date_order:
				rec.set_desription = '2% Skonto bei SEPA-Einzug oder Zahlungseingang bis ' + str(
					(date.today() + timedelta(days=14)).strftime('%d.%m.%Y'))

			elif rec.date_order_compute and rec.partner_id.is_retailer and rec.partner_id.lang not in ['de_CH',
																									   'de_DE'] and rec.partner_id.country_id.name != 'France' and rec.pricelist_id.name == 'Preismodell 2021' and rec.date_order:
				rec.set_desription = '2% discount - payment by ' + str(
					(rec.date_order + timedelta(days=14)).strftime('%d.%m.%Y'))
			elif rec.date_order_compute and rec.partner_id.is_retailer and rec.partner_id.lang not in ['de_CH',
																									   'de_DE'] and rec.partner_id.country_id.name != 'France' and rec.pricelist_id.name == 'Preismodell 2021' and not rec.date_order:
				rec.set_desription = '2% discount - payment by ' + str(
					(date.today() + timedelta(days=14)).strftime('%d.%m.%Y'))

			elif rec.date_order_compute and rec.partner_id.is_retailer and rec.partner_id.country_id.name == 'France' and rec.pricelist_id.name == 'Preismodell 2021' and rec.date_order:
				rec.set_desription1 = 'ESCOMPTE DE 2 %\nVous pouvez payer dans un délai de 30 jours nets par prélèvement bancaire/ SEPA.\nEn cas de paiement anticipé, vous bénéficiez d’une réduction supplémentaire de\n 2 % etla valeur de votre commande est réduite à '
			elif rec.date_order_compute and rec.partner_id.is_retailer and rec.partner_id.country_id.name == 'France' and rec.pricelist_id.name == 'Preismodell 2021' and not rec.date_order:
				rec.set_desription1 = 'ESCOMPTE DE 2 %\nVous pouvez payer dans un délai de 30 jours nets par prélèvement bancaire/ SEPA.\nEn cas de paiement anticipé, vous bénéficiez d’une réduction supplémentaire de\n 2 % etla valeur de votre commande est réduite à '
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

	@api.multi
	@api.onchange('partner_id', 'order_line', 'pricelist_id')
	def _compute_percentage(self):
		for rec in self:
			if rec.date_order_compute and rec.pricelist_id.name == 'Preismodell 2021':
				amount_untaxed = 0.0
				for line in rec.order_line:
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

	@api.model_create_multi
	def create(self, vals_list):
		if 'Preismodell 2021' == self.env['res.partner'].search(
				[('id', '=', vals_list[0].get('partner_id'))]).property_product_pricelist.name:

			TOTAL = 0.0
			DISCOUNT = 0.0

			if vals_list[0].get('order_line'):
				for order in vals_list[0].get('order_line'):
					TOTAL = TOTAL + (order[2].get('product_uom_qty') * order[2].get('price_unit'))

				if TOTAL >= 500.00 and TOTAL < 1000.00:
					if vals_list[0]['super_spl_discount']:
						DISCOUNT = 10
					else:
						DISCOUNT = 5
				elif TOTAL >= 1000.00 and TOTAL < 1500.00:
					if vals_list[0]['super_spl_discount']:
						DISCOUNT = 10
					else:
						DISCOUNT = 7
				elif TOTAL >= 1500.00:
					if vals_list[0]['super_spl_discount']:
						DISCOUNT = 10
					else:
						DISCOUNT = 10

				for order in vals_list[0].get('order_line'):
					order[2]['discount'] = DISCOUNT

				if vals_list[0].get('is_custom_relax_discount'):
					vals_list[0]['is_custom_relax_discount'] = True

		elif 'Preismodell 2021' == self.env['product.pricelist'].search(
				[('id', '=', vals_list[0].get('pricelist_id'))]).name:

			TOTAL = 0.0
			DISCOUNT = 0.0

			if vals_list[0].get('order_line'):
				for order in vals_list[0].get('order_line'):
					TOTAL = TOTAL + (order[2].get('product_uom_qty') * order[2].get('price_unit'))

				if TOTAL >= 500.00 and TOTAL < 1000.00:
					if vals_list[0]['super_spl_discount']:
						DISCOUNT = 10
					else:
						DISCOUNT = 5
				elif TOTAL >= 1000.00 and TOTAL < 1500.00:
					if vals_list[0]['super_spl_discount']:
						DISCOUNT = 10
					else:
						DISCOUNT = 7
				elif TOTAL >= 1500.00:
					if vals_list[0]['super_spl_discount']:
						DISCOUNT = 10
					else:
						DISCOUNT = 10

				for order in vals_list[0].get('order_line'):
					order[2]['discount'] = DISCOUNT

				if vals_list[0].get('is_custom_relax_discount'):
					vals_list[0]['is_custom_relax_discount'] = True
		else:
			pass

		return super(SaleOrderDiscount, self).create(vals_list)

	@api.multi
	def write(self, vals):
		PRICELIST = False
		TOTAL = 0.0
		DISCOUNT = 0.0

		if vals.get('pricelist_id') or vals.get('partner_id'):
			if vals.get('pricelist_id'):
				if 'Preismodell 2021' == self.env['product.pricelist'].search([('id','=',vals.get('pricelist_id'))]).name:
					PRICELIST =True
				elif not vals.get('partner_id'):
					if 'Preismodell 2021' == self.partner_id.property_product_pricelist.name:
						PRICELIST = True

			if not PRICELIST and vals.get('partner_id'):
				if 'Preismodell 2021' == self.env['res.partner'].search([('id','=',vals.get('partner_id'))]).property_product_pricelist.name:
					PRICELIST = True
				elif not vals.get('pricelist_id'):
					if 'Preismodell 2021' == self.pricelist_id.name:
						PRICELIST = True

		elif not PRICELIST and 'Preismodell 2021' == self.pricelist_id.name or 'Preismodell 2021' == self.partner_id.property_product_pricelist.name:
			PRICELIST = True

		if vals.get('order_line') and vals.get('partner_id'):
			print('$$$$ AND $$$$$$$')

		elif vals.get('order_line'):
			print('$$ OL $$')
		elif vals.get('partner_id'):
			print('$$ partner $$')

		# import pdb;pdb.set_trace()

		sale_order = super(SaleOrderDiscount, self).write(vals)

		print('SALE_ORDER : ', sale_order)

		if not PRICELIST and self.is_custom_relax_discount:
			# vals_list = list()
			# vals = dict()
			for order in self.env['sale.order.line'].search([('order_id','=', self.id)]):
				# vals_list.append([1, order.id, {'discount' : DISCOUNT}])
				order.discount = DISCOUNT
			# vals.update({'order_line' : vals_list})
			# print('VALS', vals)
			# self.write(vals)
		elif PRICELIST:
			# vals_list = list()
			# vals = dict()
			for order in self.env['sale.order.line'].search([('order_id','=', self.id)]):
				TOTAL = TOTAL + (order.product_uom_qty * order.price_unit)

			if TOTAL >= 500.00 and TOTAL < 1000.00:
				if self.super_spl_discount:
					DISCOUNT = 10
				else:
					DISCOUNT = 5
			elif TOTAL >= 1000.00 and TOTAL < 1500.00:
				if self.super_spl_discount:
					DISCOUNT = 10
				else:
					DISCOUNT = 7
			elif TOTAL >= 1500.00:
				if self.super_spl_discount:
					DISCOUNT = 10
				else:
					DISCOUNT = 10

			for order in self.env['sale.order.line'].search([('order_id','=', self.id)]):
				# vals_list.append([1, order.id, {'discount' : DISCOUNT}])
				order.discount = DISCOUNT
			# vals.update({'order_line' : vals_list})
			# print('VALS', vals)
			# self.write(vals)

		# return super(SaleOrderDiscount, self).write(vals)
		return sale_order



# Changes are adding for hiding subtotal w/o discount and adding subtotal with discount
class OrderSaleLine(models.Model):
	_inherit = "sale.order.line"

	subtotal = fields.Float(String='Subtotal',compute='_compute_subtotal_price')


	# @api.multi
	@api.onchange('product_uom_qty','tax_id')
	def _compute_subtotal_price(self):
		# import pdb;pdb.set_trace()
		for line in self:
			if line.order_id.pricelist_id.name != 'Preismodell 2021':
				line.subtotal = line.price_subtotal
			else:
				if line[0].tax_id.name and 'include' not in line[0].tax_id.name:
					line.subtotal = line.price_unit * line.product_uom_qty
				else:
					if line[0].tax_id.name and 'include' in line[0].tax_id.name:
						if line.order_id.amount_untaxed >= 500 and line.order_id.amount_untaxed < 1000:
							line.subtotal = (line.price_unit * line.product_uom_qty) - ((line[0].tax_id.amount*(line.price_unit * line.product_uom_qty))/100)

						if line.order_id.amount_untaxed >= 1000 and line.order_id.amount_untaxed < 1500:
							line.subtotal = (line.price_unit * line.product_uom_qty) - ((line[0].tax_id.amount*(line.price_unit * line.product_uom_qty))/100)

						if line.order_id.amount_untaxed >= 1500:
							line.subtotal = (line.price_unit * line.product_uom_qty) - ((line[0].tax_id.amount*(line.price_unit * line.product_uom_qty))/100)
