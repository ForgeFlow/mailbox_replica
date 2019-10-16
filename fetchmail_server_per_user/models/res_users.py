# Copyright 2015 Eficent (<http://www.eficent.com/>)
#             <contact@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUser(models.Model):
    _inherit = "res.users"

    fetchmail_server_id = fields.One2many(
        comodel_name="fetchmail.server",
        inverse_name="user_id",
        string="Fetchmail Server",
    )
