# -*- coding: utf-8 -*-
# Copyright 2015-18 Eficent (<http://www.eficent.com/>)
#             <contact@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _notify_by_email(self, message, force_send=False,
                         send_after_commit=True, user_signature=True):
        users_with_fetchmail = self.env['res.users'].search(
            [('partner_id', 'in', self.ids)]).filtered(
            lambda u: u.fetchmail_server_id and
                      u.fetchmail_server_id.state == 'done')
        partners = self.filtered(
            lambda p: p not in users_with_fetchmail.mapped('partner_id'))
        return super(Partner, partners)._notify_by_email(
            message=message, force_send=force_send,
            send_after_commit=send_after_commit, user_signature=user_signature)
