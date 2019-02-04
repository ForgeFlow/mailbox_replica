# -*- coding: utf-8 -*-


{
    'name': 'Fetch mails from IMAP since a date',
    'version': '10.0.1.0.0',
    'summary': """
Fetch emails from IMAP from a specific date.
    """,
    'author': 'Eficent',
    'website': 'http://www.eficent.com',
    "category": "Tools",
    "depends": ['fetchmail'],
    'data': [
        'security/ir.model.access.csv',
        'views/fetchmail_server.xml',
    ],
    'installable': True,
}
