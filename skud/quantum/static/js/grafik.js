jQuery(document).ready(function($){
    $.ajax({
        url: 'grafik/new',
        type: 'GET',
        dataType: 'json',
        success: function(data){smenaRow(data)},
        
    });
    var smena_row = '';
    var smena_data;
    


    function smenaRow(data){
        
        smena_data = data.smena_data;
        var counts = 1;
        data.smena.forEach(dates => {
            smena_row += `<option value="${dates.id}" >${dates.smena_name}</option>`
            counts ++;
        });
    }

    function smena_time(name){
        for(var i = 0; i < smena_data.length; i++){
            if(smena_data[i][5] == name){
                return smena_data[i];
            }
        }
    }

    function grafikRow(){
        var row_col = document.getElementById('row_col').value;
        if(row_col > 31)
            return alert('Максимальное значение 31');
        
        $('#grafic_table').empty();
        for(var i = 1; i <= row_col; i++){
            var td = `<tr>
                    <td>${document.getElementById('grafik_name').value}</td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td>
                        <select class="form-select" name="filter_${i}" required>
                            <option value="0">Выберите смену</option>
                            ${smena_row}
                        </select>
                </td>
                </tr>`; 
            $('.tbody').append(td);
        }
        
        
    }

    $(document).on('change', '#grafic_table select', function (e) {
        var optionSelected = $("option:selected", this);
        var valueSelected = this.value;
        var smena = smena_time(valueSelected);
        var tr_elem = this.parentElement.parentElement;
        if(valueSelected != 0){
            for(var i = 1; i<= 4; i++){
                tr_elem.children[i].innerHTML = smena[i];
            };
        }else
        {
            for(var i = 1; i<= 4; i++){
                tr_elem.children[i].innerHTML = "";
            };
        }
        
    });

    $( "#row_col" ).keyup(function() {
        grafikRow();
    });
    
    $( "#grafik_name" ).keyup(function() {
        grafikRow();
    });
});

