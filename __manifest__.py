{
    'name': 'Zakah Manager',
    'version': '1.0',
    'summary': 'Manage Zakah calculations',
    'category': 'Accounting',
    'author': 'Hafsa Raashid',
    'depends': ['base', 'stock', 'account'],
    'data': [
        'views/zakah_dashboard.xml',
        'reports/zakah_report_template.xml',
        'reports/zakah_report.xml',
        'data/zakah_data.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}