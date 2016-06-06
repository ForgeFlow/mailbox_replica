from openerp.osv import fields, osv, orm
from openerp import SUPERUSER_ID
from openerp.tools import email_split
from openerp.tools.translate import _


class wizard(orm.TransientModel):
    _name = 'mail_move_message.wizard'

    def _model_selection(self, cr, uid, context=None):
        selection = []
        ir_model_obj = self.pool['ir.model']
        config_parameters = self.pool['ir.config_parameter']
        model_names = config_parameters.get_param(cr, uid,
                                                  'mail_relocation_models',
                                                  False)
        model_names = model_names.split(',') if model_names else []

        if 'default_message_id' in context:
            message = self.pool['mail.message'].browse(cr, uid, context[
                'default_message_id'], context=context)
            if message.model and message.model not in model_names:
                model_names.append(message.model)
            if message.moved_from_model and message.moved_from_model \
                    not in model_names:
                model_names.append(message.moved_from_model)
        if model_names:
            model_ids = ir_model_obj.search(
                cr, uid, [('model', 'in', model_names)], context=context)
            models = ir_model_obj.browse(cr, uid, model_ids, context=context)
            selection = [(m.model, m.name) for m in models]

        return selection

    def default_get(self, cr, uid, fields_list, context=None):
        res = super(wizard, self).default_get(cr, uid, fields_list, 
                                              context=context)
        model_fields = self.fields_get(cr, uid)
        if model_fields['model']['selection']:
            res['model'] = model_fields['model']['selection'] \
                           and model_fields['model']['selection'][0][0]

        if 'message_id' in res:
            message = self.pool['mail.message'].browse(
                cr, uid, res['message_id'], context=context)
            res['can_move'] = not message.moved_by_message_id or \
                message.moved_by_message_id.id == message.id
            res['message_body'] = message.body
            res['message_subject'] = message.subject
            res['message_moved_by_message_id'] = message.moved_by_message_id.id
            res['message_moved_by_user_id'] = message.moved_by_user_id.id
            res['message_is_moved'] = message.is_moved
            res['message_to_read'] = message.to_read
            res['message_from'] = message.email_from
            res['partner_id'] = message.author_id.id
            res['res_id'] = 0
            if message.author_id and uid not in [u.id for u in
                                                 message.author_id.user_ids]:
                res['filter_by_partner'] = True
            email_from = message.email_from
            if email_from:
                parts = email_split(email_from.replace(' ', ','))
                if parts:
                    email = parts[0]
                    name = email_from[:email_from.index(email)].replace('"', '')\
                        .replace('<', '').strip() or email_from
                else:
                    name, email = email_from
                res['message_name_from'] = name
                res['message_email_from'] = email
        res['uid'] = uid

        return res

    def _get_can_move(self, cr, uid, ids, name, args, context=None):
        # message was not moved before OR message is a top message of
        # previous move
        res = dict.fromkeys(ids, False)
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = not record.message_id.moved_by_message_id or \
              record.message_id.moved_by_message_id.id == record.message_id.id
        return res

    _columns = {
        'message_id': fields.many2one('mail.message', string='Message'),
        'message_body': fields.related('message_id', 'body',
                                       type='html', string='Message to move',
                                       readonly=True),
        'message_from': fields.related('message_id', 'email_from', type='char',
                                       string='From', readonly=True),
        'message_subject': fields.related('message_id', 'subject', type='char',
                                          string='Subject', readonly=True),
        'message_moved_by_message_id': fields.related('message_id',
                                                      'moved_by_message_id',
                                                      type='many2one',
                                                      relation='mail.message',
                                                      string='Moved with',
                                                      readonly=True),
        'message_moved_by_user_id': fields.related('message_id',
                                                   'moved_by_user_id',
                                                   type='many2one',
                                                   relation='res.users',
                                                   string='Moved by',
                                                   readonly=True),
        'message_is_moved': fields.related('message_id', 'is_moved',
                                           type='boolean', string='Is Moved',
                                           readonly=True),
        'parent_id': fields.many2one('mail.message', string='Search by name'),
        'model': fields.selection(_model_selection, string='Model'),
        'res_id': fields.integer(string='Record'),
        'can_move': fields.function(_get_can_move, method=True,
                                    type='boolean', string='Can move'),
        'move_back': fields.boolean('MOVE TO ORIGIN',
                                    help='Move  message and submessages to '
                                         'original place'),
        'partner_id': fields.many2one('res.partner', string='Author'),
        'filter_by_partner': fields.boolean('Filter Records by partner'),
        'message_email_from': fields.char('Email From'),
        'message_name_from': fields.char('Name From'),
        # FIXME message_to_read should be True even if current message or any
        # his childs are unread
        'message_to_read': fields.related('message_id', 'to_read',
                                          type='boolean'),
        'uid': fields.integer('UID'),
    }

#    @api.onchange('move_back')
    def onchange_move_back(self, cr, uid, wiz_id, move_back, message_id,
                           context=None):
        if context is None:
            context = {}
        res = {}
        res.setdefault('value', {})
        message_obj = self.pool['mail.message']
        message = message_obj.browse(cr, uid, message_id, context=context)
        if not move_back:
            return res
        res['value']['parent_id'] = \
            message.moved_from_parent_id.id
        model = message.moved_from_model
        if message.is_moved:
            res['value']['model'] = model
            res['value']['res_id'] = message.moved_from_res_id
        return res

#    @api.onchange('parent_id', 'res_id', 'model')
    def update_move_back(self, cr, uid, record_id, parent_id, model, res_id,
                         context=None):
        if context is None:
            context = {}
        res = {}
        res.setdefault('value', {})
        record = self.browse(cr, uid, record_id, context=context)
        model_id = self.message_id.moved_from_model.id
        res['move_back'] = res['parent_id'] = \
            record.message_id.moved_from_parent_id.id \
            and res_id == record.message_id.moved_from_res_id \
            and (model == model_id or (not model and not model_id))
        return res


#    @api.onchange('parent_id')
    def on_change_parent_id(self, cr, uid, record_id, parent_id, context=None):
        if context is None:
            context = {}
        res = {'value': {}}
        res.setdefault('value', {})
        if parent_id:
            parent = self.pool['mail.message'].browse(cr, uid, parent_id,
                                                      context=context)
            if parent.model:
                res['value']['model'] = parent.model
            else:
                res['value']['model'] = None
            if parent.res_id:
                res['value']['res_id'] = parent.res_id
            else:
                res['value']['res_id'] = None
        return res

    def onchange_partner(self, cr, uid, ids, model, filter_by_partner,
                         partner_id, context=None):
        res = {'value': {}}
        domain = {'res_id': []}
        if model and filter_by_partner and partner_id:
            fields = self.pool[model].fields_get(cr, uid)
            contact_field = False
            for n, f in fields.iteritems():
                if f['type'] == 'many2one' and f['relation'] == 'res.partner':
                    contact_field = n
                    break
            if contact_field:
                domain['res_id'] = [(contact_field, '=', partner_id)]
        if model and domain['res_id']:
            res_id = self.pool[model].search(cr, uid, domain['res_id'],
                                             order='id desc', limit=1,
                                             context=context)
            res['value']['res_id'] = res_id
            res['domain'] = domain
        return res

    def open_moved_by_message_id(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        message_id = None
        for r in self.browse(cr, uid, ids, context=context):
            message_id = r.message_moved_by_message_id.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail_move_message.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [[False, 'form']],
            'target': 'new',
            'context': {'default_message_id': message_id},
        }

    def move(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        message_obj = self.pool['mail.message']
        ir_model_data_obj = self.pool['ir.model.data']

        for r in self.browse(cr, uid, ids, context=context):
            parent_id = False
            if not r.parent_id or not (r.parent_id.model == r.model and
                                       r.parent_id.res_id == r.res_id):
                # link with the first message of record
                parent = message_obj.search(
                    cr, uid, [('model', '=', r.model),
                              ('res_id', '=', r.res_id)],
                    order='id', limit=1, context=context)
                if parent:
                    parent_id = parent[0]
                else:
                    parent_id = None

            message_obj.move(cr, uid, r.message_id.id, parent_id,
                             r.res_id, r.model, r.move_back, context=context)

            if not (r.model and r.res_id):
                obj = ir_model_data_obj.get_object_reference(
                    cr, SUPERUSER_ID, 'mail', 'mail_archivesfeeds')[1]
                return {
                    'type': 'ir.actions.client',
                    'name': 'Archive',
                    'tag': 'reload',
                    'params': {'menu_id': obj},
                }
            return {
                'name': _('Record'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': r.model,
                'res_id': r.res_id,
                'views': [(False, 'form')],
                'type': 'ir.actions.act_window',
            }

    def delete(self, cr, uid, ids, context=None):
        message_obj = self.pool['mail.message']
        for record in self.browse(cr, uid, ids, context=context):
            message_obj.unlink(cr, uid, [record.message_id.id],
                               context=context)
        return {}

    def create_partner(self, cr, uid, message_id, relation, partner_id,
                       message_name_from, message_email_from, context=None):
        model = self.pool[relation]
        message = self.pool['mail.message'].browse(cr, uid, message_id,
                                                   context=context)
        if not partner_id and message_name_from:
            context.update({'update_message_author': True})
            partner_id = self.pool['res.partner'].create(
                cr, uid, {'name': message_name_from,
                          'email': message_email_from}, context=context)

        context = {'partner_id': partner_id}
        if model._rec_name:
            context.update({'default_%s' % model._rec_name: message.subject})

        fields = model.fields_get(cr, uid)
        contact_field = False
        for n, f in fields.iteritems():
            if f['type'] == 'many2one' and f['relation'] == 'res.partner':
                contact_field = n
                break
        if contact_field:
            context.update({'default_%s' % contact_field: partner_id})
        return context

    def read_close(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        message_obj = self.pool['mail.message']
        for record in self.browse(cr, uid, ids, context=context):
            message_obj.set_message_read(cr, uid, [record.message_id.id],
                                         True, context=context)
            child_ids = [child.id for child in record.message_id.child_ids]
            message_obj.set_message_read(cr, uid, child_ids,
                                         True, context=context)
            return {'type': 'ir.actions.act_window_close'}


class mail_message(orm.Model):
    _inherit = 'mail.message'

    def _get_all_childs(self, cr, uid, ids, name, args, context=None):
        res = dict.fromkeys(ids, False)
        for message in self.browse(cr, uid, ids, context=context):
            ids = []
            ids.append(message.id)
            while True:
                new_ids = self.search(cr, uid, [('parent_id', 'in', ids),
                                                ('id', 'not in', ids)],
                                      context=context)
                if new_ids:
                    ids = ids + new_ids
                    continue
                break
            moved_childs = self.search(
                cr, uid, [('moved_by_message_id', '=', message.id)],
                context=context)
            res[message.id] = ids + moved_childs
        return res

    _columns = {
        'is_moved': fields.boolean('Is moved'),
        'moved_from_res_id': fields.integer(
            'Related Document ID (Original)'),

        'moved_from_model': fields.char(
            'Related Document Model (Original)'),

        'moved_from_parent_id': fields.many2one(
            'mail.message', 'Parent Message (Original)',
            ondelete='set null'),

        'moved_by_message_id': fields.many2one(
            'mail.message', 'Moved by message',
            ondelete='set null',
            help='Top message, that initate moving this message'),
        'moved_by_user_id': fields.many2one(
            'res.users', 'Moved by user', ondelete='set null'),
        'all_child_ids': fields.function(_get_all_childs,
                                         type='one2many',
                                         obj='mail.message',
                                         string='All childs',
                                         help='all childs, '
                                              'including subchilds')
    }

    def move(self, cr, uid, message_id, parent_id, res_id, model, move_back,
             context=None):
        if context is None:
            context = {}
        vals = {}
        message = self.browse(cr, uid, message_id, context=context)
        if move_back:
            # clear variables if we move everything back
            vals['is_moved'] = False
            vals['moved_by_user_id'] = None
            vals['moved_by_message_id'] = None

            vals['moved_from_res_id'] = None
            vals['moved_from_model'] = None
            vals['moved_from_parent_id'] = None
        else:
            vals['parent_id'] = parent_id
            vals['res_id'] = res_id
            vals['model'] = model

            vals['is_moved'] = True
            vals['moved_by_user_id'] = uid
            vals['moved_by_message_id'] = message.id

        for r in message.all_child_ids:
            r_vals = vals.copy()
            if not r.is_moved:
                # moved_from_* variables contain not last, but original
                # reference
                r_vals['moved_from_parent_id'] = r.parent_id.id
                r_vals['moved_from_res_id'] = r.res_id
                r_vals['moved_from_model'] = r.model
            elif move_back:
                r_vals['parent_id'] = r.moved_from_parent_id.id
                r_vals['res_id'] = r.moved_from_res_id
                r_vals['model'] = r.moved_from_model
            print 'update message', r, r_vals
            self.write(cr, SUPERUSER_ID, [r.id], r_vals, context=context)

    def name_get(self, cr, uid, ids, context=None):
        if not context or 'extended_name' not in context:
            return super(mail_message, self).name_get(cr, uid, ids,
                                                      context=context)
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['record_name', 'model', 'res_id'],
                          context=context)
        res = []
        for record in reads:
            name = record['record_name'] or ''
            extended_name = '   [%s] ID %s' % (record.get('model', 'UNDEF'),
                                               record.get('res_id', 'UNDEF'))
            res.append((record['id'], name + extended_name))
        return res

    def _message_read_dict(self, cr, uid, message, parent_id=False,
                           context=None):
        res = super(mail_message, self)._message_read_dict(cr, uid, message,
                                                           parent_id, context)
        res['is_moved'] = message.is_moved
        return res


class mail_move_message_configuration(orm.TransientModel):
    _name = 'mail_move_message.config.settings'
    _inherit = 'res.config.settings'

    _columns = {
        'model_ids': fields.many2many('ir.model', string='Models',
                                      id1='config_id', id2='model_id'),
    }

    def get_default_model_ids(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        config_parameters = self.pool['ir.config_parameter']
        model_obj = self.pool['ir.model']
        model_names = config_parameters.get_param(cr, uid,
                                                  'mail_relocation_models',
                                                  context=context)
        if not model_names:
            return {}
        model_names = model_names.split(',')
        model_ids = model_obj.search(cr, uid, [('model', 'in',
                                                model_names)], context=context)
        return {'model_ids': [m for m in model_ids]}

    def set_model_ids(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        config_parameters = self.pool['ir.config_parameter']
        for record in self.browse(cr, uid, ids, context=context):
            model_names = ','.join([m.model for m in record.model_ids])
            config_parameters.set_param(cr,
                                        uid,
                                        'mail_relocation_models',
                                        model_names, context=context)


class res_partner(orm.Model):
    _inherit = 'res.partner'

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        res_id = super(res_partner, self).create(cr, uid, vals,
                                                 context=context)
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
