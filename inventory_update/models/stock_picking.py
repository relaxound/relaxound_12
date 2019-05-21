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
from pandas.io.common import EmptyDataError

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
				#print(name + ' - ' + str(time))

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
		print(model)

		product_id_list=[]
		single_product=[]
		list_for_multiple=[]
		use_dict={}

		latest_one = self._sort_data(cwd,ftp)

		localfile = open("/home/saurajchopade/Relex_Sound/"+latest_one, 'wb')

		ftp.retrbinary('RETR '+ftp.pwd()+"/"+latest_one,localfile.write)
		# ftp.close()
		localfile.close()

	
		df = pd.read_csv("/home/saurajchopade/Relex_Sound/"+latest_one,sep=';')
		

		SKU = df['SKU']
		stock= df['stock']
		dict1={}

		### user id  
		common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url),allow_none=True)
		uid = common.login(db, username, password)
		print(uid)
		print(common.version())

		#print(SKU)

		for i,s in zip(SKU,stock):
			#print(i)	
			ids= model.execute(db,uid,password,'product.product','search',[['default_code','=',i]])
			if(len(ids)==0):
				print(ids,"not available",s)
			else:
				if(len(ids)>1):
					for k in ids:
						dict1.update({k:s})
						print(k,s)
				else:
					if(s==0 or self.isnegative(s)):
						pass
					else:			
						dict1.update({ids[0]:s}) # ids of product with stock to update
						print(ids)

		date_time = current_date.strftime("%m-%d-%Y %H.%M.%S")
		print("date and time:",date_time)

		id2= model.execute(db,uid,password,'stock.inventory','create',
			[{'name':"PRODUCT_DEMO"+date_time,'filter':'partial','company_id':1,
				'state':'draft','location_id':250 }])	


		
		for id1,stock_qty in dict1.items():
			#print(id1,stock_qty) 
			# pdb.set_trace()	
			dc = model.execute(db,uid,password,'product.product','search_read',[['type','=','product'],['id','=',id1]])
			if(len(dc)==0):
				print(id1,stock_qty)
			
			else:
				id12 = dc[0]['id']
				company_id = dc[0]['company_id'][0]
				name = dc[0]['name']
				use_dict.update({id12:stock_qty})


				



		for id12,stock_qty in use_dict.items():
			dc = model.execute(db,uid,password,'product.product','search_read',[['type','=','product'],['id','=',id12]])
			if(dc[0]['qty_at_date']!=0):
				model.execute(db,uid,password,'stock.inventory.line','create',	
				[{'inventory_id': id2[0],'product_id': id12,'location_id': 29,'product_qty': float(stock_qty)+dc[0]['qty_at_date']}])

			else:
				print(id12)
				print(id12,stock_qty)
				model.execute(db,uid,password,'stock.inventory.line','create',	
				[{'inventory_id': id2[0],'product_id': id12,'location_id': 29,'product_qty': stock_qty}])

		# id2_list=[]
		# id2_list.append(id2)

		
		inv_create = model.execute(db,uid,password,'stock.inventory','action_start',id2)
		try:
			inv = model.execute(db,uid,password,'stock.inventory','action_validate',id2)
		except Exception as e:
			print("done")