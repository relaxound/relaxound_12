import requests
import logging
from ..model.api import API
from datetime import datetime
from datetime import timedelta
from ..unit.backend_adapter import WpImportExport
_logger = logging.getLogger(__name__)

class WpTaxImport(WpImportExport):
	""" Models for woocommerce tax import """
	def get_api_method(self, method, args, count=None, date=None):
		""" get api for tax"""
		api_method = None
		# print (str(args[0]['id']))
		if method == 'taxes':
			if not args[0]:
				api_method = 'taxes'
			else:
				api_method = 'taxes/' + str(args[0]['id'])
		return api_method

	def import_tax(self, method, arguments):
		"""Import tax data"""
		_logger.debug("Start calling Woocommerce api %s", method)
		result = {}

		res = self.importer(method, arguments)
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

	def create_tax(self,backend,mapper,res,status=True):
		if (res['status'] == 200 or res['status'] == 201):
			vals={
				'name' : res['data']['name'] + " " + str(res['data']['id']),
				'backend_id' : [[6,0,[backend.id]]],
				'tax_class' : res['data']['class'],
				'amount' : res['data']['rate'],
				# 'country_id.name' : res['data']['country'] ,
				# 'state_id.name' : res['data']['state'],
				'postcode' : res['data']['postcode'],
				'city' : res['data']['city'],
				'priority' : res['data']['priority'],
				'compound' : res['data']['compound'],
				'shipping' : res['data']['shipping'],
				'order' : res['data']['order'],
			}
			account_tax = mapper.tax_id.create(vals)
			return account_tax

	def write_tax(self,backend,mapper,res):
		# bkend_id = mapper.backend_id.search([('id','=',backend.id)])
		vals={
			'name' : res['data']['name'] + " " + str(res['data']['id']),
			'backend_id' : [[6,0,[backend.id]]],
			'tax_class' : res['data']['class'],
			'amount' : res['data']['rate'],
			# 'country_id' : res['data']['country'] ,
			# 'state_id' : res['data']['state'],
			'postcode' : res['data']['postcode'],
			'city' : res['data']['city'],
			'priority' : res['data']['priority'],
			'compound' : res['data']['compound'],
			'shipping' : res['data']['shipping'],
			'order' : res['data']['order'],
			}
		_logger.info(vals)
		mapper.tax_id.write(vals) 