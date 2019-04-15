from odoo import api, fields, models,_

class ProductVideo(models.Model):
	_name = 'product.videos'
	_inherits = {'product.attribute.value': 'value_ids'}

	name=fields.Char(string="Name")
	details=fields.Selection([('tires', 'Tires')], string="Details")
	video_url_name=fields.Text(string="Video Url")
	video_preview=fields.Text(related="video_url_name",string="Preview")