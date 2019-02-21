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
                    action: function ( e, dt, button, config ) {
                        var rows = dt.rows( { selected: true } );
                        var data = rows.data();
                        var selected_action = [];
                        for (var index=0; index < data.length; index++) {
                             selected_action.push(data[index][0])
                        }
                        button.ajax_delbtn({
                            selected_action: selected_action
                        })
                    }
                },
            ],
        },
        initComplete: function () {
            var $button = $("a.btn-ajax-table-add")
                .attr("title", grouprel_datatable.button.add.title)
                .attr("href", grouprel_datatable.button.add.url)
                .attr("data-refresh-url", grouprel_datatable.button.add.refresh_url + "?obj_id=");
            $("div.dt-buttons").find('span').contents().unwrap();
            $button.ajax_addbtn();

            $("a.btn-ajax-table-delete")
                .attr("href", grouprel_datatable.button.delete.url)
                .attr("title", grouprel_datatable.button.delete.title)
        },
    });
})(jQuery);