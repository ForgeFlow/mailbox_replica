# -*- coding: utf-8 -*-
import datetime

from openerp.tools.translate import _
from openerp import tools

from openerp.osv import fields, osv, orm
from openerp import SUPERUSER_ID


class FetchMailServer(orm.Model):
    _inherit = 'fetchmail.server'
    _name = 'fetchmail.server'

    _last_updated = None

    def _run_time(self, cr, uid, ids, name, args, context=None):
        if not self._last_updated:
            self._last_updated = tools.datetime.now()
        res = dict.fromkeys(ids, False)
        for server in self.browse(cr, uid, ids, context=context):
            src_tstamp_str = self._last_updated.strftime(
                tools.misc.DEFAULT_SERVER_DATETIME_FORMAT)
            src_format = tools.misc.DEFAULT_SERVER_DATETIME_FORMAT
            dst_format = tools.misc.DEFAULT_SERVER_DATETIME_FORMAT
            dst_tz_name = context.get('tz')
            _now = tools.misc.server_to_local_timestamp(
                src_tstamp_str, src_format, dst_format, dst_tz_name)
            res[server.id] = _now
        return res

    _columns = {
        'run_time': fields.function(_run_time, method=True,
                                    type='datetime',
                                    string="Launch time")
    }

    @classmethod
    def _update_time(cls):
        cls._last_updated = tools.datetime.now()

    def _fetch_mails(self, cr, uid, ids=False, context=None):
        if context is None:
            context = {}
        if context.get('run_fetchmail_manually'):
            # if interval less than 5 seconds
            if self._last_updated \
                    and (datetime.datetime.now() - self._last_updated) < \
                    datetime.timedelta(0, 5):
                raise orm.except_orm(
                    _('Error'),
                    _('Task can be started no earlier than 5 seconds.'))
        res = super(FetchMailServer, self)._fetch_mails(cr, SUPERUSER_ID, ids,
                                                        context=context)

        self._last_updated = tools.datetime.now()
        return res


class FetchMailImmediately(orm.AbstractModel):

    _name = 'fetch_mail.imm'

    def get_last_update_time(self, cr, uid, context=None):
        fechmail_obj = self.pool['fetchmail.server']
        res_ids = fechmail_obj.search(cr, SUPERUSER_ID,
                                      [('state', '=', 'done')],
                                      context=context)
        res = fechmail_obj.browse(cr, SUPERUSER_ID, res_ids, context=context)
        array = [r.run_time for r in res]
        if array:
            return array[0]
        else:
            return None

    def run_fetchmail_manually(self, cr, uid, context=None):
        fetchmail_obj = self.pool['fetchmail.server']
        ir_cron_obj = self.pool['ir.cron']
        cron_id = self.pool.get('ir.model.data').get_object_reference(
            cr, uid, 'fetchmail', 'ir_cron_mail_gateway_action')[1]
        ir_cron_obj._try_lock(cr, uid, [cron_id], context=context)
        context.update({'run_fetchmail_manually': True})
        fetchmail_obj._fetch_mails(cr, uid, False, context=context)
        return True
