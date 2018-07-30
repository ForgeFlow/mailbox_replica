# -*- coding: utf-8 -*-
# Copyright 2016-18 Eficent (<http://www.eficent.com/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.mail import email_split


class MailCreatePartnerWizard(models.TransientModel):
    _name = 'mail_create_partner.wizard'

    @api.model
    def default_get(self, fields_list):
        res = super(MailCreatePartnerWizard, self).default_get(fields_list)
        if 'default_message_id' in self._context:
            message = self.env['mail.message'].browse(
                self._context['default_message_id'])
            res['can_create_partner'] = not message.author_id
            res['partner_id'] = message.author_id.id
            email_from = message.email_from
            if email_from:
                parts = email_split(email_from.replace(' ', ','))
                if parts:
                    email = parts[0]
                    name = email_from[:email_from.index(email)].replace(
                        '"', '').replace('<', '').strip() or email_from
                else:
                    name, email = email_from
                res['message_name_from'] = name
                res['message_email_from'] = email
        return res

    @api.multi
    def _compute_can_create_partner(self):
        # message was not moved before OR message is a top message of
        # previous move
        res = {}
        for record in self:
            res[record.id] = not record.message_id.author_id
        return res

    message_id = fields.Many2one(comodel_name='mail.message',
                                 string='Message')
    message_body = fields.Html(related='message_id.body',
                               string='Message to move', readonly=True)
    can_create_partner = fields.Boolean(compute='_compute_can_create_partner',
                                        string='Can move')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Author')
    message_email_from = fields.Char('Email From')
    message_name_from = fields.Char('Name From')

    def create_partner(self, message_id):
        message = self.env['mail.message'].browse(message_id)
        email_from = message.email_from
        message_name_from = False
        message_email_from = False
        partner_id = False
        if email_from:
            parts = email_split(email_from.replace(' ', ','))
            if parts:
                email = parts[0]
                name = email_from[:email_from.index(email)].\
                    replace('"', '').replace('<', '').strip() or email_from
            else:
                name, email = email_from
            message_name_from = name
            message_email_from = email
        if message_name_from:
            self._context.update({'update_message_author': True})
            partner_id = self.env['res.partner'].create({
                'name': message_name_from,
                'email': message_email_from,
            })
        context = {'partner_id': partner_id}

        return context


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        res_id = super(Partner, self).create(vals).id
        if 'update_message_author' in self._context and 'email' in vals:
            mail_message_obj = self.env['mail.message']
            # Escape special SQL characters in email_address to
            # avoid invalid matches
            email_address = (vals['email'].replace('\\', '\\\\').
                             replace('%', '\\%').replace('_', '\\_'))
            email_brackets = "<%s>" % email_address
            messages = mail_message_obj.search([
                '|', ('email_from', '=ilike', email_address),
                ('email_from', 'ilike', email_brackets),
                ('author_id', '=', False),
            ])
            if messages:
                messages.write({'author_id': res_id})
        return res_id
