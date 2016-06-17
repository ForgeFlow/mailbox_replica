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
    'name': 'Mail Fetchmail Server SMTP',
    'category': 'Mail',
    'description': "Configure Fetchmail server from Mail.",
    'author': 'Eficent',
    'license': 'AGPL-3',
    'website': 'http://eficent.com',
    'version': '7.0.0.1.0',
    'sequence': 10,
    'depends': [
                'base',
                'mail',
                'fetchmail',
                'tko_mail_smtp_per_user'
                ],
    'data': [
             'views/ir_mail_server_view.xml',
             ],
    'init': [],
    'demo': [],
    'update': [],
    'test': [],  # YAML files with tests
    'installable': True,
    'application': False,
    'auto_install': False,  # If it's True, the modules will be auto-installed when all dependencies are installed
    'certificate': '',
}
