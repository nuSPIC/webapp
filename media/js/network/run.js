$.cookie.json = true;
var options = ($.cookie('options') ? $.cookie('options') :{
    layout: {
        width: 500.0,
        height: 360.0,
        linkDistance: 150.0,
        charge: -500.0,
        links: {
            display: {
                pre: false,
                post: true,
                weight: false,
            },
            curve: 'right',
        },
        nodes: {
            fixed: true,
            display: {
                neuron: true,
                input: true,
                output: true,
                position: false,
            },
        },
    },
    raster_plot: {
        width: 640.0,
        height_per_neuron: 18.0,
    },
    histogram: {
        width: 640.0,
        height: 140.0,
        binwidth: 50.0,
    },
    correlation: {
        width: 640.0,
        height: 140.0,
        neuronA: data.spike_detector.meta.neurons.length > 0 ? data.spike_detector.meta.neurons[0]['id'] : null,
        neuronB: data.spike_detector.meta.neurons.length > 0 ? data.spike_detector.meta.neurons[0]['id'] : null,
    },
    voltmeter: {
        width: 640.0,
        height: 70.0,
    },
});

nodes_uid = []
nodes.forEach(function(node) {
    node.fixed = options.layout.nodes.fixed;
    node.x = node.x * options.layout.width;
    node.y = node.y * options.layout.height;
    nodes_uid.push(node.uid);
});

links.forEach(function(link) {
    link.source = nodes[nodes_uid.indexOf(link.source)];
    link.target = nodes[nodes_uid.indexOf(link.target)];
});

var selected_model = null,
    hasChanged = false,
    lastNodeId = nodes.length > 1 ? nodes[nodes.length-1].id : 0;




$(".font-size").on('click', function(e) {
    $( "#network-content" ).css("font-size", $(this).css("font-size"));
})

$( ".bing" ).on('click', function() {
    $(this).parent().find(".bing").toggleClass('fade hide').parents('.portlet').toggleClass('modal');
});

$( "#toggle-button button" ).on('click', function() {
    $( "div.toggle-content").addClass("hide fade");

    if (!($(this).hasClass('active'))) {
        $( "#toggle-button button").removeClass('active');
        $( this ).addClass('active');
        $( "div.toggle-content" + $(this).attr('href')).removeClass("hide fade");
    } else {
        $( "#toggle-button button").removeClass('active');
    }

    $.cookie('options', options, { expires: 7});
});

$( "button.nodes-display" ).on('click', function() {
    options.layout.nodes.display[$(this).val()] = !(options.layout.nodes.display[$(this).val()])
    update_after_change();
});

$( "button.links-display" ).on('click', function() {
    options.layout.links.display[$(this).val()] = !(options.layout.links.display[$(this).val()])
    update_after_select();
});

$( "button.links-weight-display" ).on('click', function() {
    options.layout.links.display.weight = ($(this).val() == 'true' ? true : false)
    update_after_select();
});

$( "button.links-curve" ).on('click', function() {
    options.layout.links.curve = $(this).val();
    update_after_select();
});


$( "button.node-force" ).on('click', function() {
    var node_id = $(this).val();
    nodes[node_id].fixed = !nodes[node_id].fixed;
    update_after_select();
});

$( "button#node-force-all" ).on('click', function() {
    if ($(this).hasClass('active')) {
        $( "button.node-force" ).removeClass('active');
    } else {
        $( "button.node-force" ).addClass('active');
    }

    for (var i = 0; i < nodes.length; i++) {
        if (nodes[i].type == 'neuron') {
            nodes[i].fixed = $(this).hasClass('active');
        }
    }
    update_after_select();
});

$( "button#save-layout" ).on('click', function(e) {
        e.preventDefault();

//        $.cookie('options', options, { expires: 7});

//        var devices_json = JSON.stringify(device_list);
//        $.post('/network/ajax/'+ network_id  +'/save_layout/',
//                {'csrfmiddlewaretoken': csrf_token, 'devices_json':devices_json, 'nodes': JSON.stringify(nodes)},
//                function(data) {
//                
//        }, 'json');
});

$( "button#default-layout" ).on('click', function(e) {
        e.preventDefault();

        $.getJSON('/network/ajax/'+ network_id  +'/default_layout/',
            function(data) {
                pos = data["pos"];
                pos.map(function(p) {
                    nodes[nodes_uid.indexOf(p[0])]['x'] = p[1][0] * options.layout.width;
                    nodes[nodes_uid.indexOf(p[0])]['y'] = p[1][1] * options.layout.height;
                })

                initiate_layout("#layout-holder");
                update_after_change();
        });
});

$( "#node-add" ).on('change', show_form())

//$( "#node-form" ).on('submit', function(e) {e.preventDefault();})

$('#node-form #id_model').on('change', function() {
    show_form($(this).val());
})

$( "#node-form #id_step" ).on('keyup', function() {
    var step = parseFloat(this.value);
    var spike_times = [];
    if (step > 0) {
        var start = $( "#node-form" ).find( "#id_start" ).val();
        var stop = $( "#node-form" ).find( "#id_stop" ).val();
        if (start == '') {
            start = 0;
        }
        if ((stop == 'inf') || (stop == '')) {
            stop = simulation_stop;
        }
        var spike_times = [];
        for (var tt = parseFloat(start); tt <= parseFloat(stop); tt += step) {
            spike_times.push(tt);
        };
    };
    $(this).parents( "#node-form" ).find( "#id_spike_times" ).val(spike_times.toString());

});


$('#node-form #reset-node-form-button').on('click', function(e) {

     e.preventDefault();
     // stops the form from resetting after this function

     $(this).closest('form').get(0).reset();
     // resets the form before continuing the function

    $("#node-form #id_model #" + selected_model).prop('selected', true);
})

$(document).ready(function() {
    active_buttons();

    initiate_layout("#layout-holder");
    update_after_change();

    $("#voltmeter_holder").empty();
    if (data.voltmeter.meta.neurons.length > 0) {
        for (var i = 0; i < data.voltmeter.V_m.length; i++) {
            draw_voltmeter("#voltmeter_holder", data.voltmeter.times_reduced, data.voltmeter.V_m[i].values_reduced, data.voltmeter.meta.neurons[i].id.toString());
        }
    }

    $( "#voltmeter-holder .voltmeter").addClass('active')

    if (data.spike_detector.meta.neurons.length > 0) {
        draw_spike_detector("#spike_detector");
    }

    $('#node-form').ajaxForm( { beforeSubmit: node_validate } );
    $('#link-form').ajaxForm( { beforeSubmit: link_validate } );

//    $(".add-on").popover({trigger: 'click', content: function() {return $(this).attr('value')}})
});

//window.onbeforeunload = function (e) {
//    if (hasChanged) {
//        var message = "Your confirmation message goes here.",
//        var e = e || window.event;

//        // For IE and Firefox prior to version 4
//        if (e) {
//            e.returnValue = message;
//        }

//        // For Safari
//        return message;
//    }
//};
