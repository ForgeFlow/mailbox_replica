odoo.define('mail_create_partner.create_partner_object', function (require) {
    "use strict";

    var bus = require('bus.bus').bus;
    var chat_manager = require('mail.chat_manager');
    var base_obj = require('mail_base.base');
    var thread = require('mail.ChatThread');
    var chatter = require('mail.Chatter');
    var Model = require('web.Model');
    var form_common = require('web.form_common');
    var widgets = require('web.form_widgets');
    var core = require('web.core');

    var _t = core._t;

    thread.include({
        init: function(){
            this._super.apply(this, arguments);
            // Add click reaction in the events of the thread object
            this.events['click .oe_create_partner'] = function(event) {
                var message_id = $(event.currentTarget).data('message-id');
                this.trigger("create_partner", message_id);
            };
        },

        on_create_partner: function(message_id){
            var action = {
                name: _t('Create Partner'),
                type: 'ir.actions.act_window',
                res_model: 'mail_create_partner.wizard',
                view_mode: 'form',
                view_type: 'form',
                views: [[false, 'form']],
                target: 'new',
                context: {'default_message_id': message_id},
            };
            this.message_id = message_id;

            this.do_action(action, {
                'on_close': function(){
//                    var message = base_obj.chat_manager.get_message(this.message_id);
//                    chat_manager.bus.trigger('update_message', message);
//                    this.fetch_and_render_thread();
                }
            });
        }
    });

    chatter.include({
        start: function() {
            var result = this._super.apply(this, arguments);
            // For show wizard in the form
            this.thread.on('create_partner', this, this.thread.on_create_partner);
            return $.when(result).done(function() {});
        }
    });

    var ChatAction = core.action_registry.get('mail.chat.instant_messaging');
    ChatAction.include({
        start: function() {
            var result = this._super.apply(this, arguments);
            // For show wizard in the channels
            this.thread.on('create_partner', this, this.thread.on_create_partner);
            return $.when(result).done(function() {});
        }
    });

    base_obj.MailTools.include({
        make_message: function(data){
            var msg = this._super(data);
            msg.no_author = true;
            msg.author_id == data.author_id || false
            if (msg.author_id != false) {
                if (msg.author_id[0] == 0) {
                    msg.no_author = true;
                } else {
                    msg.no_author = false;
                }
            }
            return msg;
        },

        on_notification: function(notifications){
            this._super(notifications);
            var self = this;
            _.each(notifications, function (notification) {
                var model = notification[0][1];
                var message_id = notification[1].id;
                var message = base_obj.chat_manager.get_message(message_id);
                chat_manager.bus.trigger('update_message', message);
            });
        }
    });

    widgets.WidgetButton.include({
        on_click: function(){
            if(this.node.attrs.special == 'quick_create_partner'){
                var self = this;
                var related_field = this.field_manager.fields[this.node.attrs['field']];
                var context_built = $.Deferred();
                context_built.resolve(this.build_context());
                $.when(context_built).pipe(function (context) {
                    var dialog = new form_common.FormViewDialog(self, {
                        res_model: related_field.field.relation,
                        res_id: false,
                        context: context,
                        title: _t("Create new record")
                    }).open();
                    dialog.on('closed', self, function () {
                        self.force_disabled = false;
                        self.check_disable();
                    });
                    dialog.on('create_completed', self, function(id) {
                        related_field.set_value(id);
                    });
                });
            }
            else {
                this._super.apply(this, arguments);
            }
        }
    });
});
