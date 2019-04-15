##########################################################################
#
#   Copyright (c) 2016-Present Techspawn Solutions Pvt. Ltd.
# (<https://techspawn.com/>)
#
##########################################################################

{
    'name': 'Odoo Woo Connect',
    'version': '11.0.1.0.0',
    'category': 'Custom',
    'sequence': 1,
    # 'price': 249.00,
    # 'currency': 'EUR',
    'images': ['static/description/icon.png'],
    'author': 'Techspawn Solutions Pvt. Ltd.',
    'website': 'http://www.techspawn.com',
    'description': """

Odoo Woocommerce Connect
=========================

This Module will Connect Odoo with Wordpress WooCommerce and synchronise Data.
------------------------------------------------------------------------------


Some of the feature of the module:
--------------------------------------------

  1. Synchronise all the products.

  2. Synchronise all the products attributes.

  3. Synchronise all the categories.

  4. Synchronise all the customers.

  5. Synchronise all the sales orders.

  6. Synchronise all the taxes.



This module works very well with latest version of Wordpress v4.4 or later and WooCommerce v2.6.x or later
----------------------------------------------------------------------------------------------------------
    """,
    'demo_xml': [],
    'update_xml': [],
    'depends': ['base',
                'product',
                'stock',
                'sale',
                'queue_job',
                'major_unit',
                'service',
                'service_messanger',
                'product_deals',
                'sales_reward',
                'credit_application',
                ],

    'data': [
              'security/bridge_security.xml',
              # 'security/ir.model.access.csv',
              'views/wp_bridge_view.xml',
              # 'views/product.xml',
              # 'views/stock_ware.xml',
              'views/sale_order.xml',
              'views/tax.xml',
              # 'views/product_mapping.xml',
              # 'views/product_image_mapping.xml',
              # 'views/product_tag_mapping.xml',
              # 'views/product_coupon_mapping.xml',
              # 'views/product_attribute_mapping.xml',
              # 'views/product_category_mapping.xml',
              # 'views/product_ecomm_category_mapping.xml',
              'views/tax_mapping.xml',
              # 'views/customer_mapping.xml',
              'views/sale_order_mapping.xml',
              'views/invoice_refund_view.xml',
              # 'views/service_rides_mapping.xml',
              # 'views/major_unit_mapping.xml',
              # 'views/major_unit.xml',
              # 'views/service_sync.xml',
              # 'views/pickup_delivery_mapping.xml',
              # 'views/customer.xml',
              # 'views/standard_job_sync.xml',
              # 'views/standard_job_mapping.xml',
              # 'views/jobs.xml',
              # 'views/service_message.xml',
              # 'views/product_deals.xml',
              # 'views/product_deals_mapping.xml',
              # 'views/crm_lead.xml',
              # 'views/crm_lead_mapping.xml',
              'views/sales_order_scheduler.xml',
              # 'views/credit_app_mapping.xml',
              # 'views/mu_product_mapping.xml',
              # 'views/product_video.xml',
              # 'views/form_view.xml',
              # 'views/description_quota.xml',
              # 'data/charges_product_demo.xml',
              'views/sale_settings.xml'

    ],
    'js': [],
    'application': True,
    'installable': True,
    'auto_install': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
