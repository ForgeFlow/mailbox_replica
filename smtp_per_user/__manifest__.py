# Author: Andrius Laukavičius. Copyright: JSC Boolit.
# See LICENSE file for full copyright and licensing details.

{
    "name": "SMTP Per User",
    "version": "12.0.1.0.0",
    "summary": "Send letters from Odoo using your own mail",
    "category": "Mail",
    "author": "Boolit",
    "license": "LGPL-3",
    "website": "https://www.github.com/Eficent/mailbox_replica",
    "depends": ["mail"],
    "data": ["security/ir.model.access.csv", "views/smtp_per_user_view.xml"],
    "installable": True,
}
