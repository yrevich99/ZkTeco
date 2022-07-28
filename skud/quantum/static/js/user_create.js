
jQuery(document).ready(function($){
    
    $("#right").on('click', function(){
        var values = [];
        
        $('[name="access_list"]:checked').each(function(){
            values.push($(this).attr('id'));
            $('#table2').append( $(this).parent());
            $(this).attr('name', 'access');
            $(this).siblings('input').attr('name', 'access');
        });
    });

    $("#left").on('click', function(){
        var values = [];
        $('[name="access"]:checked').each(function(){
            values.push($(this).attr('id'));
            $('#table1').append( $(this).parent());
            $(this).attr('name', 'access_list');
            $(this).siblings('input').attr('name', 'access_list');
        });
    });
});
