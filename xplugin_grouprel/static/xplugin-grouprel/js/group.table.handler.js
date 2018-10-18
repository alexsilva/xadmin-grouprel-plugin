(function ($) {
    var csrftoken = $.getCookie('csrftoken');
    $('#ajax-table').DataTable({
        "ajax": {
            "url": ajax_table_url,
            "type": "POST",
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        "processing": true,
        "serverSide": true,
    });

})(jQuery);