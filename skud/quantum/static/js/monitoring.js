// $(".js-start-live").click(function () {
//     $.ajax({
//         url: '/live_mode/realtime',
//         type: 'get',
//         dataType: 'json',
//         beforeSend: function () {
//             // alert('Ok');
//         },
//         success: function (data) {
//             console.log(data.real);
//             // $("table_real .row_real").html(data.html_form);
//             let rows = '';
//             data.real.forEach(dates => {
//                 rows += `
//                 <tr>
//                     <td>${dates.time}</td>
//                     <td>${dates.pin}</td>
//                     <td>${dates.surname}</td>
//                     <td>${dates.name}</td>
//                     <td>${dates.card}</td>
//                     <td>${dates.door}</td>
//                     <td>${dates.event}</td>
//                     <td>${dates.entry_exit}</td>
//                     <td>${dates.verify}</td>
//                 </tr>
//                 `
//             });
//             $('.real_table > tbody').append(rows);
//         }
//     });


// });




jQuery(document).ready(function($){
    

var timeId = {};
var counts = 0;
    

var my_ajax_req ={ // создаем экземпляр объекта

    
    // задаем свойства объекта
    updInterval: 3000, // 3 сек. - интервал времени между запросами
    url: `/live_mode/realtime/`, // скрипт который должен отвечать на Ajax запросы
    init:  function(){
        var self = my_ajax_req;
        my_ajax_req.url = `/live_mode/realtime/${$('#dev_ip').val()}`;
        console.log('ip :>> ', this.url);
        timeId[counts] = setInterval($.proxy(my_ajax_req.requestData, my_ajax_req), my_ajax_req.updInterval);
        counts += 1;
        
    },

    requestData: function(){
        var self = my_ajax_req;
        
        // ajax запрос посредством JQuery
        $.ajax({
            url: self.url,
            type: 'GET',
            dataType: 'json',
            success: function(data){ self.update(data)},
            error: function(data){ self.error(data)},
        });
    },

    // метод принимает ответ на Ajax запрос
    update: function(Data){
        var self = my_ajax_req;
        console.log(Data);
        // тут можно дописать логику после получения данных
        console.log(Data.real);
            // $("table_real .row_real").html(data.html_form);
            let rows = '';
            Data.real.forEach(dates => {
                rows += `
                <tr>
                    <td>${dates.time}</td>
                    <td>${dates.pin}</td>
                    <td>${dates.surname}</td>
                    <td>${dates.name}</td>
                    <td>${dates.card}</td>
                    <td>${dates.door}</td>
                    <td>${dates.entry_exit}</td>
                    <td>${dates.event}</td>
                    <td>${dates.verify}</td>
                </tr>
                `
            });
            $('.real_table > tbody').append(rows);
    },

    // метод для обработки ошибок
    error: function(Data){
        var self = my_ajax_req;
        console.log('Failed to get data');
    },
    };

// jQuery(document).ready(function($){
    // var timeId = setInterval(my_ajax_req.requestData, my_ajax_req.updInterval);
    $( ".js-stop-live" ).click(function(){
        for(var i = 0; i<Object.keys(timeId).length; i++){
            clearInterval(timeId[i]);
            console.log('timeId :>> ', timeId[i]);
        };
        
    });
    $( ".js-start-live" ).click(function(){
        my_ajax_req.init(); 
        console.log('timeId :>> ', timeId);
    });

});

