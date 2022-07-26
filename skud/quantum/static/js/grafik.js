jQuery(document).ready(function($){
    $.ajax({
        url: 'grafik/new',
        type: 'GET',
        dataType: 'json',
        success: function(data){smenaRow(data)},
        
    });
    var smena_row = '';
    var smena_data;
    var grafik;
    
    

    function smenaRow(data){
        smena_data = data.smena_data;
        grafik = data.grafik;
        console.log('grafik :>> ', grafik);
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
        if(row_col <= 0)
            return alert('Минимальное значение 1');
        
        $('#grafic_table').empty();
        for(var i = 0; i < row_col; i++){
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

    
    
    $('#added_grafik td').click(function(){
        var cells=$(this).parent('tr').children('td');
        $('#grafik_name').val($(cells[0]).text().trim());
        $('#row_col').val($(cells[1]).text().trim());
        var row_col = document.getElementById('row_col').value;
        var grafik_val;

        for(var i = 0; i<grafik.length; i++){
            if (grafik[i]['grafik_name'] == $(cells[0]).text().trim()) 
                grafik_val = grafik[i]
        };
        $('#grafik_id').val(grafik_val['id']);
        var grafik_smena = grafik_val['smena'].split(',').map(Number);
            $('#grafic_table').empty();
            for(var i = 0; i < row_col; i++){
                var smena_id = smena_time(grafik_smena[i])
                if(smena_id){
                    var td = `<tr>
                            <td>${document.getElementById('grafik_name').value}</td>
                            <td>${smena_id[1]}</td>
                            <td>${smena_id[2]}</td>
                            <td>${smena_id[3]}</td>
                            <td>${smena_id[4]}</td>
                            <td>
                                <select class="form-select" name="filter_${i}" required>
                                    <option value="${smena_id[5]}">Выберите смену</option>
                                    ${smena_row}
                                </select>
                        </td>
                        </tr>`; 
                    $('.tbody').append(td);
                }
                else{
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
    });


    $( "#row_col" ).keyup(function() {
        grafikRow();
    });
    
    $( "#grafik_name" ).keyup(function() {
        grafikRow();
    });
});

