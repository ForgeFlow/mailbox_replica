.. image:: https://img.shields.io/badge/license-GPL--3-blue.png
   :target: https://www.gnu.org/licenses/gpl
   :alt: License: GPL-3

=========================
Web Polymorphic Selection
=========================

This module adds a new widget named "polymorphic".
The polymorphic field allow to dynamically store an id linked to any model in
Odoo instead of the usual fixed one in the view definition.

E.g::

    <field name="model" widget="polymorphic" polymorphic="object_id" />
    <field name="object_id" />

