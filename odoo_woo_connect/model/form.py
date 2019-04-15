from odoo import api, fields, models

class Froms(models.Model):
	_inherit = 'sale.order'
	

	bill_of_sale = fields.Char(string='Bill Of Sale')
	
	installation_doc = fields.Char(string = 'Installation Doc')
	
	buyers_certificate = fields.Char(string = 'Buyers Certificate')
	
	agreement_to_insurance = fields.Char(string = 'Agreement To Insurance')
	
	seller_certificate = fields.Char(string = 'Seller Certificate')
	
	seller_in_state_delivery = fields.Char(string = 'Seller In State Delivery')
	
	as_is_dealer_warranty_disclaimer = fields.Char(string = 'As Is Dealer Warranty Disclaimer')
	
	lost_title = fields.Char(string = 'Lost Title')
	
	lemon_law = fields.Char(string = 'Lemon Law')
	
	buyers_affidavit = fields.Char(string = 'Buyers Affidavit')
	
	power_of_attorney = fields.Char(string = 'Power Of Attorney')