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
try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib
from odoo import api, fields, models, tools
from odoo.tools import pycompat
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

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
            msg_date = stored_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return '%s/%s/%s' % (msg_from, msg_to, msg_date)

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
                            additionnal_context):
        MailThread = self.env['mail.thread']
        messages = []
        fetch_from_date = datetime.today() - timedelta(days=self.nbr_days)
        _logger.info(
            'Starting to fetch emails from %s, from %s' %
            (self.name,
             fetch_from_date.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)))
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
            try:
                message = data[0][1]
                if isinstance(message, xmlrpclib.Binary):
                    message = bytes(message.data)
                if isinstance(message, pycompat.text_type):
                    message = message.encode('utf-8')
                extract = getattr(email, 'message_from_bytes',
                                  email.message_from_string)
                msg_txt = extract(message)
                message_id = self._get_message_id(msg_txt)
                received_messages_d[message_id] = new_uid
            except Exception:
                _logger.info('Failed to process mail from %s server %s.',
                             self.type, self.name, exc_info=True)
                failed += 1
        _logger.info(
            'Mapping searched emails with existing ones in Odoo '
            'for %s server.' % self.name)
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
        _logger.info(
            'Fetching emails found truly new from Odoo '
            'for %s server.' % self.name)
        for num in messages:
            # SEARCH command *always* returns at least the most
            # recent message, even if it has already been synced
            res_id = None
            result, data = imap_server.fetch(num, '(RFC822)')
            if data and data[0]:
                _logger.info(
                    'Processing email %s' % data[0][1])
                try:
                    res_id = MailThread.with_context(
                        **additionnal_context).message_process(
                        self.object_id.model, data[0][1],
                        save_original=self.original,
                        strip_attachments=(not self.attach))
                except Exception:
                    _logger.info('Failed to process mail from %s server %s.',
                                 self.type, self.name, exc_info=True)
                    failed += 1
                if res_id and hasattr(self, 'action_id') and self.action_id:
                    self.action_id.with_context({
                        'active_id': res_id,
                        'active_ids': [res_id],
                        'active_model': self.env.context.get(
                            "thread_model", self.object_id.model)
                    }).run()
                imap_server.store(num, '+FLAGS', '\\Seen')
                cr = self._cr
                # pylint: disable=invalid-commit
                cr.commit()
                count += 1
        _logger.info(
            'Ended fetching emails for %s server from date %s.'
            % (self.name, fetch_from_date))
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
                    days=server.nbr_days)
                imap_server = None
                try:
                    imap_server = server.connect()
                    imap_server.select()
                    count, failed = server._fetch_missing_imap(
                        imap_server, count, failed,
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
                super(FetchmailServer, server).fetch_mail()
        return True
