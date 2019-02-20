(function ($) {
    var csrftoken = $.getCookie('csrftoken');
    var static_url = window.__admin_media_prefix__.replace(/xadmin\/$/i, "xplugin-grouprel/");
    var table = $('#ajax-table').DataTable({
        dom: 'Blfrtip',
        "ajax": {
            "url": grouprel_datatable.ajax.url,
            "type": "POST",
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        "language": {
            "url": static_url + window.__admin_language_code__ + ".json"
        },
        "processing": true,
        "serverSide": true,
        "columnDefs": grouprel_datatable.columns_defs,
        buttons: {
            buttons: [{
                text: grouprel_datatable.button.text,
                action: function (e, dt, node, config) {
                    $('div.modal.quick-form')
                        .find(".has-error").each(function(){
                            var $input = $(this);
                            $input.removeClass("has-error");
                            $input.parent().find("span[id^=error_]").remove()
                    })
                }
            }],
            dom: {
                button: {
                    tag: "a",
                    className: "btn btn-primary btn-md btn-ajax-table-add"
                }
            }
        },
        initComplete: function () {
            var $button = $("a.btn-ajax-table-add")
                .attr("title", grouprel_datatable.button.title)
                .attr("href", grouprel_datatable.button.url)
                .attr("data-refresh-url", "#");
            $button.ajax_addbtn();
        },
    });
})(jQuery);