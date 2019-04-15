#    Techspawn Solutions Pvt. Ltd.
#    Copyright (C) 2016-TODAY Techspawn(<http://www.Techspawn.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
import requests
import logging
from ..model.api import API
from datetime import datetime
from datetime import timedelta
from ..unit.backend_adapter import WpImportExport
_logger = logging.getLogger(__name__)

class WpCustomerImport(WpImportExport):
	""" Models for woocommerce customer ixport """
	def get_api_method(self, method, args, count=None, date=None):
		""" get api for customer"""
		api_method = None
		if method == 'customer_import':
			if not args[0]:
				api_method = 'customers/list?per_page=100&page='+str(count)
			else:
				api_method = 'customers/details/' + str(args[0])
		return api_method

	def import_customer(self,method,arguments,count=None,date=None):
		"""Import Customer data"""
		_logger.debug("Start calling Woocommerce api %s", method)
		result = {}

		res = self.importer(method, arguments,count)
		try:
			if 'false' or 'true' or 'null'in res.content:
				result = res.content.decode('utf-8')
				result=result.replace(
					'false', 'False')
				result = result.replace('true', 'True')
				result = result.replace('null', 'False')
				result = eval(result)
			else:
				result = eval(res.content)
		except:
			_logger.error("api.call(%s, %s) failed", method, arguments)
			raise
		else:
			_logger.debug("api.call(%s, %s) returned %s ",
						  method, arguments, result)

		return {'status': res.status_code, 'data': result or {}}

	def create_customer(self,backend,mapper,res,status=True):
		if (res['status'] == 200 or res['status'] == 201):
			bkend_id = mapper.backend_id.search([('id','=',backend.id)])
			contact = res['data']['customer_details']['billing']
			shipping = res['data']['customer_details']['shipping']
			metadata = res['data']['customer_details']['meta_data']
			wp_child_ids = []

			shipping_details = self.get_shipping(mapper, shipping)
			wp_child_ids.append([0,0,shipping_details])

			bill_country_id = mapper.env['res.partner'].country_id.search([('code','=',shipping['country'])]) 
			bill_state_id =	mapper.env['res.partner'].state_id.search([('code','=',shipping['state']),('country_id','=',bill_country_id.id)])		

			# if(status == True):
			# 	ride_details = res['data']['my_rides']
			# 	rides_list = []
			# 	ride_id = None
			# 	for ride in ride_details:
			# 		ride_id = mapper.env['wordpress.odoo.majorunit'].search([('backend_id','=',backend.id),('woo_id','=',ride)]).majorunit_id
			# 		if ride_id:
			# 			rides_list.append([6,0,ride_id.ids])
			# 		else:
			# 			major_unit = mapper.env['major_unit.major_unit']
			# 			major_unit.single_importer(backend,ride)
			# 			ride_id = mapper.env['wordpress.odoo.majorunit'].search([('backend_id','=',backend.id),('woo_id','=',ride)]).majorunit_id
			# 			rides_list.append([6,0,ride_id.ids])

			# 	service_rides = res['data']['my_services']
			# 	service_list = []
			# 	repair_order = None
			# 	for order in service_rides:
			# 		repair_order = mapper.env['wordpress.odoo.service.repair_order'].search([('backend_id','=',backend.id),('woo_id','=',order)]).service_rides_id
			# 		if repair_order:
			# 			service_list.append([6,0,repair_order.ids])
			# 		else:
			# 			repair_order_id = mapper.env['service.repair_order']
			# 			repair_order_id.single_importer(backend,order)
			# 			repair_order = mapper.env['wordpress.odoo.service.repair_order'].search([('backend_id','=',backend.id),('woo_id','=',order)]).service_rides_id
			# 			service_list.append([6,0,repair_order.ids])

			sale_orders = res['data']['order_ids']
			sales_list = []
			sale_id = None
			for sale in sale_orders:
				sale_id = mapper.env['wordpress.odoo.sale.order'].search([('backend_id','=',backend.id),('woo_id','=',sale)]).order_id
				if sale_id:
					sales_list.append([6,0,sale_id.ids])
				else:
					sale_order = mapper.env['sale.order']
					sale_order.single_importer(backend,sale)
					sale_id = mapper.env['wordpress.odoo.sale.order'].search([('backend_id','=',backend.id),('woo_id','=',sale)]).order_id
					sales_list.append([6,0,sale_id.ids])

			for addr in metadata:
				if isinstance(addr['value'], list):
					for type_of_addr in addr['value']:
						if isinstance(type_of_addr,dict):
							if 'type' in type_of_addr:
								if type_of_addr['type'] == 'billing':
									if 'billing_country' in type_of_addr:
										country_name = mapper.env['res.country'].search([('code','=',type_of_addr['billing_country'])])
									else:
										country_name = mapper.env['res.country']
									if 'billing_state' in type_of_addr:
										state_name = mapper.env['res.country.state'].search([('code','=',type_of_addr['billing_state']),('country_id','=',country_name.id)])
									else:
										state_name = mapper.env['res.country.state']
									shipping_details = {
									'type':'invoice',
									# 'name' : type_of_addr['billing_first_name'] or None,
									'street' : type_of_addr['billing_address_1'] or None,
									'street2' : type_of_addr['billing_address_2'] or None,
									'city' : type_of_addr['billing_city'] or None,
									'state_id': state_name.id or None,
									'zip' : type_of_addr['billing_postcode'] or None,
									'country_id' : country_name.id or None,
									}
									wp_child_ids.append([0,0,shipping_details])
								elif type_of_addr['type'] == 'shipping':
									if 'shipping_country' in type_of_addr:
										country_name = mapper.env['res.country'].search([('code','=',type_of_addr['shipping_country'])])
									else:
										country_name = mapper.env['res.country']
									if 'shipping_state' in type_of_addr:
										state_name = mapper.env['res.country.state'].search([('code','=',type_of_addr['shipping_state']),('country_id','=',country_name.id)])
									else:
										state_name = mapper.env['res.country.state']
									shipping_details = {
									'type':'delivery',
									# 'name' : shipping['first_name'] or None,
									'street' : type_of_addr['shipping_address_1'] or None,
									'street2' : type_of_addr['shipping_address_2'] or None,
									'city' : type_of_addr['shipping_city'] or None,
									'state_id': state_name.id or None,
									'zip' : type_of_addr['shipping_postcode'] or None,
									'country_id' : country_name.id or None,
									}
									wp_child_ids.append([0,0,shipping_details])

			for addr in metadata:
				for ele in addr:
					if isinstance(addr[ele],dict):
						for entry in addr[ele]:
							if isinstance(addr[ele][entry], dict):
								if addr[ele][entry]['type']=="billing":
									type_of_addr = addr[ele][entry]
									if 'billing_country' in type_of_addr:
										country_name = mapper.env['res.country'].search([('code','=',type_of_addr['billing_country'])])
									else:
										country_name = mapper.env['res.country']
									if 'billing_state' in type_of_addr:
										state_name = mapper.env['res.country.state'].search([('code','=',type_of_addr['billing_state']),('country_id','=',country_name.id)])
									else:
										state_name = mapper.env['res.country.state']
									shipping_details = {
									'type':'invoice',
									# 'name' : type_of_addr['billing_first_name'] or None,
									'street' : type_of_addr['billing_address_1'] or None,
									'street2' : type_of_addr['billing_address_2'] or None,
									'city' : type_of_addr['billing_city'] or None,
									'state_id': state_name.id or None,
									'zip' : type_of_addr['billing_postcode'] or None,
									'country_id' : country_name.id or None,
									}
									wp_child_ids.append([0,0,shipping_details])
								elif addr[ele][entry]['type']=="shipping":
									type_of_addr = addr[ele][entry]
									if 'shipping_country' in type_of_addr:
										country_name = mapper.env['res.country'].search([('code','=',type_of_addr['shipping_country'])])
									else:
										country_name = mapper.env['res.country']
									if 'shipping_state' in type_of_addr:
										state_name = mapper.env['res.country.state'].search([('code','=',type_of_addr['shipping_state']),('country_id','=',country_name.id)])
									else:
										state_name = mapper.env['res.country.state']
									shipping_details = {
									'type':'delivery',
									# 'name' : shipping['first_name'] or None,
									'street' : type_of_addr['shipping_address_1'] or None,
									'street2' : type_of_addr['shipping_address_2'] or None,
									'city' : type_of_addr['shipping_city'] or None,
									'state_id': state_name.id or None,
									'zip' : type_of_addr['shipping_postcode'] or None,
									'country_id' : country_name.id or None,
									}
									wp_child_ids.append([0,0,shipping_details])
			vals={
			'name' : res['data']['customer_details']['username'],
			'backend_id' : [[6,0,[backend.id]]],
			'first_name' : res['data']['customer_details']['first_name'],
			'last_name' : res['data']['customer_details']['last_name'],
			'email' : res['data']['customer_details']['email'],
			'street' : contact['address_1'] or None,
			'street2' : contact['address_2'] or None,
			'city' : contact['city'] or None,
			'state_id' : bill_state_id.id or None,
			'zip' : contact['postcode'] or None,
			'country_id' : bill_country_id.id or None,
			'child_ids' : wp_child_ids or None,
			# 'child_ids' : [[0,0,shipping_details]] or None,
			'phone' : contact['phone'] or None,
			# 'jacket' : res['data']['jacket'] or None,
			# 'helmet' : res['data']['helmet'] or None,
			# 'pants' : res['data']['pants'] or None,
			# 'gloves' : res['data']['gloves'] or None,
			# 'rewards' : res['data']['rewards'] or None,
			# 'licence_no' : res['data']['license_number'] or None,
			}
			# if(status==True) and (sale_id or repair_order or ride_id):
			# 	if sale_id:
			# 		return sale_id.partner_id
			# 	elif repair_order:
			# 		return repair_order.partner_id
			# 	elif ride_id:
			# 		return ride_id.partner_id
			res_partner = mapper.customer_id.create(vals)
			return res_partner

	def write_customer(self,backend,mapper,res):
		bkend_id = mapper.backend_id.search([('id','=',backend.id)])
		contact = res['data']['customer_details']['billing']
		shipping = res['data']['customer_details']['shipping']
		metadata = res['data']['customer_details']['meta_data']
		wp_child_ids = []

		shipping_details = self.get_shipping(mapper, shipping)
		wp_child_ids.append([6,0,shipping_details])

		bill_country_id = mapper.env['res.partner'].country_id.search([('code','=',shipping['country'])]) 
		bill_state_id =	mapper.env['res.partner'].state_id.search([('code','=',shipping['state']),('country_id','=',bill_country_id.id)])		

		# ride_details = res['data']['my_rides']
		# rides_list = []
		# ride_id = None
		# for ride in ride_details:
		# 	ride_id = mapper.env['wordpress.odoo.majorunit'].search([('backend_id','=',backend.id),('woo_id','=',ride)]).majorunit_id
		# 	if ride_id:
		# 		pass
		# 	else:
		# 		major_unit = mapper.env['major_unit.major_unit']
		# 		major_unit.single_importer(backend,ride)
		# 		ride_id = mapper.env['wordpress.odoo.majorunit'].search([('backend_id','=',backend.id),('woo_id','=',ride)]).majorunit_id
		# 		rides_list.append([6,0,ride_id.ids])

		# service_rides = res['data']['my_services']
		# service_list = []
		# repair_order = None
		# for order in service_rides:
		# 	repair_order = mapper.env['wordpress.odoo.service.repair_order'].search([('backend_id','=',backend.id),('woo_id','=',order)]).service_rides_id
		# 	if repair_order:
		# 		pass
		# 	else:
		# 		repair_order_id = mapper.env['service.repair_order']
		# 		repair_order_id.single_importer(backend,order)
		# 		repair_order = mapper.env['wordpress.odoo.service.repair_order'].search([('backend_id','=',backend.id),('woo_id','=',order)]).service_rides_id
		# 		service_list.append([6,0,repair_order.ids])

		sale_orders = res['data']['order_ids']
		sales_list = []
		sale_id = None
		for sale in sale_orders:
			sale_id = mapper.env['wordpress.odoo.sale.order'].search([('backend_id','=',backend.id),('woo_id','=',sale)]).order_id
			if sale_id:
				pass
			else:
				sale_order = mapper.env['sale.order']
				sale_order.single_importer(backend,sale)
				sale_id = mapper.env['wordpress.odoo.sale.order'].search([('backend_id','=',backend.id),('woo_id','=',sale)]).order_id
				sales_list.append([6,0,sale_id.ids])

		# for addr in metadata:
		# 	for type_of_addr in addr['value']:
		# 		if 'type' in type_of_addr:
		# 			if type_of_addr['type'] == 'billing':
		# 				country_name = mapper.env['res.country'].search([('code','=',type_of_addr['billing_country'])])
		# 				state_name = mapper.env['res.country.state'].search([('code','=',type_of_addr['billing_state']),('country_id','=',country_name.id)])
		# 				shipping_details = {
		# 				'type':'invoice',
		# 				# 'name' : type_of_addr['billing_first_name'] or None,
		# 				'street' : type_of_addr['billing_address_1'] or None,
		# 				'street2' : type_of_addr['billing_address_2'] or None,
		# 				'city' : type_of_addr['billing_city'] or None,
		# 				'state_id': state_name.id or None,
		# 				'zip' : type_of_addr['billing_postcode'] or None,
		# 				'country_id' : country_name.id or None,
		# 				}
		# 				wp_child_ids.append([6,0,shipping_details])
		# 			elif type_of_addr['type'] == 'shipping':
		# 				country_name = mapper.env['res.country'].search([('code','=',type_of_addr['shipping_country'])])
		# 				state_name = mapper.env['res.country.state'].search([('code','=',type_of_addr['shipping_state']),('country_id','=',country_name.id)])
		# 				shipping_details = {
		# 				'type':'delivery',
		# 				# 'name' : shipping['first_name'] or None,
		# 				'street' : type_of_addr['shipping_address_1'] or None,
		# 				'street2' : type_of_addr['shipping_address_2'] or None,
		# 				'city' : type_of_addr['shipping_city'] or None,
		# 				'state_id': state_name.id or None,
		# 				'zip' : type_of_addr['shipping_postcode'] or None,
		# 				'country_id' : country_name.id or None,
		# 				}
		# 				wp_child_ids.append([6,0,shipping_details])

		vals={
		'name' : res['data']['customer_details']['username'],
		'backend_id' : [[6,0,[backend.id]]],
		'first_name' : res['data']['customer_details']['first_name'],
		'last_name' : res['data']['customer_details']['last_name'],
		'email' : res['data']['customer_details']['email'],
		'street' : contact['address_1'] or None,
		'street2' : contact['address_2'] or None,
		'city' : contact['city'] or None,
		'state_id' : bill_state_id.id or None,
		'zip' : contact['postcode'] or None,
		'country_id' : bill_country_id.id or None,
		'child_ids' : [[6,0,mapper.customer_id.child_ids.ids]] or None,
		# 'child_ids' : wp_child_ids or None,
		'phone' : contact['phone'] or None,
		# 'jacket' : res['data']['jacket'] or None,
		# 'helmet' : res['data']['helmet'] or None,
		# 'pants' : res['data']['pants'] or None,
		# 'gloves' : res['data']['gloves'] or None,
		# 'licence_no' : res['data']['license_number'] or None,
		# 'customer_vehicles' : [[6,0,mapper.customer_id.customer_vehicles.ids]],
		# 'customer_ride_service' : [[6,0,mapper.customer_id.customer_ride_service.ids]],
		# 'customer_product_ids' : [[6,0,mapper.customer_id.customer_product_ids.ids]]
		}

		mapper.customer_id.write(vals) 

	def get_shipping(self,mapper,shipping):
		ship_country_id = mapper.env['res.partner'].country_id.search([('code','=',shipping['country'])]) 
		ship_state_id =	mapper.env['res.partner'].state_id.search([('code','=',shipping['state']),('country_id','=',ship_country_id.id)])
		
		shipping_details = {
		'type':'delivery',
		# 'name' : shipping['first_name'] or None,
		'street' : shipping['address_1'] or None,
		'street2' : shipping['address_2'] or None,
		'city' : shipping['city'] or None,
		'state_id': ship_state_id.id or None,
		'zip' : shipping['postcode'] or None,
		'country_id' : ship_country_id.id or None,
		}

		return shipping_details