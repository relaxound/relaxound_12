import logging
from ..model.api import API
from datetime import datetime
from datetime import timedelta
from ..unit.backend_adapter import WpImportExport

_logger = logging.getLogger(__name__)


class StandardJobExport(WpImportExport):

    """ Models for woocommerce service export """

    def get_api_method(self, method, args):
        """ get api for service"""
        api_method = None
        if method == 'products':
            if not args[0]:
                api_method = 'products/details'
            else:
                api_method = 'products/details/' + str(args[0])
        return api_method

    def get_bundle_products(self, product_ids):
        products_bundle = []
        counter = 0
        products_id = []
        if product_ids:
            for product_id in product_ids:
                if product_id.product_id.product_variant_count <= 1:
                    product_mapper = product_id.product_id.product_tmpl_id.backend_mapping.search(
                        [('backend_id', '=', self.backend.id), ('product_id', '=', product_id.product_id.product_tmpl_id.id)])
                    if product_mapper:
                        products_id = product_mapper.woo_id
                    else:
                        product_id.product_id.product_tmpl_id.export(
                            self.backend)
                        mapper = product_id.product_id.product_tmpl_id.backend_mapping.search(
                            [('backend_id', '=', self.backend.id), ('product_id', '=', product_id.product_id.product_tmpl_id.id)])
                        if mapper.woo_id:
                            products_id = mapper.woo_id

                else:
                    product_mapper = product_id.product_id.product_tmpl_id.backend_mapping.search(
                        [('backend_id', '=', self.backend.id), ('product_id', '=', product_id.product_id.id)])
                    if product_mapper:
                        products_id = product_mapper.woo_id
                    else:
                        product_id.product_id.product_tmpl_id.export(
                            self.backend)
                        mapper = product_id.product_id.product_tmpl_id.backend_mapping.search(
                            [('backend_id', '=', self.backend.id), ('product_id', '=', product_id.product_id.product_tmpl_id.id)])
                        if mapper.woo_id:
                            products_id = mapper.woo_id

                counter = counter + 1
                products_bundle.append({
                    "product_id": products_id or None,
                    "bp_quantity": product_id.quantity or None,
                    "bundle_order": counter

                }),
        return products_bundle

    def export_standard_job(self, method, arguments):

        """ Export service data"""
        _logger.debug("Start calling Woocommerce api %s", method)

        standard_job_woo_ids = []
        mapper = ''
        if arguments[1].backend_mapping:
            for standard_job_id in arguments[1].backend_mapping:
                mapper = standard_job_id.search(
                    [('backend_id', '=', self.backend.id), ('standard_job_id', '=', arguments[1].id)])
                if mapper.woo_id:
                    standard_job_woo_ids.append(mapper.woo_id)

        if arguments[1].active_job == True and arguments[1].publish_job == True:
            status = "publish"
        else:
            status = "draft"

        if mapper:
            img_id = mapper.std_job_image
        else:
            img_id = ''  
   
        loc_val=[]
        if arguments[1].loc:
            for store in arguments[1].store_location:
                loc_val.append(store)
        if arguments[1].fitment_ids:
            for make in arguments[1].fitment_ids.make_attr_value_id:
                loc_val.append(make)
            for model in arguments[1].fitment_ids.model_attr_value_id:
                loc_val.append(model)
            for year in arguments[1].fitment_ids.year_attr_value_ids:
                loc_val.append(year)
        attributes = []
        for attr in loc_val:
            attributes_value = []
            mapper = attr.attribute_id.backend_mapping.search(
                [('backend_id', '=', self.backend.id), ('attribute_id', '=', attr.attribute_id.id)], limit=1)
            if not mapper.woo_id:
                attr.attribute_id.export(self.backend)
                mapper = attr.backend_mapping.search(
                    [('backend_id', '=', self.backend.id), ('attribute_id', '=', attr.attribute_id.id)], limit=1)

            val_mapper = attr.backend_mapping.search(
                [('backend_id', '=', self.backend.id), ('attribute_value_id', '=', attr.id)], limit=1)
            if not val_mapper.woo_id:
                attr.export(self.backend)
            attributes_value.append(attr.name)

            attributes.append({
                "id": mapper.woo_id or 0,
                "name": attr.attribute_id.name or None,
                "visible": attr.attribute_id.visible,
                "variation": attr.attribute_id.create_variant,
                "options": attributes_value,
            })   
        if arguments[1].standard_job_image:
            src=arguments[1].standard_job_image.decode('utf-8')
        else:
            src=arguments[1].standard_job_image   

        if arguments[1].instruction:
            ins=arguments[1].instruction.decode('utf-8')
        else:
            ins=arguments[1].instruction    

        result_dict = {
            "name": arguments[1].name or None,
            "odoo_warehouse" : arguments[1].warehouse.name or None,
            "part_number":arguments[1].part_number or None,
            "attributes":attributes or '',
            "status": status,
            "type": "yith_bundle",
            "price": str(arguments[1].bundle_amount_total) or None,
            "regular_price": str(arguments[1].bundle_amount_total) or None,
            "description": arguments[1].job_description or None,
            "_yith_wcpb_bundle_data": self.get_bundle_products(arguments[1].product_ids),
            "product_type":"service" or None,
            "service_images":[{
                                'id':img_id,
                                'src':src,
                                'position':0,
                                'name':arguments[1].name
                                }],
            # "service_images_name" : arguments[1].name

        }
        if arguments[1].recall==True:
            result_dict.update({
                "recall":arguments[1].recall,
                "manufacturer":arguments[1].manufacturer,
                "claim_id":arguments[1].claim_id,
                "defect_type":arguments[1].defect_type,
                "defect_group":arguments[1].defect_group,
                "defect_code":arguments[1].defect_code,
                "cause":arguments[1].cause,
                "instruction": ins,
                "product_type":"warranty" or None,
                "attributes":attributes or ''
                })
        print (result_dict)
        r = self.export(method, result_dict, arguments)
        return {'status': r.status_code, 'data': r.json()}
