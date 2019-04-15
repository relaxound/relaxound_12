import logging

# import xmlrpclib
from collections import defaultdict
from odoo.addons.queue_job.job import job
import base64
from odoo import models, fields, api, _
from ..unit.customer_exporter import WpCustomerExport
from ..unit.customer_importer import WpCustomerImport
from odoo.exceptions import Warning


_logger = logging.getLogger(__name__)


class StockWarehouse(models.Model):
	_inherit = 'stock.warehouse'

	physical_address = fields.Char(string='Physical Address')
