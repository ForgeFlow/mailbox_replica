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
from openerp import models, fields

_logger = logging.getLogger(__name__)


class FetchMailServer(models.Model):
    _inherit = 'fetchmail.server'

    def _get_current_user(self, cr, uid, context=None):
        return uid

    user_id = fields.Many2one('res.users', string='Owner', default=_get_current_user)

    _sql_constraints = [
        ('fetchmail_user_uniq', 'unique(user_id)', 'That user already has a '
                                                   'Fetchmail server.'),
    ]
