# -*- coding: utf-8 -*-
# Copyright 2016-18 Eficent (<http://www.eficent.com/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Mail Create Partner',
    'version': '10.0.1.0.0',
    'summary': 'Allows to create a partner from an existing message',
    'author': 'Eficent Business and IT Consulting Services S.L.',
    'category': 'Social Network',
    'website': 'https://www.github.com/Eficent/mailbox_replica/tree/10.0',
    'depends': ['mail'],
    'data': [
        'views/mail_create_partner_view.xml',
        'views/mail_create_partner_assets.xml',
        ],
    'js': [
        'static/src/js/mail_create_partner.js',
    ],
    'qweb': [
        'static/src/xml/mail_create_partner_main.xml',
    ],
    'installable': True,
}
