# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#             <contact@eficent.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
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
    'name' : 'Mail keep recipients',
    'version' : '1.0.0',
    'author' : 'Eficent',
    'category' : 'Social Network',
    'website' : 'www.eficent.com',
    'description': """
Allows to store recipients of the mail. When they are being sent. If the
send process fails, after re-trying to send the recipients will be included
in the notification again.
    """,
    'depends' : ['mail'],
    'data':[
        'views/mail_mail_view.xml',
    ],
    'installable': True
}
