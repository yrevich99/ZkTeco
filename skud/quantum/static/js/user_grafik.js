
function add_graph()
{
    var user_list = $('.list-group-item input:checkbox:checked').map((i, el) => el.value).get();
    var graph_id = $('select[name="grafik"]').val();
    var start_time = $('input[name="start_time"]').val();
    var end_time = $('input[name="end_time"]').val();
    var data = {user_list, graph_id, start_time, end_time};
    console.log(data);
    $.ajax({
        url: "/reports/user_grafik",
        type: "POST",
        dataType: "json",
        data: JSON.stringify({data: data,}),
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),  // don't forget to include the 'getCookie' function
        },
        success: (data) => {
            console.log(data);
        },
        error: (error) => {
            console.log(error);
        }
        });
}


    $('select[name="department"]').on('change', function() {
        var department_id = $(this).val();
        $.ajax({
            url: `/reports/user_grafik/${department_id}`,
            type: 'GET',
            dataType: 'json',
            success: function(data){getUserList(data)},
            
        });
    });


    function getUserList(data)
    {
        $('#user_list_graph label').remove();
        console.log(data.graf);
        for (let i = 0; i < data.graf.length; i++) 
        {
            var item = `<label class="list-group-item"><input class="form-check-input mr-1" type="checkbox" id="${data.graf[i][2]}" name="users_list" value="${data.graf[i][2]}"> ${data.graf[i][1]}</label>`;
            $('#user_list_graph').append(item);
        }
    }




function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + "=")) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
        }
        }
    }
    return cookieValue;
    }