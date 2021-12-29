
jQuery(document).ready(function($){
    $("#right").on('click', function(){
        var values = [];
        $('[name="first_table"]:checked').each(function(){
            values.push($(this).attr('id'));
            $('#table2').append( $(this).parent());
            $(this).attr('name', 'lock_control');
        });
    });

    $("#left").on('click', function(){
        var values = [];
        $('[name="lock_control"]:checked').each(function(){
            values.push($(this).attr('id'));
            $('#table1').append( $(this).parent());
            $(this).attr('name', 'first_table');
        });
    });
});


