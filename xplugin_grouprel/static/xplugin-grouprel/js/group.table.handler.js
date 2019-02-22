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
        buttons: grouprel_datatable.buttons,
        initComplete: function () {
            if (grouprel_datatable.hasOwnProperty("initComplete")) {
                grouprel_datatable.initComplete()
            }
        },
    });
})(jQuery);