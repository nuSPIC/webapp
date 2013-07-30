function connect_to_output(element, index, array) {
    return (element.source.type == 'output' || element.target.type == 'output')
}

function connect_to_input(element, index, array) {
    return (element.source.type == 'input' || element.target.type == 'input')
}

// LOOPING REQUEST FOR SIMULATION PROGRESS
function check_task_status(task_id) {
    $.getJSON('/status/'+task_id+'/?', function(data) {
            var task = data['task'];
            var status = task['status'];

            $( "#dialog-msg #dialog-msg-title" ).html('Simulation info')
            $( "#dialog-msg .msg-content" ).html('Simulation is running.<p>Loading... please wait.</p>')
            $( "#dialog-msg a" ).addClass('hide fade');
            $( "#dialog-msg #task_status" ).html(status);
            $( "#dialog-msg" ).modal();

            if (status == 'PENDING') {
                window.setTimeout(function() {check_task_status(task_id)}, 2000);
            } else {
                if (status == 'ABORTED') {
                    alert(task_status)
                } else if (status == 'FAILURE') {
                    alert(task_status)
                }

                window.setTimeout(function() {
                    result = task['result']
                    window.location.href = '/network/?id='+ result['network_id']
                }, 1000);
            }
    });
};

function simulate() {
    $("#dialog-msg").addClass('hide fade');
    var clean_nodes = nodes.map(function (n) {
        return {
            uid: n.uid, id: n.id,
            label: n.label, type: n.type,
            synapse: n.synapse,
            status: n.status, disabled: n.disabled,
            x: n.x/options.layout.width,
            y: n.y/options.layout.height}
        })

    var clean_links = links.map(function (l) {
        return {
            source: l.source.uid, target: l.target.uid,
            weight: l.weight, delay: l.delay}
        })

    $( "#network-form" ).find("#id_nodes").val(JSON.stringify(clean_nodes));
    $( "#network-form" ).find("#id_links").val(JSON.stringify(clean_links));

    var form = $( "#network-form" ).serialize();
    $( ":input" ).attr("disabled", true);

    $.post('/network/ajax/'+ network_id +'/simulate/',
        form,
        function(data){
            check_task_status(data.task_id);
    }, 'json');
};



$( "form#network-form" ).on('submit',  function(e) {
    e.preventDefault();
    $( "#dialog-msg #dialog-msg-title" ).html('Warning')
    if (links.filter(connect_to_output).length <1) {
        $( "#dialog-msg .msg-content" ).html('No <b>recording device</b> connected. <p>Do you want to continue?</p>');
        $( "#dialog-msg" ).modal();
    } else if (links.filter(connect_to_input).length <1) {
        $( "#dialog-msg .msg-content" ).html('No <b>input device</b> connected. Network may be silent. <p>Do you want to continue?</p>');
        $( "#dialog-msg" ).modal();
    } else if ($( "#id_duration" ).val() > 5000.0) {
        $( "#dialog-msg .msg-content" ).html('The simulation lasts more than 5 seconds and it could have a speed effect on page loading time. <p>Are you sure?</p>')
        $( "#dialog-msg" ).modal();
    } else {
        simulate()
    }
});
