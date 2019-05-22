from odoo import models,fields,api,exceptions,tools
import os
from ftplib import FTP
import logging
import pandas as pd
from dateutil import parser
from xmlrpc import client as xmlrpclib
import pdb
from ftplib import FTP
import time
from dateutil import parser

_logger = logging.getLogger(__name__)

class stockpicking(models.Model):
	_inherit="stock.picking"

	def isnegative(self,s):
		if(s<0):
			return True	
		return False

	def _sort_data(self,cwd,ftp):
			files = ftp.mlsd("/"+cwd)
			dict1={}

			for file in files:
				name = file[0]
				timestamp = file[1]['modify']
				time = parser.parse(timestamp)
				

			if(file[1]['type']=="dir"):
				pass
			else:
				dict1.update({time:name})
		

			max1=max(dict1)
			file_name = dict1.get(max1)
			return file_name

	def _import_inventory_(self): 
		db="relaxound-relaxound-12-test-master-new-405959"  # main stage
		username="rahelheuser@zwitscherbox.com"
		password="let/s1_smile"
		url = "https://relaxound-relaxound-12-test-master-new-405959.dev.odoo.com" # main stage

		ftp = FTP("62.214.48.227")
		ftp.login('relaxound', 'qOIg7W1Cic1vSNU')
		ftp.cwd('STOCK')
		print("connect")

		cwd="STOCK"

		current_date = fields.Datetime.now()

		model = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url),allow_none=True)
		

		product_id_list=[]
		single_product=[]
		list_for_multiple=[]
		use_dict={}

		latest_one = self._sort_data(cwd,ftp)
		
		localfile = open(latest_one, 'wb')

		ftp.retrbinary('RETR '+ftp.pwd()+"/"+latest_one,localfile.write)
		localfile.close()

	
		df = pd.read_csv(latest_one,sep=';')
			

		SKU = df['SKU']
		stock= df['stock']
		dict1={}

		common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url),allow_none=True)
		uid = common.login(db, username, password)
		_logger.info(uid)

		
		for i,s1 in zip(SKU,stock):
			ids = self.env['product.product'].search([('default_code','=',i)])
			if( not ids):
				pass
			else:
				if(len(ids)>1):
					for i in ids:
						if(i.type=='product'and s1!=0 and s1>0):
							dict1.update({i.id:s1})
						else:
							pass		
				else:			
					if(ids.type =="product" and s1!=0 and s1>0):
							dict1.update({ids.id:s1})
						
					else:
							pass

		date_time = current_date.strftime("%m-%d-%Y %H.%M.%S")
	

		id2= model.execute(db,uid,password,'stock.inventory','create',
			[{'name':"Inventory-Updated-"+date_time,'filter':'partial','company_id':1,
				'state':'draft','location_id':200 }])	

		# for id1,stock_qty in dict1.items():	
		# 	dc = model.execute(db,uid,password,'product.product','search_read',[['type','=','product'],['id','=',id1]])
		# 	if(len(dc)==0):
		# 		pass
			
		# 	else:
		# 		id12 = dc[0]['id']
		# 		company_id = dc[0]['company_id'][0]
		# 		name = dc[0]['name']
		# 		use_dict.update({id12:stock_qty})

		
		for id12,stock_qty in dict1.items():
			dc = model.execute(db,uid,password,'product.product','search_read',[['id','=',id12]])
			stock_ex =dc[0]['qty_at_date']
			if(stock_ex!=0):
				model.execute(db,uid,password,'stock.inventory.line','create',	
				[{'inventory_id': id2[0],'product_id': id12,'location_id': 200,'product_qty': float(stock_qty)+stock_ex}])

			else:
			
				model.execute(db,uid,password,'stock.inventory.line','create',	
				[{'inventory_id': id2[0],'product_id': id12,'location_id': 200,'product_qty': stock_qty}])

		

		
		inv_create = model.execute(db,uid,password,'stock.inventory','action_start',id2)
		try:
			inv = model.execute(db,uid,password,'stock.inventory','action_validate',id2)
		except Exception as e:
			print("done")
