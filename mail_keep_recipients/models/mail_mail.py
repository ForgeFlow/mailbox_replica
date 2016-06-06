from openerp.osv import orm, fields


class MailMail(orm.Model):
    _inherit = 'mail.mail'

    _columns = {
        'recipient_ids': fields.many2many('res.partner',
                                          string='To (Partners)'),
    }

    def send(self, cr, uid, ids, auto_commit=False, recipient_ids=None,
             context=None):
        if recipient_ids:
            rec_ids = [(4, id) for id in recipient_ids]
            self.write(cr, uid, ids, {'recipient_ids': rec_ids},
                       context=context)
        for mail in self.browse(cr, uid, ids, context=context):
            if not recipient_ids:
                recipient_ids = [rec.id for rec in mail.recipient_ids] or False
            super(MailMail, self).send(cr, uid, [mail.id],
                                       auto_commit=auto_commit,
                                       recipient_ids=recipient_ids,
                                       context=context)
        return True
