# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
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
import logging
from openerp.osv import fields, orm, osv


_logger = logging.getLogger(__name__)


class MailDeliveryException(osv.except_osv):
    """Specific exception subclass for mail delivery errors"""
    def __init__(self, name, value):
        super(MailDeliveryException, self).__init__(name, value)


class IrMailServer(orm.Model):
    _inherit = 'ir.mail_server'

    def send_email(
            self, cr, uid, message, mail_server_id=None, smtp_server=None,
            smtp_port=None, smtp_user=None, smtp_password=None,
            smtp_encryption=None, smtp_debug=False, context=None):
        try:
            super(IrMailServer, self).send_email(
                cr, uid, message, mail_server_id, smtp_server, smtp_port,
                smtp_user, smtp_password, smtp_encryption, smtp_debug, context)

        except MailDeliveryException:

            default_attempt_send = self.pool.get(
                'ir.config_parameter').get_param(
                cr, uid, 'mail_attempt_send', default=5)
            if message.state == 'exception':
                if message.attempt_send < int(default_attempt_send):
                    message.attempt_send += 1
