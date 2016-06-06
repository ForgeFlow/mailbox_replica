from openerp.osv import orm


class mail_message(orm.Model):
    _inherit = 'mail.message'

    def check_access_rule(self, cr, uid, ids, operation, context=None):
        model_data_obj = self.pool['ir.model.data']
        res_groups_obj = self.pool['res.groups']
        group_all_emails_id = model_data_obj._get_id(
            cr, uid, 'mail_outgoing',
            'group_all_emails')
        res_id = model_data_obj.read(cr, uid, [group_all_emails_id],
                                     ['res_id'])[0]['res_id']
        group_all_emails = res_groups_obj.browse(
            cr, uid, res_id, context=context)
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        user_groups = set(user.groups_id)
        if user_groups.issuperset([group_all_emails]):
            return

        return super(mail_message, self).check_access_rule(cr, uid, ids,
                                                           operation, context)


class mail_mail(orm.Model):
    _name = 'mail.mail'
    _inherit = ['mail.mail', 'ir.needaction_mixin']
    _needaction = True

    def _needaction_domain_get(self, cr, uid, context=None):
        return [('state', 'in', ['outgoing', 'exception'])]
