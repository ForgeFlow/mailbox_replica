# -*- coding: utf-8 -*-
import datetime
import pytz
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class FetchMailServer(models.Model):
    _inherit = 'fetchmail.server'
    _name = 'fetchmail.server'
    _last_updated = None

    run_time = fields.Datetime(string="Launch time")

    def _run_time(self):
        if not self._last_updated:
            self._last_updated = tools.datetime.now()

        src_tstamp_str = self._last_updated.strftime(
            DEFAULT_SERVER_DATETIME_FORMAT)
        src_format = DEFAULT_SERVER_DATETIME_FORMAT
        dst_format = DEFAULT_SERVER_DATETIME_FORMAT
        dst_tz_name = self._context.get('tz') or self.env.user.tz

        if not src_tstamp_str:
            return False
        _now = src_tstamp_str
        if src_format and dst_format:
            # find out server timezone
            server_tz = "UTC"
            try:
                dt_value = datetime.strptime(src_tstamp_str, src_format)
                if dst_tz_name:
                    try:
                        src_tz = pytz.timezone(server_tz)
                        dst_tz = pytz.timezone(dst_tz_name)
                        src_dt = src_tz.localize(dt_value, is_dst=True)
                        dt_value = src_dt.astimezone(dst_tz)
                    except Exception:
                        pass
                _now = dt_value.strftime(dst_format)
            except Exception:
                pass
        return _now

    @api.model
    def _fetch_mails(self):

        if self._context.get('run_fetchmail_manually'):
            # if interval less than 5 seconds
            if self._last_updated and (
                    datetime.datetime.now() - self._last_updated
            ) < datetime.timedelta(0, 5):
                raise UserError(
                    _('Task can be started no earlier than 5 seconds.'))

        res2 = super(FetchMailServer, self)._fetch_mails()

        res = self.env['fetchmail.server'].sudo().with_context(
            tz=self.env.user.tz).search([('state', '=', 'done')])
        if res:
            res[0].run_time = self._run_time()
        return res2


class FetchMailImmediately(models.AbstractModel):
    _name = 'fetch_mail.imm'

    @api.model
    def get_last_update_time(self):
        res = self.env['fetchmail.server'].sudo().with_context(
            tz=self.env.user.tz).search([('state', '=', 'done')])
        array = [r.run_time for r in res]
        if array:
            return array[0]
        else:
            return None

    @api.model
    def run_fetchmail_manually(self):

        fetchmail_task = self.env.ref('fetchmail.ir_cron_mail_gateway_action')
        fetchmail_model = self.env['fetchmail.server'].sudo()

        fetchmail_task._try_lock()
        fetchmail_model.with_context(
            run_fetchmail_manually=True)._fetch_mails()
