;(function ($) {

    $('form.widget-form').on('post-success', function (e, data) {
        $(this).data('ajax_form_modal').clean();
        $('.alert-success #change-link').attr('href', data['change_url']);
        $('.alert-success').show()
    });

    var AjaxForm = function (element, options) {
        var that = this;

        this.$form = $(element);
        this.ainit()
    }

    AjaxForm.prototype = {
        constructor: AjaxForm,

        ainit: function () {
            this.$mask = $('<div class="mask"><h1 style="text-align:center;"><i class="fa-spinner fa-spin fa fa-large"></i></h1></div>');

            this.$form.prepend(this.$mask);
            this.$form.submit($.proxy(this.submit, this));

            this.$form.find('input, select, textarea').each(function () {
                var el = $(this);
                if (el.is("[type=checkbox]")) {
                    el.data('init-value', el.attr('checked'))
                } else if (el.is("select")) {
                    el.data('init-value', el[0].selectedIndex)
                } else {
                    el.data('init-value', el.val())
                }
            })
        },

        clean: function () {
            this.$form.find('input, select, textarea').each(function () {
                var el = $(this);
                if (el.is("[type=checkbox]")) {
                    el.removeAttr('checked')
                } else if (el.is("select")) {
                    el[0].selectedIndex = el.data('init-value') || 0
                } else {
                    el.val(el.data('init-value') || '')
                }
                el.change()
            })
        },
        submit: function (e) {
            e.stopPropagation();
            e.preventDefault();
            $.when(this.save())
                .done($.proxy(function (data) {
                    this.$mask.hide();
                    this.$form.find('submit, button[type=submit], input[type=submit]').removeClass('disabled');
                    this.$form.find('.alert-success').hide();
                    if (data['result'] === 'success') {
                        this.$form.trigger('post-success', data);
                    }
                }, this))
                .fail($.proxy(function (xhr) {
                    this.$mask.hide();
                    alert(typeof xhr === 'string' ? xhr : xhr.responseText || xhr.statusText || 'Unknown error!');
                }, this));
        },
        save: function (newValue) {

            this.$form.find('.text-error, .help-inline.error').remove();
            this.$form.find('.control-group').removeClass('error');

            this.$mask.show();
            this.$form.find('submit, button[type=submit], input[type=submit]').addClass('disabled');

            var $nonfile_input = this.$form.serializeArray();

            var formData = new FormData();

            $nonfile_input.forEach(function (field) {
                formData.append(field.name, field.value)
            });

            var $file_input = this.$form.find("input[type=file]");
            $file_input.each(function (idx, file) {
                formData.append($(file).attr('name'), file.files[0]);
            });

            return $.ajax({
                data: formData,
                url: this.$form.attr('action'),
                type: "POST",
                dataType: 'json',
                contentType: false,
                processData: false,
                beforeSend: function (xhr, settings) {
                    xhr.setRequestHeader("X-CSRFToken", $.getCookie('csrftoken'));
                }
            })
        },
    }

    $.fn.ajax_form_modal = function (option) {
        var args = Array.apply(null, arguments);
        args.shift();
        return this.each(function () {
            var $this = $(this),
                data = $this.data('ajax_form_modal'),
                options = typeof option == 'object' && option;
            if (!data) {
                $this.data('ajax_form_modal', (data = new AjaxForm(this)));
            }
        });
    };

    $.fn.ajax_form_modal.Constructor = AjaxForm;

    $.fn.exform.renders.push(function (form) {
        if (form.is('.quick-form-modal')) {
            form.ajax_form_modal()
        }
    })

    var QuickAddBtn = function (element, options) {
        this.$btn = $(element);
        this.options = options || {};
        this.url = this.$btn.attr('href');
        this.$for_input = $('#' + this.$btn.data('for-id'));
        this.$for_wrap = $('#' + this.$btn.data('for-id') + '_wrap_container');
        this.refresh_url = this.$btn.data('refresh-url');
        this.rendered_form = false;
        this.binit(element, options);
    }

    QuickAddBtn.prototype = {
        constructor: QuickAddBtn,

        binit: function(element, options){
            if (options.bind_click) this.$btn.click($.proxy(this.click, this));
        },

        click: function(e) {
            e.stopPropagation();
            e.preventDefault();
            this.execute()
        },

        execute: function () {
            var self = this;

            if (!this.modal) {
                this.modal = $('<div class="modal fade quick-form-modal" role="dialog"><div class="modal-dialog"><div class="modal-content">' +
                    '<div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button><h3>' +
                    this.$btn.attr('title') + '</h3></div><div class="modal-body"></div>' +
                    '<div class="modal-footer" style="display: none;"><button class="btn btn-default" data-dismiss="modal" aria-hidden="true">' + gettext('Close') + '</button>' +
                    '<a class="btn btn-primary btn-submit">' + gettext("Add") + '</a></div></div></div></div>');
                $('body').append(this.modal);
            }
            this.modal.find('.modal-body').html('<h2 style="text-align:center;"><i class="fa-spinner fa-spin fa fa-large"></i></h2>');
            var data = this.options.data || null;
            if (data != null && Object.keys(data).length > 0) { // post
                data.csrfmiddlewaretoken = $.getCookie('csrftoken');
            }
            this.modal.find('.modal-body').load(this.url, data,
                function (form_html, status, xhr) {
                    var form = $(this).find('form');
                    form.addClass('quick-form-modal');
                    form.on('post-success', $.proxy(self.post_success, self));
                    form.exform();

                    self.modal.find('.modal-footer').show();
                    self.modal.find('.btn-submit').click(function () {
                        form.submit()
                    });

                    self.$form = form
            });
            this.modal.find('button[data-dismiss="modal"]').click(function () {
                var data = self.$form.data('ajax_form_modal');
                if (data && data.hasOwnProperty("clean")) {
                    data.clean();
                }
            });
            this.modal.modal();
            return this;
        },
        post_success: function (e, data) {
            this.$form.data('ajax_form_modal').clean();
            this.modal.modal('hide');
        }
    }

    $.fn.ajax_btn_form_exc = function (options) {
        options = options || {};
        options.bind_click = false;
        return new QuickAddBtn(this, options).execute()
    };

    $.fn.ajax_btn_form = function ( option ) {
        return this.each(function () {
            var $this = $(this), data = $this.data('ajax_btn_form');
            if (!data) {
                $this.data('ajax_btn_form', (data = new QuickAddBtn(this, {bind_click: true})));
            }
        });
    };

    $.fn.ajax_btn_form.Constructor = QuickAddBtn;

})(jQuery);
