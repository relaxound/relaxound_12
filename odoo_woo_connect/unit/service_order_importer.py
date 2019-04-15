import logging
from ..model.api import API
from datetime import datetime
from datetime import timedelta
from ..unit.backend_adapter import WpImportExport
_logger = logging.getLogger(__name__)


class ServiceOrderImport(WpImportExport):

    """ Models for woocommerce service export """

    def get_api_method(self, method, args, date=None, count=None):
        """ get api for service"""
        api_method = None

        if method == 'my_services':
            if not args[0]:
                api_method = 'my_services/details'
            else:
                api_method = 'my_services/details/' + str(args[0])
        return api_method

    def import_service_rides(self, method, arguments):
        """ Import sale order data"""
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

    def create_service_rides(self, backend, mapper, res, partner_id, major_unit):
        if partner_id and major_unit:
            std_job_list = []
            std_jobs_details = res['data']['service_product_details']
            if isinstance(std_jobs_details, dict):
                for key in std_jobs_details:
                    std_job = mapper.env['wordpress.odoo.service.standard_job'].search(
                        [('backend_id','=',backend.id),('woo_id','=',key)])
                    if std_job:
                        std_job_list.append([6,0,std_job.standard_job_id.ids])
            values = {
            'partner_id' : partner_id[0].customer_id.id,
            'backend_id' : [[4,backend.id,backend]],
            'repair_type' : 'repair_order',
            'major_unit_id' : major_unit.majorunit_id.id,
            'standard_job_ids' : std_job_list,
            # 'requested_date' : res['data']['service_details']['so_schedule_date']
            }
            service_rides_id = mapper.service_rides_id.create(values)
            if isinstance(std_jobs_details, dict):
                for key in std_jobs_details:
                    product_list = []
                    std_job = mapper.env['wordpress.odoo.service.standard_job'].search(
                        [('backend_id','=',backend.id),('woo_id','=',key)])
                    if std_job:
                        odoo_std_job = std_job.standard_job_id
                        for job in odoo_std_job:
                            products = odoo_std_job.product_ids
                            for product in products:
                                vals = {
                                    'product_id' : product.product_id.id,
                                    'repair_order_id' : service_rides_id.id
                                }
                                service_rides_id.product_ids.create(vals)

            return service_rides_id

    def write_service_rides(self, backend, mapper, res, partner_id, major_unit):
        if partner_id and major_unit:
            std_job_list = []
            std_jobs_details = res['data']['service_product_details']
            if isinstance(std_jobs_details, dict):
                for key in std_jobs_details:
                    std_job = mapper.env['wordpress.odoo.service.standard_job'].search(
                        [('backend_id','=',backend.id),('woo_id','=',key)])
                    if std_job:
                        std_job_list.append([6,0,std_job.standard_job_id.ids])

            values = {
            'partner_id' : partner_id[0].customer_id.id,
            'backend_id' : [[4,backend.id,backend]],
            'repair_type' : 'repair_order',
            'major_unit_id' : major_unit.majorunit_id.id,
            'standard_job_ids' : std_job_list,
            }
            mapper.service_rides_id.write(values)
            if isinstance(std_jobs_details, dict):
                for key in std_jobs_details:
                    product_list = []
                    std_job = mapper.env['wordpress.odoo.service.standard_job'].search(
                        [('backend_id','=',backend.id),('woo_id','=',key)])
                    if std_job:
                        odoo_std_job = std_job.standard_job_id
                        for job in odoo_std_job:
                            products = odoo_std_job.product_ids
                            for product in products:
                                vals = {
                                    'product_id' : product.product_id.id,
                                    'repair_order_id' : mapper.service_rides_id.id
                                }
                                mapper.service_rides_id.product_ids.write(vals)

            return True
