# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
#           <http://www.eficent.com>
# Copyright 2019 Aleph Objects, Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import hashlib
import time
from odoo import api, models
import re


class MailThread(models.AbstractModel):

    _inherit = "mail.thread"

    @api.model
    def _prepare_header_to_hash(self, msg_dict):
        email_from = msg_dict.get('email_from', False)
        email_to = msg_dict.get('to', False)
        email_date = msg_dict.get('date', False)
        return '%s/%s/%s' % (email_from, email_to, email_date)

    @api.model
    def _create_header_hash(self, msg_dict):
        data = self._prepare_header_to_hash(msg_dict)
        if not data:
            return False
        sha256 = hashlib.sha256(
            data.encode('utf-8')).hexdigest()
        return sha256

    @api.model
    def _get_message_id(self, msg_dict):
        message_id = self._create_header_hash(msg_dict)
        if not message_id:
            message_id = "<%s@localhost>" % time.time()
        return message_id

    @api.model
    def message_parse(self, message, save_original=False):
        # We don't want to store the message-id
        msg_dict = super(MailThread, self).message_parse(
            message, save_original=save_original)
        # Remove empty message-id (contains pattern <%s@localhost>)
        regexp = re.compile(r'<[+-]?([0-9]*[.])?[0-9]+@localhost>')
        if regexp.search(msg_dict['message_id']):
            msg_dict['message_id'] = self._get_message_id(msg_dict)
        return msg_dict
