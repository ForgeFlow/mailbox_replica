# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of theh
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Mail Replica',
    'version': '0.1',
    'category': 'Mail',
    'depends': [
        'fetchmail_get_messages_since_date',
        'fetchmail_server_per_user',
        'mail_check_immediately',
        'mail_create_partner',
        'mail_keep_recipients',
        'mail_message_external',
        'mail_move_message',
        'mail_outgoing',
        'mail_sent',
        'mail_server_smtp',
        'res_partner_mail_message_view',
        'tko_mail_smtp_per_user',
        'web_polymorphic_selection',
     ],

    'author': 'Eficent',
    'description': """
      mailbox replica app
""",
    'installable': False,
    'application': True,
}
