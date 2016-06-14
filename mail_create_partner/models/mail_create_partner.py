from openerp.osv import fields, osv
from openerp import SUPERUSER_ID
from openerp.tools import email_split
from openerp import models

class MailCreatePartnerWizard(osv.osv_memory):
    _name = 'mail_create_partner.wizard'

    def default_get(self, cr, uid, fields_list, context=None):
        res = super(MailCreatePartnerWizard, self).default_get(cr, uid,
                                                               fields_list,
                                                               context=context)
        if 'default_message_id' in context:
            message = self.pool['mail.message'].browse(
                cr, uid, context['default_message_id'], context=context)
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

    def _get_can_create_partner(self, cr, uid, ids, name, args, context=None):
        # message was not moved before OR message is a top message of
        # previous move
        res = dict.fromkeys(ids, False)
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = not record.message_id.author_id
        return res

    _columns = {
        'message_id': fields.many2one('mail.message', string='Message'),
        'message_body': fields.related('message_id', 'body',
                                       type='html', string='Message to move',
                                       readonly=True),
        'can_create_partner': fields.function(_get_can_create_partner,
                                              method=True, type='boolean',
                                              string='Can move'),
        'partner_id': fields.many2one('res.partner', string='Author'),
        'message_email_from': fields.char('Email From'),
        'message_name_from': fields.char('Name From'),
    }

    def create_partner(self, cr, uid, message_id, context=None):
        message = self.pool['mail.message'].browse(cr, uid, message_id,
                                                   context=context)
        email_from = message.email_from
        message_name_from = False
        message_email_from = False
        partner_id = False
        if email_from:
            parts = email_split(email_from.replace(' ', ','))
            if parts:
                email = parts[0]
                name = email_from[:email_from.index(email)].\
                    replace('"', '').replace('<', '').strip() \
                    or email_from
            else:
                name, email = email_from
            message_name_from = name
            message_email_from = email
        if message_name_from:
            context.update({'update_message_author': True})
            partner_id = self.pool['res.partner'].create(
                cr, uid, {'name': message_name_from,
                          'email': message_email_from}, context=context)
        context = {'partner_id': partner_id}

        return context


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        res_id = super(ResPartner, self).create(cr, uid, vals, context=context)
        if 'update_message_author' in context and 'email' in vals:
            mail_message_obj = self.pool['mail.message']
            # Escape special SQL characters in email_address to
            # avoid invalid matches
            email_address = (vals['email'].replace('\\', '\\\\').
                             replace('%', '\\%').replace('_', '\\_'))
            email_brackets = "<%s>" % email_address
            messages = mail_message_obj.search(cr, uid, [
                                '|',
                                ('email_from', '=ilike', email_address),
                                ('email_from', 'ilike', email_brackets),
                                ('author_id', '=', False)
                            ], context=context)
            if messages:
                mail_message_obj.write(cr, SUPERUSER_ID, messages,
                                       {'author_id': res_id}, context=context)
        return res_id
