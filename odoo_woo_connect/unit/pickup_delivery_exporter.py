import logging
from ..model.api import API
from datetime import datetime
from datetime import timedelta
from ..unit.backend_adapter import WpImportExport

_logger = logging.getLogger(__name__)


class PickupExport(WpImportExport):

    """ Models for woocommerce service export """

    def get_api_method(self, method, args):
        """ get api for service"""
        api_method = None
        if method == 'pickup':
            if not args[0]:
                api_method = 'pickup'
            else:
                api_method = 'pickup/' + str(args[0])
        return api_method

    def export_pickup(self, method, arguments):
        """ Export service data"""
        _logger.debug("Start calling Woocommerce api %s", method)
        service_woo_ids = []

        if arguments[1].backend_mapping:
            for service_id in arguments[1].backend_mapping:
                mapper = service_id.search(
                    [('backend_id', '=', self.backend.id), ('service_rides_id', '=', arguments[1].id)])
                if mapper.woo_id:
                    service_woo_ids.append(mapper.woo_id)

        result_dict = {
            "partner_id": arguments[1].partner_id.name or None,
            "order_id": arguments[1].order_id.name or None,
            "vehicle_id": arguments[1].vehicle_id.name or None,
            "technician_id": arguments[1].technician_id.name or None,
            "choose": arguments[1].choose or None,
            "process_type": arguments[1].process_type or None,
            "service_job": arguments[1].service_job or None,
            "distance": arguments[1].distance or None,
            "estimate": arguments[1].estimate or None,
            "pickup_address": {
                "address_1": arguments[1].street or None,
                "address_2": arguments[1].street2 or None,
                "city": arguments[1].city or None,
                "state": arguments[1].state_id.code or None,
                "postcode": arguments[1].zip or None,
                "country": arguments[1].country_id.code or None,
                "mobile": arguments[1].mobile or None,
                "phone": arguments[1].phone or None,
            },

        }

        r = self.export(method, result_dict, arguments)
        return {'status': r.status_code, 'data': r.json()}
