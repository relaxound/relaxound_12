{
    "name": "RS Document Layout",
    "version": "12.0",
    "depends": ["base","sale","sale_management","stock","account","delivery","product_color_field","customer_sequence","fill_pack"],
    "author": "Level9",
    "category": "Custom Development",
    "description": """    
    """,
    'sequence': 150,
    "init_xml": [],
    'data': [
             "data/data.xml",
            "report/inherited_layouts.xml",
            "report/layout_account_invoice.xml",
            "report/layout_sale_order.xml",
            # "report/layout_delivery.xml",
            'report/res_partner.xml',
            "report/layout_purchase.xml",
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
#    'certificate': 'certificate',
}
