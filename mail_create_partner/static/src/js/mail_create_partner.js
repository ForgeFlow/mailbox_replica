openerp.mail_create_partner = function (session) {
    var _t = session.web._t,
       _lt = session.web._lt;

    var mail = session.mail;

    mail.ThreadMessage.include({
        bind_events: function(){
            this._super.apply(this, arguments);
            this.$('.oe_create_partner').on('click', this.on_create_partner)
        },
        on_create_partner: function(event){
            var self = this;
            var context = {
                'default_message_id': this.id
            }
            var action = {
                name: _t('Create Partner'),
                type: 'ir.actions.act_window',
                res_model: 'mail_create_partner.wizard',
                view_mode: 'form',
                view_type: 'form',
                views: [[false, 'form']],
                target: 'new',
                context: context,
            };

            self.do_action(action, {
                'on_close': function(){
                    self.check_for_rerender();
                }
            });
        }
    })

    mail.MessageCommon.include({
        init: function (parent, datasets, options) {
            this._super(parent, datasets, options);
            this.no_author = true;
            this.author_id == datasets.author_id || false
            if (this.author_id != false) {
                if (this.author_id[0] == 0) {
                    this.no_author = true;
                } else {
                    this.no_author = false;
                }
            }

        }
    })

    session.web.form.WidgetButton.include({
        on_click: function() {
            if(this.node.attrs.special == 'quick_create_partner'){
                var self = this;
                var related_field = this.field_manager.fields[this.node.attrs['field']];
                var context_built = $.Deferred();
                context_built.resolve(this.build_context());
                $.when(context_built).pipe(function (context) {
                    var pop = new session.web.form.FormOpenPopup(this);
                    pop.show_element(
                        related_field.field.relation,
                        false,
                        context,
                        {
                            title: _t("Create new record"),
                        }
                    );
                    pop.on('closed', self, function () {
                        self.force_disabled = false;
                        self.check_disable();
                    });
                    pop.on('create_completed', self, function(id) {
                        related_field.set_value(id);
                    });
                });
            }
            else {
                this._super.apply(this, arguments);
            }
        },
    });

}