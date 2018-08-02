# -*- coding: utf-8 -*-
# Copyright 2015 Eficent (<http://www.eficent.com/>)
#             <contact@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class FetchMailServer(models.Model):
    _inherit = 'fetchmail.server'

    def _get_current_user(self):
        return self._uid

    user_id = fields.Many2one(
        comodel_name='res.users', string='Owner', default=_get_current_user)

    _sql_constraints = [
        ('fetchmail_user_uniq', 'unique(user_id)', 'That user already has a '
                                                   'Fetchmail server.'),
    ]
