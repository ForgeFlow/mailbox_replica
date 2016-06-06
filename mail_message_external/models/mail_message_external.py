# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#               <jordi.ballester@eficent.com>
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
from openerp.osv import fields, orm
from openerp.tools import html2plaintext


class MailMessageExternal(orm.Model):
    _name = 'mail.message.external'
    _description = 'External Mail Message'
    _inherit = ['mail.thread']

    _columns = {
        'name': fields.char('Subject', size=64, required=True, select=1),
        'description': fields.text('Notes'),
        'email_from': fields.char(
            'Email From', size=128,
            help="From", select=1),
        'email_to': fields.char(
            'Email To', size=252,
            help="To", select=1),
        'email_cc': fields.text(
            'CC', size=252,
            help="These email addresses will be "
                 "added to the CC field of all inbound "
                 "and outbound emails for this record "
                 "before being sent. "
                 "Separate multiple email addresses with a "
                 "comma"),
        'create_date': fields.datetime('Creation Date', readonly=True),
        'partner_id': fields.many2one('res.partner', 'Partner',
                                      ondelete='set null',
                                      select=True,
                                      help="Linked partner "
                                           "(optional)."),
    }

    def message_new(self, cr, uid, msg, custom_values=None, context=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        if custom_values is None:
            custom_values = {}
        desc = html2plaintext(msg.get('body')) if msg.get('body') else ''
        defaults = {
            'name':  msg.get('subject') or _("No Subject"),
            'description': desc,
            'email_from': msg.get('from'),
            'email_to': msg.get('to'),
            'email_cc': msg.get('cc'),
            'partner_id': msg.get('author_id', False),
            'user_id': False,
        }
        defaults.update(custom_values)
        return super(MailMessageExternal, self).message_new(
            cr, uid, msg, custom_values=defaults,
            context=context)
