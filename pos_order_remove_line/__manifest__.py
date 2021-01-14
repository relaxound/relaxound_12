{
    'name': "POS Order Remove Line",
    'summary': "Add button to remove POS order line.",
    'description': """
    Long description of module's purpose""",
    'author': "Techspawn Solutons",
    'website': "http://www.techspawn.com",

    'category': 'Point of Sale',
    'version': '12.0',
    'depends': ['point_of_sale'],
    'data': [
        'views/assets.xml'
    ],
    'qweb': [
        'static/src/xml/order_line.xml'
    ]
}
