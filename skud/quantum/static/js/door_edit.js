$(function () {

    /* Functions */

    var loadForm = function () {
        var btn = $(this);
        $.ajax({
        url: btn.attr("data-url"),
        type: 'get',
        dataType: 'json',
        beforeSend: function () {
            $("#modal-door").modal("show");
        },
        success: function (data) {
            $("#modal-door .modal-content").html(data.html_form);
        }
        });
    };

    var saveForm = function () {
        var form = $(this);
        $.ajax({
        url: form.attr("action"),
        data: form.serialize(),
        type: form.attr("method"),
        dataType: 'json',
        success: function () {
            
            // $("#department-table ol").html(data.html_department_list);
            // console.log('data :>> ', data);
            $("#modal-door").modal("hide");
            location.reload(); 
            // $("#modal-door .modal-content").html(data.html_form);
        }
        });
        return false;
    };


    /* Binding */

    // Create book
    $(".js_door_setting").click(loadForm);
    $("#modal-door").on("submit", ".js_door_create", saveForm);
});
