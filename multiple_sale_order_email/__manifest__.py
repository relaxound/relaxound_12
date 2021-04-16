{
    'name': "Multiple Sale Order Email",

    'summary': """Odoo Module Deneme""",

    'description': """

    """,

    'author': "USTA",
    'website': "http://www.techspawn.com",

    'category': 'Test',
    'version': '0.1',

    'depends': ['base', 'sale','base_setup', 'bus', 'web_tour','sales_team', 'payment', 'portal'],

    'data': [
        'views/res_config.xml',
        'wizard/wizard.xml',
    ],

}
