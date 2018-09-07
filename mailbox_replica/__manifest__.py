# -*- coding: utf-8 -*-
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mail Replica',
    'version': '10.0.1.0.0',
    'category': 'Mail',
    "license": "AGPL-3",
    'depends': [
        'fetchmail_server_per_user',
        'smtp_per_user',
        'mail_message_external',
        'mail_log_message_to_process',
        'partner_mail_message_view',
        'fetchmail_fetch_missing',
        'mail_create_partner',
        'mail_all',
        'web_polymorphic_selection',
    ],
    'author': 'Eficent',
    'summary': """
      Mailbox replica app
""",
    'installable': True,
    'application': True,
}
