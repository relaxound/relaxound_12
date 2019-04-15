import logging
from ..model.api import API
from datetime import datetime
from datetime import timedelta
from ..unit.backend_adapter import WpImportExport
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class ServiceOrderExport(WpImportExport):

    """ Models for woocommerce service export """

    def get_api_method(self, method, args):
        """ get api for service"""
        api_method = None

        if method == 'my_services':
            if not args[0]:
                api_method = 'my_services/details'
            else:
                api_method = 'my_services/details/' + str(args[0])
        return api_method

    def get_standard_job(self, standard_job_ids):
        standard_job = []
        #If there are multiple std_jobs then for dynamic quantity,
        #first we have to add quantity of job
        if standard_job_ids:
            for standard_job_id in standard_job_ids:
                standard_job.append({
                    "id": standard_job_id.id or None,
                    "qty": 1.0,
                })
            # return standard_job[0]
        return standard_job

    def get_pickup_address(self, pickup_ids):
        """ return shipping address od customer """

        pickup = []
        if pickup_ids:
            for pickup_id in pickup_ids:
                if pickup_id.process_type == 'pickup':
                    pickup.append({
                        "sa_add_LineOnePick": pickup_id.street or None,
                        "sa_add_LineTwoPick": pickup_id.street2 or None,
                        "sa_cityPick": pickup_id.city or None,
                        "sa_statePick": pickup_id.state_id.code or None,
                        "sa_zipPick": pickup_id.zip or None,
                        "type": pickup_id.process_type or None,
                        "sa_specialInstructionsPick": pickup_id.note or None,
                        "sa_preferredTimePick": pickup_id.preferred_time or None,
                    })
                elif pickup_id.process_type == 'delivery':
                    pickup.append({
                        "sa_add_LineOneDelivery": pickup_id.street or None,
                        "sa_add_LineTwoDelivery": pickup_id.street2 or None,
                        "sa_cityDelivery": pickup_id.city or None,
                        "sa_stateDelivery": pickup_id.state_id.code or None,
                        "sa_zipDelivery": pickup_id.zip or None,
                        "type": pickup_id.process_type or None,
                        "sa_specialInstructionsDelivery": pickup_id.note or None,
                        "sa_preferredTimeDelivery": pickup_id.preferred_time or None,
                    })
        return pickup

    def get_suggested_job(self, suggested_job_ids):
        suggested_job = []
        if suggested_job_ids:
            for suggested_job_id in suggested_job_ids:
                suggested_job.append({
                    "name": suggested_job_id.standard_job_id.name or None,
                    "sequence": suggested_job_id.sequence or None,
                    "repair_order": suggested_job_id.repair_order_id.name or None,
                    "state": suggested_job_id.state or None,
                    "taxes_id": suggested_job_id.taxes_id or None,
                    "qty_available": suggested_job_id.qty_available or None,
                    "product_id": suggested_job_id.product_id.id or None,
                    "price": suggested_job_id.price or None,
                    "unit_price": suggested_job_id.unit_price or None,
                    "quantity": suggested_job_id.quantity or None,
                })
        return suggested_job

    def get_products(self, product_ids):
        products = []
        if product_ids:
            for product_id in product_ids:
                products.append({
                    "name": product_id.standard_job_id.name or None,
                    "sequence": product_id.sequence or None,
                    "repair_order": product_id.repair_order_id.name or None,
                    "state": product_id.state or None,
                    "taxes_id": product_id.taxes_id.id or None,
                    "qty_available": product_id.qty_available or None,
                    "product_id": product_id.product_id.id or None,
                    "price": product_id.price or None,
                    "unit_price": product_id.unit_price or None,
                    "quantity": product_id.quantity or None,
                    "standard_job_type": product_id.standard_job_id.standard_job_type or None,

                }),
        return products

    def get_product_inspection(self, product_inspection_ids):
        product_inspection = []
        if product_inspection_ids:
            for product_inspection_id in product_inspection_ids:
                product_inspection.append({
                    "name": product_inspection_id.name or None,
                })
            return product_inspection[0]
        return product_inspection

    def get_loaner_product(self, loaner_product_ids):

        loaner_product = []
        cr_make = None
        cr_year = None
        cr_type = None
        cr_model = None
        if loaner_product_ids:
            for loaner_product_id in loaner_product_ids:
                for loan in loaner_product_ids.attribute_value_ids:
                    if loan.attribute_id.name.lower() == 'make':
                        cr_make = loan.name
                    elif loan.attribute_id.name.lower() == 'year':
                        cr_year = loan.name
                    elif loan.attribute_id.name.lower() == 'model':
                        cr_model = loan.name
                    elif loan.attribute_id.name.lower() == 'type':
                        cr_type = loan.name

                loaner_product.append({
                    "slb_service_id": loaner_product_id.id or None,
                    "slb_name": loaner_product_id.name or None,
                    "product_type": loaner_product_id.details_model or None,
                    "slb_make": cr_make or None,
                    "slb_year": cr_year or None,
                    "slb_type": cr_type or None,
                    "slb_model": cr_model or None,
                })
        return loaner_product

    def export_service_order(self, method, arguments):
        """ Export service data"""
        _logger.debug("Start calling Woocommerce api %s", method)
        customers = []
        if arguments[1].partner_id:
            for customer_id in arguments[1].partner_id:
                mapper = customer_id.backend_mapping.search(
                    [('backend_id', '=', self.backend.id), ('customer_id', '=', customer_id.id)])
                if mapper.woo_id:
                    customers.append(mapper.woo_id)
                else:
                    customer_id.export(self.backend)
                    mapper = customer_id.backend_mapping.search(
                        [('backend_id', '=', self.backend.id), ('customer_id', '=', customer_id.id)])
                    if mapper.woo_id:
                        customers.append(mapper.woo_id)

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

        start_time = None
        end_time = None
        if arguments[1].start_date:
            start_t = datetime.strptime(
                arguments[1].start_date, '%Y-%m-%d %H:%M:%S')
            start_time = start_t.strftime('%H:%M:%S')

        if arguments[1].end_date:
            end_t = datetime.strptime(
                arguments[1].end_date, '%Y-%m-%d %H:%M:%S')
            end_time = end_t.strftime('%H:%M:%S')

        if arguments[1].pickup == True:
            pickup = 1
        elif arguments[1].pickup == False:
            pickup = 0

        if arguments[1].delivery == True:
            delivery = 1
        elif arguments[1].delivery == False:
            delivery = 0

        if arguments[1].loaner == True:
            loaner = 'yes'
        elif arguments[1].loaner == False:
            loaner = 'no'

        if arguments[1].state == 'QUOTE':
            state = -1
        elif arguments[1].state == 'APPROVE':
            state = 0
        elif arguments[1].state == 'PARTS':
            state = 1
        elif arguments[1].state == 'PICKUP':
            state = 2
        elif arguments[1].state == 'INSPECT':
            state = 3
        elif arguments[1].state == 'LIFT':
            state = 4
        elif arguments[1].state == 'TEST':
            state = 7
        elif arguments[1].state == 'COMPLETE':
            state = 8
        elif arguments[1].state == 'DELIVER':
            state = 9
        elif arguments[1].state == 'done':
            state = 10
        elif arguments[1].state == 'CANCEL':
            state = 11          
        if not rides:
            raise UserError("Please Check Make, Year, Model of product")
        result_dict = {
            "service_details": {
                "so_customer_id": customers[0] or None,
                "so_rides_id": rides[0] or None,
                "so_loaner_status": loaner or None,
                "urgency": arguments[1].urgency or None,
                "so_service_type": arguments[1].repair_type or None,
                "so_schedule_date": arguments[1].requested_date or None,
                "so_status_pick_add": pickup or None,
                "so_status_delivery_add": delivery or None,
                "so_service_status": state,
                # "so_service_type": self.get_standard_job(arguments[1].standard_job_ids)['name'],
            },
            "appointment_details": {
                "location": "1" or None,
                "service": "1" or None,
                "worker": "1" or None,
                "date": arguments[1].requested_date or None,
                "start": start_time or None,
                "end": end_time or None,
                "name": arguments[1].partner_id.first_name or arguments[1].user_id.name or None,
                "email": arguments[1].partner_id.email or None,
            },

            "pickup_delivery_details": self.get_pickup_address(arguments[1].product_pickup_ids),
            "so_service_product_details": self.get_standard_job(arguments[1].standard_job_ids),
            "si_product_meta": self.get_products(arguments[1].product_ids),
            "suggested_job_ids": self.get_suggested_job(arguments[1].suggested_job_ids),
            "inspection_ids": self.get_product_inspection(arguments[1].product_inspection_ids),
            # "service_loaner_bikes": self.get_loaner_product(arguments[1].loaner_product_id),
            "si_ro_number": arguments[1].name or None,
            "si_date_in": arguments[1].claim_date or None,
            "si_date_promised": arguments[1].requested_date or None,
            "si_date_closed": arguments[1].done_date or None,
            "si_plate": arguments[1].plate or None,
            "si_miles_in": arguments[1].miles_in or None,
            "si_miles_out": arguments[1].miles_out or None,
            "si_parts_subtotal": arguments[1].amount_total or None,

        }
        print (result_dict)
        r = self.export(method, result_dict, arguments)
        return {'status': r.status_code, 'data': r.json()}
