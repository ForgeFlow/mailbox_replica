# -*- coding: utf-8 -*-
{
    'name': 'Check Mail Immediately',
    'summary': 'Keep your inbox up to date',
    'version': '10.0.1.0.0',
    'author': 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'LGPL-3',
    'category': 'Discuss',
    'website': 'https://github.com/Eficent/mailbox_replica/tree/10.0',
    'depends': ['base', 'web', 'fetchmail', 'mail'],
    'data': [
        'views/views.xml',
    ],
    'qweb': [
        "static/src/xml/main.xml",
    ],
    'installable': True,
}
