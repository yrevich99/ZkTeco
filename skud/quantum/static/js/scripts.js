// function exportTableToExcel(){
//     let tab_text = document.getElementById('exelTable'); // id of table

//     TableToExcel.convert(tab_text, { // html code may contain multiple tables so here we are refering to 1st table tag
//         name: $("#filter option:selected").text() + '.xlsx', // fileName you could use any name
//         sheet: {
//             name: $("#filter option:selected").text() + '.xlsx' // sheetName
//         }
//     });
// }

var language = {
    "lengthMenu": "Показывать _MENU_ строк",
    "zeroRecords": "Ничего не нашлось",
    "infoEmpty": "Показано с 0 по 0 из 0 элементов",
    "info": "Показано с _START_ по _END_ из _TOTAL_ элементов",
    "search":         "Поиск:",
    "infoFiltered": "(Найдено _MAX_ количество записей)",
    // "searchPanes": "Фильтр",
    "paginate": {
        "first":      "Первая",
        "last":       "Последняя",
        "next":       "Следующая",
        "previous":   "Предыдущая"
    },
}

// window.$('#exelTable').DataTable();
$(document).ready(function () {
    $('#exelTable').DataTable( {
        buttons: [
            {
                extend: 'searchPanes',
                config: {
                    cascadePanes: true
                },
            }, 
            { extend: 'excel', text: 'Сохранить в Exel' },
            { extend: 'print', text: 'Печатать' },
        ],
        dom: 'Bfrtip',
        "language": language,
        colReorder: {
            realtime: true
        },
        // autoFill: true,
        fixedHeader: true,
        // rowReorder: true,
        deferRender: true,
        scrollY: 800,
        responsive: true,
        // // scrollX: true,
        scrollCollapse: true,
        // "paging": false,
        select: {
            info: false
        }
        
    } );
});



// var table = $('#exelTable').DataTable( {
//     buttons: [
//         'excel'
//     ]
// } );
  
// table.buttons().container()
//     .appendTo( '#buttonExel' );


// $(document).ready(function () {
//     var table = $('#UsersTable').DataTable( {
//         dom: 'Bfrtip',
//         "language": language,
//         buttons: [
//         'copy', 'excel', 'pdf'
//         ],
//         colReorder: {
//             realtime: true
//         },
//         fixedHeader: true
//     } );

//     table.buttons().container()
//         .appendTo( $('.col-sm-6:eq(0)', table.table().container() ) );
// });

$(document).ready(function () {
    $('#UsersTable').DataTable( {
        buttons: [
            {
                extend: 'searchPanes',
                config: {
                    cascadePanes: true
                },
            }, 
            { extend: 'excel', text: 'Сохранить в Exel' },
            { extend: 'print', text: 'Печатать' },
        ],
        dom: 'Bfrtip',
        "language": language,
        colReorder: {
            realtime: true
        },
        // autoFill: true,
        fixedHeader: true,
        // rowReorder: true,
        deferRender: true,
        responsive: true,
        scrollY:     800,
        scrollCollapse: true,
        "paging": false,
        // select: {
        //     info: false
        // }
        
    } );
});

var alertList = document.querySelectorAll('.alert')
alertList.forEach(function (alert) {
    new bootstrap.Alert(alert)
})

