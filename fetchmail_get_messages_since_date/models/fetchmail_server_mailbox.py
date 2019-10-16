# -*- coding: utf-8 -*-

from odoo import fields, models


class FetchMailServerMailbox(models.Model):
    _name = 'fetchmail.server.mailbox'
    _rec_name = 'path'

    path = fields.Char(
        'Path', size=256,
        help='The path to your mail '"folder. Typically "
             "would be something like 'INBOX.myfolder'", required=True)
    server_id = fields.Many2one('fetchmail.server', 'Server')


class FetchMailServerMailboxPath(models.Model):
    _name = 'fetchmail.server.mailbox.path'

    server_id = fields.Many2one('fetchmail.server', 'Server')
