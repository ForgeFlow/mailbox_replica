# -*- coding: utf-8 -*-

from datetime import datetime
import logging
import time
import re

from odoo import api, fields, models
from odoo import tools

_logger = logging.getLogger(__name__)


class FetchMailServer(models.Model):
    _inherit = "fetchmail.server"

    imap_fetch_from_last_date = fields.Boolean(
        'Fetch from last fetch date',
        help='Fetch only IMAP emails that have not yet been received from '
             'the last check.')
    mailbox_ids = fields.One2many(
        'fetchmail.server.mailbox', 'server_id', 'Mailboxes')
    mailbox_path_ids = fields.One2many(
        'fetchmail.server.mailbox.path', 'server_id', 'Mailbox Path',
        readonly=True)

    @api.multi
    def fetch_mail(self):
        mail_thread = self.env['mail.thread']
        action_pool = self.env['ir.actions.server']
        check_original = []

        for server in self:
            if not server.imap_fetch_from_last_date or server.type == 'pop':
                check_original.append(server.id)
                continue

            _logger.info('start checking for new emails on %s server %s',
                         server.type, server.name)

            self.with_context({'fetchmail_server_id': server.id,
                               'server_type': server.type})
            count, failed = 0, 0
            imap_server = False
            fetch_date = datetime.strptime(server.date,
                                           "%Y-%m-%d %H:%M:%S").date()
            fetch_date = fetch_date.strftime("%d-%b-%Y")
            if server.type == 'imap':
                try:
                    imap_server = server.connect()
                    for mailbox in server.mailbox_ids:
                        mailbox_path = str(mailbox.path)
                        if imap_server.select(mailbox_path)[0] != 'OK':
                            _logger.error('Could not open mailbox %s on %s',
                                          mailbox_path, server.name)
                            imap_server.select()
                            continue
                        imap_server.select(mailbox_path)
                        result, data = imap_server.search(
                            None, '(SINCE {date})'.format(date=fetch_date))
                        for message_uid in data[0].split():
                            res_id = None
                            result, data = imap_server.fetch(message_uid,
                                                             '(RFC822)')
                            try:
                                res_id = mail_thread.message_process(
                                    server.object_id.model,
                                    data[0][1],
                                    save_original=server.original,
                                    strip_attachments=(not server.attach))
                            except Exception:
                                _logger.exception('Failed to process mail '
                                                  'from %s server %s.',
                                                  server.type, server.name)
                                failed += 1
                            if res_id and server.action_id:
                                action_pool.run([server.action_id.id],
                                                {'active_id': res_id,
                                                 'active_ids': [res_id],
                                                 'active_model':
                                                     self.env.context.get(
                                                     "thread_model",
                                                     server.object_id.model)})
                            self.env.cr.commit()
                            count += 1
                        _logger.info("Fetched %d email(s) on %s server %s; "
                                     "and mailbox %s. %d succeeded, "
                                     "%d failed.",
                                     count, server.type,
                                     server.name, mailbox_path,
                                     (count - failed), failed)
                except Exception:
                    _logger.exception("General failure when trying to "
                                      "fetch mail from %s server %s.",
                                      server.type, server.name)
                finally:
                    if imap_server:
                        imap_server.select()
                        imap_server.close()
                        imap_server.logout()
            server.write({'date': time.strftime(
                tools.DEFAULT_SERVER_DATETIME_FORMAT)})
        return super(FetchMailServer, self).fetch_mail()

    @api.model
    def _parse_list_response(self, line):
        list_response_pattern = re.compile(
            r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')
        match = list_response_pattern.match(line)
        flags, delimiter, mailbox_name = match.groups()
        mailbox_name = mailbox_name.strip('"')
        return (flags, delimiter, mailbox_name)

    @api.multi
    def list_mailboxes(self):
        mailbox_obj = self.env['fetchmail.server.mailbox']

        for server in self:
            server.mailbox_ids.unlink()
            try:
                imap_server = server.connect()
                typ, data = imap_server.list()
                for line in data:
                    flags, delimiter, mailbox_name = \
                        self._parse_list_response(line)
                    mailbox_obj.create({'server_id': server.id,
                                        'path': mailbox_name})
            except Exception:
                _logger.exception("General failure when trying to "
                                  "fetch mail from %s server %s.",
                                  server.type, server.name)
        return True
