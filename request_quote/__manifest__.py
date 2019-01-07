# -*- coding: utf-8 -*-
{
    'name': "Website Product Quotation",

    'summary': """
        Creates Leads and Quotation from website shop with product details.
        """,

    'description': """
        Allowes the user to send quotion for a product from website which creates lead in backend.
        Allowes sales person to generate lead with product lines.
    """,
    'price': 49.00,
    'currency': 'EUR',
    'author': "Techspawn Solutions",
    'website': "http://www.techspawn.com",
    'images': ['static/description/main.jpg'],
    'license':'OPL-1',
    'category': 'Sale/Crm',
    'version': '1.1',

    'depends': ['base','crm', 'sale', 'sale_management', 'sale_crm', 'website_sale','website_form','uom'],


    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/quote_view.xml',
    ],

    "installable": True,
}