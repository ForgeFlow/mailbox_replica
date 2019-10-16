# Copyright 2015 Innoviu srl <http://www.innoviu.it>
# Copyright 2015 Agile Business Group <http://www.agilebg.com>
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
#                <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Fetchmail Fetch Missing",
    "summary": 'Fetchmail fetch missing messages',
    "version": "12.0.1.0.0",
    "category": "Discuss",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "https://www.github.com/Eficent/mailbox_replica",
    "license": 'AGPL-3',
    "installable": True,
    "depends": [
        'fetchmail',
        'mail',
    ],
    "data": [
        'views/fetchmail_views.xml',
        'views/mail_message_trash_views.xml',
        'security/ir.model.access.csv',
    ],
}
