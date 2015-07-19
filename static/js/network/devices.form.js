function device_list_preview (idx, status) {
    var model = status['model'].replace("_", " ");

    var title = [];
    for (var statusKey in status) {
        title.push(statusKey +": "+ status[statusKey].toString())
        }

    // Add new device to the list
    if (idx == -1) {
        var device = $( "#device-table > tbody tr:last" );
        $(device).after( $(device).clone() );
        $(device).attr('id', "device_"+ selected_device_id).addClass('enabled');

        $(device).find( "td.id" ).html(selected_device_id).end()
            .find(" td.model" ).html(model);

        var term = 'added';
        last_device_id++;
    } else {
        var device = $( "#device_"+ idx );
        var term = 'changed';
    }

    if ('targets' in status) { $(device).find( "td.targets" ).html(status['targets'])}
    else if ('sources' in status) { $(device).find( "td.targets" ).html(status['sources'])};

    if ('weight' in status) {$(device).find( "td.weight" ).html(status['weight'])}
    if ('delay' in status) {$(device).find( "td.delay" ).html(status['delay'])};

    $(device).attr('title', title.join(", ")).fadeIn().tipTip({defaultPosition: 'right',});

    result_id = 0;
    $( "#device-message" ).html("<li>"+ model +" ["+ selected_device_id +"] was "+ term +" successfully.</li>");
    $( "#device-list" ).find( ".portlet-content" ).show();
};


$( "form.device-form" ).on('submit',  function(e) {
    e.preventDefault();
    var form_content = $( this ).find( ".form-content" );
    var form_data = $( this ).serialize();
    $.post('/network/ajax/' + network_id +'/device_preview/',
        form_data.concat('&neuron_ids='+ JSON.stringify(neuron_ids)), function(data){
            if (data.valid == -1) {
                $(form_content).html(data.responseHTML);
            } else {
                $( "ul.errorlist" ).remove();
                if ($( "select#id_model" ).val() == 'voltmeter' || $("select#id_model" ).val() == 'spike_detector') {
                    $( "select#id_model option:selected" ).hide()
                };
                $( "option:first" ).attr('selected', 'selected');

                var status = data.status,
                statusJSON = data.statusJSON;

                if (status["type"] == 'output') {
                    if ("targets" in status) {
                        connect_to_output.push(status["targets"]);
                    } else {
                        connect_to_output.push(status["sources"]);
                    };
                } else if (status["type"] == 'input') {
                    connect_to_input.push(status["targets"]);
                } else if (status["type"] == 'neuron') {
                    neuron_ids.push(status["id"])
                }

                if (selected_device_id > device_list.length || selected_device_id > last_device_id) {
                    device_list.push(status);
                } else {
                    position = device_list[data.idx]["position"];
                    status["position"] = position;
                    device_list[data.idx] = status;
                };
                
                device_list_preview(data.idx, JSON.parse(statusJSON));
            };
    }, 'json');
});

$( "#id_step" ).on('keyup', function() {
    var step = parseFloat(this.value);
    var spike_times = [];
    if (step > 0) {
        var start = $(this).parents( ".form-content" ).find( "#id_start" ).val();
        var stop = $(this).parents( ".form-content" ).find( "#id_stop" ).val();
        if (stop == 'inf') {
            stop = simulation_stop;
        }
        var spike_times = [];
        for (var tt = parseFloat(start); tt <= parseFloat(stop); tt += step) {
            spike_times.push(tt);
        };
    };
    $(this).parents( ".form-content" ).find( "#id_spike_times" ).val(spike_times.toString());

});

$( ".required input" ).on('change', function() {
    if (this.value == '') {
        $(this).parent(".field-box").addClass('red');
    } else {
        $(this).parent(".field-box").removeClass('red');
    }
});
