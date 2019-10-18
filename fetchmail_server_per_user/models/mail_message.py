# Copyright 2015-18 Eficent (<http://www.eficent.com/>)
#             <contact@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.multi
    def _notify_recipients(
        self,
        rdata,
        record,
        msg_vals,
        force_send=False,
        send_after_commit=True,
        model_description=False,
        mail_auto_delete=True,
    ):
        rdata = self._notify_compute_internal_recipients(
            record, msg_vals, rdata
        )
        partner_email_rdata = [r for r in rdata["partners"]]
        self.env["res.partner"]._notify(
            self,
            partner_email_rdata,
            record,
            force_send=force_send,
            send_after_commit=send_after_commit,
            model_description=model_description,
            mail_auto_delete=mail_auto_delete,
        )
        return super(MailMessage, self)._notify_recipients(
            rdata,
            record,
            msg_vals,
            force_send,
            send_after_commit,
            model_description,
            mail_auto_delete,
        )

    @api.multi
    def _notify_compute_internal_recipients(self, record, msg_vals, rdata):
        rdata["partners"].append(
            {
                "id": record.id,
                "active": True,
                "share": False,
                "groups": [1],
                "notif": "inbox",
                "type": "user",
            }
        )
        return rdata
