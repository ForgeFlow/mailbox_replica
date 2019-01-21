# Copyright 2015 Innoviu srl <http://www.innoviu.it>
# Copyright 2015 Agile Business Group <http://www.agilebg.com>
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
#           <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime, timedelta
import dateutil
import time
import pytz
import email
import hashlib
from odoo import api, fields, models, tools

_logger = logging.getLogger(__name__)


class FetchmailServer(models.Model):
    _inherit = "fetchmail.server"

    nbr_days = fields.Integer(
        string='# Days to fetch',
        help="Remote emails with a date greater today's date - # days will "
             "be fetched if not already processed",
        default=1)

    @api.model
    def _prepare_header_to_hash(self, msg_str):
        msg_from = msg_str.get('From')
        msg_to = msg_str.get('To')
        message_id = msg_str.get('Message-ID')
        msg_date = False
        if msg_str.get('Date'):
            try:
                date_hdr = tools.decode_smtp_header(msg_str.get('Date'))
                parsed_date = dateutil.parser.parse(date_hdr, fuzzy=True)
                if parsed_date.utcoffset() is None:
                    # naive datetime, so we arbitrarily decide to make it
                    # UTC, there's no better choice. Should not happen,
                    # as RFC2822 requires timezone offset in Date headers.
                    stored_date = parsed_date.replace(tzinfo=pytz.utc)
                else:
                    stored_date = parsed_date.astimezone(tz=pytz.utc)
            except Exception:
                _logger.info(
                    'Failed to parse Date header %r in incoming mail '
                    'with message-id %r, assuming current date/time.',
                    msg_str.get('Date'), message_id)
                stored_date = datetime.now()
            msg_date = stored_date.strftime(
                tools.DEFAULT_SERVER_DATETIME_FORMAT)
        if msg_date and msg_from and msg_to:
            return '%s/%s/%s' % (msg_from, msg_to, msg_date)
        else:
            return False

    @api.model
    def _create_header_hash(self, msg_str):
        data = self._prepare_header_to_hash(msg_str)
        if not data:
            return False
        sha256 = hashlib.sha256(
            data.encode('utf-8')).hexdigest()
        return sha256

    @api.model
    def _get_message_id(self, msg_str):
        message_id = msg_str.get('Message-ID')
        if not message_id:
            message_id = self._create_header_hash(msg_str)
            if not message_id:
                message_id = "<%s@localhost>" % time.time()
        return message_id

    @api.model
    def _fetch_missing_imap(self, imap_server, count, failed,
                            server, additionnal_context):
        MailThread = self.env['mail.thread']
        messages = []
        fetch_from_date = datetime.today() - timedelta(days=self.nbr_days)
        search_status, uids = imap_server.search(
            None,
            'SINCE', '%s' % fetch_from_date.strftime('%d-%b-%Y')
            )
        new_uids = uids[0].split()
        received_messages_d = {}
        for new_uid in new_uids:
            fetch_status, data = imap_server.fetch(
                new_uid.decode(),
                '(BODY.PEEK[HEADER])'
                )
            msg_str = email.message_from_string(data[0][1].decode())
            message_id = self._get_message_id(msg_str)
            received_messages_d[message_id] = new_uid
        # Retrieve all the message id's stored in odoo
        mail_messages = self.env['mail.message'].search(
            [('message_id', 'in', list(received_messages_d.keys()))])
        mail_msg_d = mail_messages.read(['message_id'])
        stored_mids = [m['message_id'] for m in mail_msg_d]
        # Retrieve all the messages trashed
        mail_messages_trashed = self.env['mail.message.trash'].search(
            [('message_id', 'in', list(received_messages_d.keys()))])
        mail_msg_d = mail_messages_trashed.read(['message_id'])
        trashed_mids = [m['message_id'] for m in mail_msg_d]
        # If it has not yet been received, nor was trashed then it is new
        for message_id in received_messages_d.keys():
            if str(message_id) not in stored_mids and \
                    str(message_id) not in trashed_mids:
                messages.append(received_messages_d[message_id])
        for num in messages:
            # SEARCH command *always* returns at least the most
            # recent message, even if it has already been synced
            res_id = None
            result, data = imap_server.fetch(num, '(RFC822)')
            if data and data[0]:
                try:
                    res_id = MailThread.with_context(
                        **additionnal_context).message_process(
                        server.object_id.model, data[0][1],
                        save_original=server.original,
                        strip_attachments=(not server.attach))
                except Exception:
                    _logger.info('Failed to process mail from %s server %s.',
                                 server.type, server.name, exc_info=True)
                    failed += 1
                if res_id and server.action_id:
                    server.action_id.with_context({
                        'active_id': res_id,
                        'active_ids': [res_id],
                        'active_model': self.env.context.get(
                            "thread_model", server.object_id.model)
                    }).run()
                imap_server.store(num, '+FLAGS', '\\Seen')
                cr = self._cr
                # pylint: disable=invalid-commit
                cr.commit()
                count += 1
        return count, failed

    @api.multi
    def fetch_mail(self):
        additionnal_context = {
            'fetchmail_cron_running': True
        }
        for server in self:
            if server.type == 'imap' and server.nbr_days:
                _logger.info(
                    'start checking for new emails, %s days in the past, '
                    'on %s server %s',
                    server.nbr_days, server.type, server.name)
                additionnal_context['fetchmail_server_id'] = server.id
                additionnal_context['server_type'] = server.type
                count, failed = 0, 0
                fetch_from_date = datetime.today() - timedelta(
                    days=self.nbr_days)
                imap_server = None
                try:
                    imap_server = server.connect()
                    imap_server.select()
                    count, failed = self._fetch_missing_imap(
                        imap_server, count, failed, server,
                        additionnal_context)
                except Exception:
                    _logger.exception(
                        "General failure when trying to fetch mail by date \
                        from %s server %s.",
                        server.type,
                        server.name
                        )
                finally:
                    if imap_server:
                        imap_server.close()
                        imap_server.logout()
                _logger.info(
                    "Fetched %d email(s) on %s server %s, starting from "
                    "%s; %d succeeded, %d failed.", count,
                    server.type, server.name, fetch_from_date,
                    (count - failed), failed)
                server.write({'date': fields.Datetime.now()})
            else:
                super(FetchmailServer, self).fetch_mail()
        return True
