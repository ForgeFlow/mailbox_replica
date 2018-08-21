# -*- coding: utf-8 -*-
# Copyright 2014 Eficent (<http://www.eficent.com/>)
#             <contact@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.tools.mail import html2plaintext


class MailMessageExternal(models.Model):
    _name = 'mail.message.external'
    _description = 'External Mail Message'
    _inherit = ['mail.thread']

    name = fields.Char(string='Subject', size=64, required=True, index=1)
    description = fields.Text(string='Notes')
    email_from = fields.Char('Email From', size=128, help="From", index=1)
    email_to = fields.Char(string='Email To', size=252, help="To", index=1)
    email_cc = fields.Text(string='CC', size=252,
                           help="These email addresses will be "
                                "added to the CC field of all inbound "
                                "and outbound emails for this record "
                                "before being sent. "
                                "Separate multiple email addresses with a "
                                "comma")
    create_date = fields.Datetime(string='Creation Date', readonly=True)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner',
                                 ondelete='set null',
                                 index=1,
                                 help="Linked partner (optional).")

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        if custom_values is None:
            custom_values = {}
        desc = html2plaintext(msg_dict.get('body')) if msg_dict.get('body') \
            else ''
        defaults = {
            'name':  msg_dict.get('subject') or _("No Subject"),
            'description': desc,
            'email_from': msg_dict.get('from'),
            'email_to': msg_dict.get('to'),
            'email_cc': msg_dict.get('cc'),
            'partner_id': msg_dict.get('author_id', False),
            'user_id': False,
        }
        defaults.update(custom_values)
        return super(MailMessageExternal, self).message_new(
            msg_dict=msg_dict, custom_values=defaults)
