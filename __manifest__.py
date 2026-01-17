{
    'name': 'Zakah Manager',
    'version': '1.0',
    'summary': 'Manage Zakah calculations',
    'category': 'Accounting',
    'author': 'Hafsa Raashid',
    'depends': ['stock', 'account'],
    'data': [
        'views/zakah_dashboard.xml',
        'views/zakah_report_templates.xml',
        'data/zakah_data.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}