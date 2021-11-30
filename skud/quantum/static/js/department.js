// $(function(){

//     $(".js-create-department").click(function(){
//         $.ajax({
//             url: '/department/create',
//             type: 'get',
//             dataType: 'json',
//             beforeSend: function(){
//                 $("#modal-department").modal("show");
//             },
//             success: function(data){
//                 $("#modal-department .modal-content").html(data.html_form);
//             }
//         });
//     });
// });


$("#modal-department").on("submit", ".js-department-create-form", function(){
    var form = $(this);
    $.ajax({
        url: form.attr("action"),
        data: form.serialize(),
        type: form.attr("method"),
        dataType: 'json',
        success: function (data){
            if (data.form_is_valid){
                alert("Отдел создан");
            }
            else {
                $("#modal-department .modal-content").html(data.html_form);
            }
        }
    });
    return false;
});