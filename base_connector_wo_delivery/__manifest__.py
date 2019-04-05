{
    "name": "Base Connector (No Delivery)",
    "version": "1.0",
    "depends": ["base","product","sale","stock","sale_management"],
    "author": "Level9",
    "category": "Custom Development",
    "description": """    
    """,
    "init_xml": [],
    'data': [
            'connector_view.xml',
            'product/product_view.xml',
            'sale_import_error/sale_import_error_view.xml',
            'security/ir.model.access.csv'
            ],
    'demo_xml': [],
    'installable': True,
    'active': False,
#    'certificate': 'certificate',
}
