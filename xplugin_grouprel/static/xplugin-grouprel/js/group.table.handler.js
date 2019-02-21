(function ($) {
    var csrftoken = $.getCookie('csrftoken');
    var static_url = window.__admin_media_prefix__.replace(/xadmin\/$/i, "xplugin-grouprel/");
    var table = $('#ajax-table').DataTable({
        dom: 'Blfrtip',
        ajax: {
            url: grouprel_datatable.ajax.url,
            type: "POST",
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        language: {
            url: static_url + window.__admin_language_code__ + ".json"
        },
        scrollX: true,
        processing: true,
        serverSide: true,
        select: {
            style: 'multi'
        },
        columnDefs: grouprel_datatable.columns_defs,
        buttons: {
            buttons: [
                {
                    tag: "a",
                    className: "btn btn-primary btn-sm btn-ajax-table-add",
                    text:"<i class=\"fa fa-plus\"></i>",
                    action: function (e, dt, node, config) {
                        $('div.modal.quick-form')
                            .find(".has-error").each(function(){
                                var $ele = $(this);
                                $ele.removeClass("has-error");
                                $ele.parent().find("span[id^=error_]").remove()
                        })
                    },
                },
                {
                    extend: 'selected',
                    className: 'btn btn-danger btn-sm btn-ajax-table-delete',
                    text: "<i class=\"fa fa-trash-o\"></i>",
                    tag: 'a',
                },
            ],
        },
        initComplete: function () {
            var $button = $("a.btn-ajax-table-add")
                .attr("title", grouprel_datatable.button.title)
                .attr("href", grouprel_datatable.button.url)
                .attr("data-refresh-url", grouprel_datatable.button.refresh_url + "?obj_id=");
            $("div.dt-buttons").find('span').contents().unwrap();
            $button.ajax_addbtn();
        },
    });
})(jQuery);