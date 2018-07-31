.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

========================
Web Polymorphic Many2One
========================

This module adds a new widget named "polymorphic".
The polymorphic field allow to dynamically store an id linked to any model in
Odoo instead of the usual fixed one in the view definition.

Python fields declaration::

    'model': fields.many2one('ir.model', string='Model'),
    'object_id': fields.integer("Resource")

XML fields declaration::

    <field name="model" invisible="1" />
    <field name="object_id" widget="polymorphic" polymorphic="model" />
