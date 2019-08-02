(function ($) {
    $.fn.create_table = function (datatable_config) {
        var csrftoken = $.getCookie('csrftoken');
        var static_url = window.__admin_media_prefix__.replace(/xadmin\/$/i, "xplugin-grouprel/");
        var config = {
            ajax: {
                url: datatable_config.ajax.url,
                type: "POST",
                beforeSend: function (xhr, settings) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            },
            language: {
                url: static_url + window.__admin_language_code__ + ".json",
                select: {
                rows: {
                    _: gettext("%d rows selected"),
                    0: gettext("Click a row to select it"),
                    1: gettext("1 row selected")
                }
                }
            },
            scrollX: true,
            processing: true,
            serverSide: true,
            select: {
                style: 'multi',
                selector: 'td:first-child'
            },
            columnDefs: datatable_config.columns_defs,
            initComplete: function () {
                if (datatable_config.hasOwnProperty("initComplete")) {
                    datatable_config.initComplete()
                }
            },
        };
        if (datatable_config.hasOwnProperty("buttons")) {
            config.dom = 'Blfrtip';
            config.buttons = datatable_config.buttons
        }
        var table = this.DataTable(config);
        this.data("table", table);
        return table;
    }
})(jQuery);