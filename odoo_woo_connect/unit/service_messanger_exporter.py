import logging
from ..model.api import API
from datetime import datetime
from datetime import timedelta
from ..unit.backend_adapter import WpImportExport
_logger = logging.getLogger(__name__)


class WpServiceMessangerExport(WpImportExport):

    """ Models for woocommerce customer export """

    def get_api_method(self, method, args):
        """ get api for customer"""
        api_method = None
        if method == 'alerts_msgs':
            if not args[0]:
                api_method = 'alerts_msgs/details'
            else:
                api_method = 'alerts_msgs/details/' + str(args[0])
        return api_method

    def export_service_messanger(self, method, arguments):
        """ Export customer data"""
        _logger.debug("Start calling Woocommerce api %s", method)
        customer_woo_ids = []
        if arguments[1].customer_id:
            for customer_id in arguments[1].customer_id:
                mapper = customer_id.backend_mapping.search(
                    [('backend_id', '=', self.backend.id), ('customer_id', '=', customer_id.id)])
                if mapper.woo_id:
                    customer_woo_ids.append(mapper.woo_id)
                else:
                    customer_id.export(self.backend)
                    mapper = customer_id.backend_mapping.search(
                        [('backend_id', '=', self.backend.id), ('customer_id', '=', customer_id.id)]) 
                    if(mapper.woo_id):
                        customer_woo_ids.append(mapper.woo_id)              
        

        rides = []
        if arguments[1].major_unit_id:
            for majorunit_id in arguments[1].major_unit_id:
                mapper = majorunit_id.backend_mapping.search(
                    [('backend_id', '=', self.backend.id), ('majorunit_id', '=', majorunit_id.id)])
                if mapper.woo_id:
                    rides.append(mapper.woo_id)
                else:
                    majorunit_id.export(self.backend)
                    mapper = majorunit_id.backend_mapping.search(
                        [('backend_id', '=', self.backend.id), ('majorunit_id', '=', majorunit_id.id)])
                    if mapper.woo_id:
                        rides.append(mapper.woo_id)

        result_dict = {
            "customer_id": customer_woo_ids[0] or None,
            "Title": arguments[1].name or None,
            "Description": arguments[1].description or None,
            "Phone": arguments[1].phone or None,
            "Email": arguments[1].email or None,
            "state_type": arguments[1].state_type or None,
            "store_name": arguments[1].store_name or None,
            "Logo": arguments[1].logo_image or None,
            "major_unit_id": rides[0] or None,

        }
        r = self.export(method, result_dict, arguments)
        return {'status': r.status_code, 'data': r.json()}
