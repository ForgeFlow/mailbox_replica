# -*- coding: utf-8 -*-
from openerp.osv import fields, osv


class MailMessage(osv.Model):
    _inherit = 'mail.message'

    _columns = {
        'attempt_send': fields.integer('Attempt send')
    }
