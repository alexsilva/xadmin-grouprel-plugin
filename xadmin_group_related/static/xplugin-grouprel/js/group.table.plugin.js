(function ($) {
    $.fn.create_table = function (datatable_config) {
            var csrftoken = $.getCSRFToken(),
            static_url = window.xadmin.media_prefix.replace(/xadmin\/$/i, "xplugin-grouprel/"),
            config = {
                ajax: {
                    url: datatable_config.ajax.url,
                    type: "POST",
                    beforeSend: function (xhr, settings) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                },
                language: {
                    url: static_url + window.xadmin.language_code.toLowerCase() + ".json",
                        select: {
                        rows: {
                            _: gettext("%d rows selected"),
                            0: gettext("Click a row to select it"),
                            1: gettext("1 row selected")
                        }
                    }
                },
                order: datatable_config.get_columns_order(),
                scrollX: true,
                processing: true,
                serverSide: true,
                select: {
                    style: 'multi',
                    selector: 'td:first-child',
                    info: true
                },
                columnDefs: datatable_config.columns_defs,
                initComplete: function () {
                    if (datatable_config.hasOwnProperty("initComplete")) {
                        datatable_config.initComplete()
                    }
                },
            };
        if (datatable_config.hasOwnProperty("buttons")) {

            config.dom = "<'card card-body bg-secondary'<'row justify-content-start align-items-center '<'col-auto'B><'col-auto col-xl col-xxl-auto'l><'col-12 d-xl-none'<'border-top my-2 my-md-3'>><'col-auto'f>>>" +
                "<'row mt-3'<'col-12'rt>>" +
                "<'row align-items-center'<'col-12 col-xl'i><'col-12 col-xl-auto'p>>";
            config.buttons = datatable_config.buttons
        }
        var table = this.DataTable(config);
        this.data("table", table);
        return table;
    }
})(jQuery);