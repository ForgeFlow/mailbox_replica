# -*- coding: utf-8 -*-
# Copyright 2015 Eficent (<http://www.eficent.com/>)
#             <contact@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Fetchmail Server Per User',
    'category': 'Mail',
    'summary': "Configure one fetchmail server account by user",
    'author': 'Eficent',
    'license': 'AGPL-3',
    'website': 'http://eficent.com',
    'version': '10.0.1.0.0',
    'depends': [
        'mail', 'fetchmail',
    ],
    'data': [
        'security/fetchmail_server_per_user.xml',
        'security/ir.model.access.csv',
        'views/res_users_view.xml',
        'views/fetchmail_server_view.xml',
    ],
    'installable': True,
}
