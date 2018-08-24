# -*- coding: utf-8 -*-
{
    'name': 'Mail Move Message',
    'version': '10.0.1.0.0',
    'summary': 'Relocate customer\'s mails to a correct place'
               ' (lead, task, etc.)',
    'author': 'IT-Projects LLC, Ivan Yelizariev, Pavel Romanchenko',
    'license': 'LGPL-3',
    'category': 'Discuss',
    'images': ['images/m1.png'],
    'website': 'https://www.github.com/Eficent/mailbox_replica/tree/10.0',
    'depends': ['mail_all', 'web_polymorphic_selection'],
    'data': [
        'views/mail_move_message_views.xml',
        'data/mail_move_message_data.xml',
    ],
    'qweb': [
        'static/src/xml/mail_move_message_main.xml',
    ],
    'installable': True,
}
