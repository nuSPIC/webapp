// autocomplete input fields with device models
function autocomplete(field) {
    $(field).autocomplete({
        source: devices,
        select: function ( event, ui ) {
            var terms = split(this.value);
            terms.pop();

            // add the selected item
            terms.push( ui.item.value );

            // add device id
            terms.push( $(this).parent().attr('id').split("-")[1] );
            this.value = terms.join('; ');

            var params = params_order[ ui.item.value ]
            params[0] = 'model';
            var keyCSV = params.join('; ')

            $(this).parent().find( "input.deviceCSV" ).attr("title", keyCSV)
            $(this).parent().find( "input.deviceJSON" ).attr("value", CSVtoJSON(keyCSV, this.value)).attr("name", $(this).parent().attr('id'));
            return false;
        }
    });
}

function DicttoCSV(valDict) {
    var keyCSV = new Array(),
    valCSV = new Array(),
    model = valDict['model'];

    for (var key in params_order[model]) {
        if (key in valDict) {
            keyCSV.push(key);
            valCSV.push(valDict[key].toString());
        }
    }

    return {'key': keyCSV, 'value':valCSV}
}

function JSONtoCSV(valJSON) {
    var valDict = JSON.parse(valJSON);
    return DicttoCSV(valDict);
}

function CSVtoJSON(keyCSV, valCSV) {
    var valDict = {};

    var keyList = keyCSV.split(/[\s;]+/);
    var valList = valCSV.split(/;/);

    for (var i=0; i<keyList.length; i++) {
        if (i<valList.length) {
            if (keyList[i] == 'id') {
                valDict[keyList[i]] = parseInt(valList[i])
            } else {
                valDict[keyList[i]] = valList[i].replace(/ /g,"");
            }
        } else {
            valDict[keyList[i]] = ""
        }
    }

    return JSON.stringify(valDict);
}

function setForm(device) {

    $( "#device_id" ).html("");
    $( ".device-form" ).hide();
    $( "#device-form" ).hide();

    // get form and remove its error message
    var form = $( "#"+ device.model );
    $( form ).find( "ul.errorlist" ).remove();

    if ( selected_device_id == device.id ) {

        // clicking same device, do nothing
        selected_device_id = "-1";

    } else {
        $(" #fields div.id_model-" + selected_device_id).find( ".buttonset" ).hide();

        // highlights device row and edit button
        selected_device_id = device.id;

        $( ".id_model-" + selected_device_id).find( ".device_edit" ).addClass( "active" );
        $( "#device_id" ).html(selected_device_id)

        // get reset form and put values in fields
        $( form ).reset();
        var form_content = $( form ).children();

        // write the header of form
        $( "#selected_device_id" ).html(selected_device_id);
        $( "#selected_device_model" ).html(device.model.replace(/_/g, ' '));

        // add model to form
        $( form_content ).find( "#id_model" ).val(device.model);

        // add values to fields and check if this field is required.
        for (var key in device) {
            $( form_content ).find( "#id_"+ key ).val(device[key]).removeClass('ui-state-hover');
        };

        // show form
        $( form ).show();
        $( "#device-form" ).show();
    }


}

// SELECT DEVICE TO CHANGE PARAMETERS
$( "tr.enabled" ).find( "td.selectable" ).on('click', function(e) {
        e.preventDefault();
        $( "#id_model option:first" ).attr('selected', 'selected');
        var device = device_list[$(this).parent( ".enabled" ).attr('id').split("_")[1]];
        setForm(device);
});

// DELETE DEVICE FROM THE TABLE
$( "button#delete_devices_button" ).on('click', function(e) {
        e.preventDefault();
        $( this ).toggleClass( "highlight" )
            if ($( "table#device-table .delete" ).is(":visible") && $( "table#device-table .delete" ).find( "input" ).is(":checked")) {
            $(".devices-form").submit();
        } else {
            $( "table#device-table tr:visible .delete" ).toggle();
        };
});

// SAVE DEVICE FROM TABLE TO SERVER
$( "button#save_devices_button" ).on('click', function(e) {
        e.preventDefault();
        $( "#device-form" ).hide();
        var devices_json = JSON.stringify(device_list);
        $.post('{% url device_commit network_obj.id %}',
                {'csrfmiddlewaretoken':"{{ csrf_token }}", 'devices_json':devices_json},
                function(data) {
                        $( "#dialog-msg p" ).html("Loading... please wait'.");
                        $( "#dialog-msg #loading_icon" ).show();
                        $( "#dialog-msg" ).dialog({
                                height: 150,
                                resizable: false,
                                modal: true,
                        });
                        window.setTimeout(function() {
                            window.location.href = '/network/{{network_obj.SPIC.group}}/{{network_obj.SPIC.local_id}}/'+ data.local_id +'/{{term}}'}, 1000);
        }, 'json');
});

// CSV SAVE
$( "form#device_csv_form" ).on('submit',  function(e) {
    e.preventDefault();

    var form_data = $( this ).serialize();
    var post_data = form_data.concat('&neuron_ids='+ JSON.stringify(neuron_ids));
    $.post('{% url device_csv network_obj.id %}',
        post_data , function(data){
            if (data['valid'] == 1) {
                var current_url =  window.location.href.split('?')[0].split('#');
                window.location.href = current_url[0]
            } else {
                errorsMsg = data['errorsMsg'];
                for (model_id in errorsMsg) {
                    msg = errorsMsg[model_id];
                    for (err in msg) {
                        $( "#id_model-"+ model_id ).find( ".errorlist" ).html("<li>"+err+": "+msg[err]+"</li>")
                    }
                }
            };
        }, 'json');
});

$( ".device_edit" ).on('click', function() {
    var fieldwrapper = $( this ).parents( ".field-wrapper" );
    var valJSON = $( this ).parents( ".field-wrapper" ).find( "input.deviceJSON" ).attr( "value" );

    if (valJSON != '') {
        var valDict = JSON.parse(valJSON);

        setForm(valDict);
    } else {
        alert('this is empty')
    }
    
})

// SELECT A DEVICE TO ADD A NEW NODE
//$( "select#node-add" ).on('change', function(e) {
//        e.preventDefault();
//        $( ".device-form:visible" ).hide();
//        $( "#device-form" ).hide();
//        $( "ul.errorlist" ).remove();

//        selected_device_id = lastNodeId
//        $( "span#device_id" ).html(lastNodeId+1);

//        var device_form = $( "#"+ $(this).val() +"-form" );
//        if ($(this).val() != "") {
////            $( form ).find("input:text").empty();
//            $( device_form ).find( "#selected_device_id" ).html(selected_device_id).end()
//                .find( "#id_model" ).attr('value', $(this).val()).end()
//                .find( "#id_id" ).attr('value', selected_device_id).end()
//                .show();

//            $( "#device-form" )
//                .find( "#title-device-id" ).html(selected_device_id).end()
//                .find( "#title-device-label" ).html($(this).find(":selected").html()).end()
//                .show();
//        }
//});
