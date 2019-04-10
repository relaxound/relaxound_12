{
    "name": "RS Document Layout",
    "version": "12.0",
    "depends": ["base","sale","stock","account","product_color_field","l10n_in","sale_payment_method","fill_pack"],
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
            "report/layout_delivery.xml",
            ],
    'demo_xml': [],
    'installable': True,
    'active': False,
#    'certificate': 'certificate',
}