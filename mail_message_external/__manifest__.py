# -*- coding: utf-8 -*-
# Copyright 2014 Eficent (<http://www.eficent.com/>)
#             <contact@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "External Mail Message",
    "version": "10.0.1.0.0",
    "author": "Eficent",
    "category": "Social Network",
    "summary": "Create an External Mail Message entity",
    "website": "https://www.github.com/Eficent/mailbox_replica/tree/10.0",
    "license": "AGPL-3",
    "depends": ['mail'],
    "data": [
        'security/ir.model.access.csv',
        'views/mail_message_external_view.xml'
    ],
    "installable": True,
}
