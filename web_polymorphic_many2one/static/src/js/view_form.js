/* Copyright 2010-2014 Elico Corp
   Copyright 2014-2015 Augustin Cisterne-Kaas (ACK Consulting Limited)
   Copyright 2018 Miquel Raïch (Eficent)
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define('web_polymorphic_many2one.FieldPolymorphic', function (require) {
    var core = require('web.core');

    var FieldMany2One = core.form_widget_registry.get('many2one');
    var FieldPolymorphic = FieldMany2One.extend( {
        template: "FieldMany2One",
        events: {
            'focus input': function(e) {
                this.field.relation = this.field_manager.get_field_value(this.polymorphic);
            },
            'click input': function(e) {
                this.field.relation = this.field_manager.get_field_value(this.polymorphic);
            }
        },
        init: function(field_manager, node) {
            this._super(field_manager, node);
            this.polymorphic = this.node.attrs.polymorphic;
        },
        render_editable: function() {
            var self = this;
            this.$dropdown = this.$(".o_dropdown_button");
            this.$dropdown.click(function() {
                self.polymorphic = self.node.attrs.polymorphic;
                self.field.relation = self.field_manager.get_field_value(self.polymorphic);
            });
            this._super();
            this.set_polymorphic_event();
            this.set({
                readonly: true
            });

        },
        set_polymorphic_event: function() {
            var self = this;
            this.field_manager.fields[this.polymorphic].$el.on(
                'change', function(){
                    var field_value = self.field_manager.get_field_value(self.polymorphic);
                    if(field_value !== false) {
                        self.set("effective_readonly", false);
                    } else {
                        self.set("effective_readonly", true);
                    }
                }
            );
        }
    });
    core.form_widget_registry.add('polymorphic', FieldPolymorphic);
});
