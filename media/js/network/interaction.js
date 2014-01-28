function capitalise(value) { return (typeof value == 'string') ? value.charAt(0).toUpperCase() + value.slice(1) : value ;}
function isNumber(n) { return !isNaN(parseFloat(n)) && isFinite(n); }

function stringify(value) {
    if (!(typeof value == 'object')) {return value};
    var n = [];
    for (var key in value) {
        if (key != 'model') {
            var val = value[key];
            n.push('<span class="'+key+'">' + key.toString() + ': ' + (!isNaN(val) && val.toString().indexOf('.') != -1 ? parseFloat(val).toFixed(1).toString() : val.toString()) + '</span>');
        }
    }
    return n.join(', ');
}

function show_msg(title, content, mode) {

    $( "#dialog-msg #dialog-msg-title" ).html(title);
    $( "#dialog-msg #dialog-msg-content" ).html(content);
    $( "#dialog-msg .button").addClass('hide fade');
    $( "#dialog-msg").find("#dialog-msg-"+ mode).removeClass('hide fade');
    $( "#dialog-msg" ).modal();
}

function active_buttons() {
    $("#layout-option-content #nodes-display").find("#input").addClass( (options.layout.nodes.display.input ? "active" : ""));
    $("#layout-option-content #nodes-display").find("#neuron").addClass((options.layout.nodes.display.neuron ? "active" : ""));
    $("#layout-option-content #nodes-display").find("#output").addClass((options.layout.nodes.display.output ? "active" : ""));

    $("#layout-option-content #links-display").find("#pre").addClass((options.layout.links.display.pre ? "active" : ""));
    $("#layout-option-content #links-display").find("#post").addClass((options.layout.links.display.post ? "active" : ""));
    $("#layout-option-content #links-weight-display").find((options.layout.links.display.weight ? "#true" : "#false")).addClass("active");
    $("#layout-option-content #links-curve").find("#" + options.layout.links.curve).addClass("active");

    if (data.spike_detector.meta.neurons.length > 0) {
        $("#spike_detector #binwidth").find("button[value=" + options.histogram.binwidth + "]").addClass("active");
        if (options.correlation.neuronA < data.spike_detector.meta.neurons.length) {
            $("#correlated_neurons #neuronA").find(".title").html("Neuron " + data.spike_detector.meta.neurons[options.correlation.neuronA].id);
        } 
        if (options.correlation.neuronB < data.spike_detector.meta.neurons.length) {
            $("#correlated_neurons #neuronB").find(".title").html("Neuron " + data.spike_detector.meta.neurons[options.correlation.neuronB].id);
        }
    }
}

function tabulate(reference, data, columns, prefixes) {
    var table = d3.select(reference);

    table.html('');

    var thead = table.append("thead"),
        tbody = table.append("tbody");

    // append the header row
    thead.append("tr")
        .selectAll("th")
        .data(columns)
        .enter()
        .append("th")
            .attr('class', function(column) {return prefixes[1]+ ('id' in data ? data[columns.indexOf(column)-1].id : column) ;})
            .text(function(column) { return capitalise(column); });

    // create a row for each object in the data
    var rows = tbody.selectAll("tr")
        .data(data)
        .enter()
        .append("tr")
        .attr('id', function(d) {return prefixes[0]+d.id});

    // create a cell in each row for each column
    var cells = rows.selectAll("td")
        .data(function(row) {
            return columns.map(function(column) {
                return {column: column, value: row[column]};
            });
        })
        .enter()
        .append("td")
        .attr('class', function(d) {return prefixes[1]+d.column})
            .html(function(d) { return stringify(d.value); });
    
    return table;
}

function update_links() {

    // CLEAR TABLES
    $("#nodes-table .targets").empty();
    $("#connection_matrix tr").each(function() {return $(this).find("td:not(:first)").empty()});

    // TEXT WEIGHTS AND DELAY IN CONNECTION TABLE
    var posts = {};
    links.map(function(link) {
        $("#weights-table tr#source_" + link.source.id).find("td.target_" + link.target.id).text(link.weight);
        $("#delays-table tr#source_" + link.source.id).find("td.target_" + link.target.id).text(link.delay);

        // ADD TARTETS FOR TARGETS COLUMN
        if (link.source.id in posts) {
            posts[link.source.id].push({id: link.target.id, weight: link.weight, delay: link.delay});
        } else {
            posts[link.source.id] = [{id: link.target.id, weight: link.weight, delay: link.delay}]
        }
    })

    // TEXT TARGETS IN NODES TABLE
    for (var source in posts) {
        var post = posts[source].sort(function(a,b) {return a.id - b.id});

        $("#nodes-table tr#node_" + source).find("td.node_targets").text(post.map(function(p) {return p.id}).join(', '));
        $("#nodes-table tr#node_" + source).find("td.node_weights").text(post.map(function(p) {return p.weight}).join(', '));
        $("#nodes-table tr#node_" + source).find("td.node_delays").text(post.map(function(p) {return p.delay}).join(', '));

    }

    // ADD CLASSES
    nodes.map(function(node) {
        $("#nodes-table").find("tr#node_" + node.id).addClass(node.type).addClass(node.status.model);
        $("#connection_matrix").find("tr#source_" + node.id).addClass(node.type).addClass(node.status.model);
        $("#connection_matrix").find("td.target_" + node.id).addClass(node.type).addClass(node.status.model);
        $("#connection_matrix").find("th.target_" + node.id).addClass(node.type).addClass(node.status.model);
    })

    for (var type in options.layout.nodes.display) {
        if (!options.layout.nodes.display[type]) {
            $("#connection_matrix tr." + type).addClass("hide fade");
            $("#connection_matrix td." + type).addClass("hide fade");
            $("#connection_matrix th." + type).addClass("hide fade");
        }
    }

};

function highlight_selected() {

    $("#nodes-table tr").removeClass('active');
    $("#connection_matrix tr").removeClass('active');
    $("#connection_matrix th").removeClass('active');
    $("#connection_matrix td").removeClass('active');

    if (selected_node) {
        $("#nodes-table").find("tr#node_" + selected_node.id ).addClass('active');
        $("#connection_matrix").find("tr#source_" + selected_node.id ).addClass(options.layout.links.display.post ? 'active': '');
        $("#connection_matrix").find("th.target_" + selected_node.id ).addClass(options.layout.links.display.pre ? 'active': '');
        $("#connection_matrix").find("td.target_" + selected_node.id ).addClass(options.layout.links.display.pre ? 'active': '');
    } else if (selected_link) {
        $("#connection_matrix").find("tr#source_" + selected_link.source.id ).find( "td.target_" + selected_link.target.id ).addClass('active');
    }

};

function show_form(model) {
    // Hide and fade portlet, fields and buttons
    $("#node-form").parent().addClass('hide fade');
    $("#node-form .fieldWrapper").addClass('hide fade');
    $("#node-form .btn-group").addClass('hide fade');
    $("#node-form").parent().addClass('hide fade'); 
    $("#node-form #id_model option").addClass('hide fade');
    $('#node-form').find(".alert").remove();

    $("#link-form").parent().addClass('hide fade');
    $('#link-form').find(".alert").remove();

    // Empty fields and remove selected model;
    $("#node-form input").val('');

    if (selected_node) {
        if (selected_node.type == 'output') return;

        var status = selected_node.status;
        selected_model = (model == null ? status.model : model)

        for (var key in status) {
            key != 'model' ? $("#node-form").find("#id_"+key).val(status[key]) : '';
        }

        $("#node-form #id_model #" + selected_model).prop('selected', true).parents(".fieldWrapper").removeClass('hide fade');
        if (SPIC_group == 1) {
            $("#node-form #id_model option."+selected_node.type).removeClass('hide fade');
        } else {
            $("#node-form #id_model option").removeClass('hide fade');
        }

        // hide output models if existed in nodes
        nodes.forEach(function(node) {
            if (node.type == 'output') {
                $("#id_model #"+ node.status.model).addClass('hide fade');
            }
        })


        $("#node-form").find("."+ selected_model).parents(".fieldWrapper").removeClass('hide fade');
        $("#node-form .btn-group").removeClass('hide fade');
        $("#node-form").parent().removeClass('hide fade');

        if (selected_node.disabled == 1) {
            $("#node-form input.neuron").prop('disabled', true);
            $("#node-form #id_model").parents(".fieldWrapper").addClass('hide fade');
            $("#node-form .btn-group").addClass('hide fade');
        }

    } else if (selected_link) {
        $("#link-form").find("#id_weight").val(selected_link.weight);
        $("#link-form").find("#id_delay").val(selected_link.delay);
        $("#link-form").parent().removeClass('hide fade');
        $("#link-form input").prop('disabled', false);
        $("#link-form .btn-group").removeClass('hide fade');

        if (selected_link.source.disabled != 0 && selected_link.target.disabled != 0) {
                $("#link-form input").prop('disabled', true);
                $("#link-form .btn-group").addClass('hide fade');
            }
    }
}

function update_selected_node(reference, object) {
    var ref_obj = d3.select(reference);
    ref_obj.selectAll(object).classed('active', selected_node != null)
    ref_obj.selectAll(object).classed('selected', false)
    ref_obj.selectAll(object).classed('compared', false)

    if (selected_node) {
        ref_obj.select("#neuron_"+selected_node.id.toString()).classed('selected', true)
        if (compared_node) { ref_obj.select("#neuron_"+compared_node.id.toString()).classed('compared', true)};
    }
}


function update_after_select() {
    update_layout();
    highlight_selected();
    show_form(null);

    if (data.spike_detector.meta.neurons.length > 0) {
        update_selected_node("g.smoothed_histogram", "path");
        update_correlation("#correlation_plot");
    }
    if (data.voltmeter.meta.neurons.length > 0) { update_selected_node("g.voltmeter", "path"); }
}

function node_interaction() {
    var id = $(this).attr('id').substring(5);

    selected_node = nodes.filter(function(n) {
        return (n.id == id);
    })[0];
    selected_link = null;
    update_after_select();
}

function node_connection_interaction() {
    var id = $(this).parent().attr('id').substring(7);

    selected_node = nodes.filter(function(n) {
        return (n.id == id);
    })[0];
    update_after_select();
}

function link_interaction_click() {
    var source_id = $(this).parent().attr('id').substring(7);
    var target_id = $(this).attr('class').substring(7,9);

    selected_link = links.filter(function(l) { return (l.source.id == source_id && l.target.id == target_id); })[0];

    selected_node = null;
    update_after_select();
}

function link_interaction_dblclick() {

    var source_id = $(this).parent().attr('id').substring(7);
    var target_id = $(this).attr('class').substring(7,9);

    selected_link = links.filter(function(l) { return (l.source.id == source_id && l.target.id == target_id); })[0];

    if (selected_link) {
        if (SPIC_group && selected_link.source.type == 'neuron' && selected_link.target.type == 'neuron') return;
        links.splice(links.indexOf(selected_link), 1);
        selected_link = null;
    } else {
        source = nodes.filter(function(n) { return (n.id == source_id); })[0];
        target = nodes.filter(function(n) { return (n.id == target_id); })[0];

        if (SPIC_group == 1 && source.type == 'neuron' && target.type == 'neuron') return;
        if ((source.type == 'input' || source.type == 'output') && target.type == 'output') return;

        selected_link = {source: source, target: target, weight: source.synapse == 'excitatory' || source.type == 'input' || target.type == 'output' || source.type == 'output' ? 1 : -1 , delay:1};
        links.push(selected_link);
    }

    selected_node = null;
    update_after_change();
}


function update_after_change() {

   update_layout();

   tabulate('#nodes-table', nodes, ['id', 'label', 'targets', 'status'], ['node_', 'node_'])
   tabulate('#weights-table', nodes.map(function(node) {return {id: node.id} }), ['id'].concat(nodes.map(function(node) {return node.id })), ['source_', 'target_'])
   tabulate('#delays-table', nodes.map(function(node) {return {id: node.id} }), ['id'].concat(nodes.map(function(node) {return node.id })), ['source_', 'target_'])

   update_links();
   highlight_selected();
   show_form(null);

    $('#nodes-table tr').click(node_interaction)
    $('#connection_matrix td.target_id').click(node_connection_interaction)
    $('#connection_matrix td:not(.target_id)').click(link_interaction_click)
    $('#connection_matrix td:not(.target_id)').dblclick(link_interaction_dblclick)
}

function node_form_validation(formData, jqForm, options) { 
    // jqForm is a jQuery object which wraps the form DOM element 
    // 
    // To validate, we can access the DOM elements directly and return true 
    // only if the values of both the username and password fields evaluate 
    // to true 

    $('#node-form').find(".errorlist").remove();
    $('#node-form').find(".text-warning").remove();

    var error_prefix = '<ul class="errorlist"><li>';
    var error_suffix = '</li></ul>';

    var status = {'model': $("#node-form #id_model :selected").val()};
    var clean = true;
    $('#node-form').find('input:visible').each(function () {
        var error_msg;

        if ($(this).val() != '') {

            if ( !(isNumber( $(this).val() )) ) {
                error_msg = 'Enter a valid number value.';
            } else if ( ($(this).hasClass('positive')) && (parseFloat($(this).val()) < 0.0) ) {
                error_msg = 'Enter a valid positive value.';
            } else if ( ($(this).hasClass('nonzero')) && (parseFloat($(this).val()) == 0.0) ) {
                error_msg = 'Enter a valid nonzero value.';
            } else if ( $(this).hasClass('limit') ) {
                var classes = $(this).attr("class").split(' ');

                if (classes.indexOf('max')) {
                    var val_max = parseFloat(classes[classes.indexOf('max')+1]);
                    if (parseFloat($(this).val()) > val_max) {
                        error_msg = 'Enter a valid value that is smaller than ' + val_max +'.';
                    }
                }

                if (classes.indexOf('min')) {
                    var val_min = parseFloat(classes[classes.indexOf('min')+1]);
                    if (parseFloat($(this).val()) < val_min) {
                        error_msg = 'Enter a valid value that is greater than ' + val_min +'.';
                    }
                }
            }

            if (error_msg == null) {
                status[$(this).attr('id').substr(3)] = parseFloat($(this).val());
            }

        } else if ($(this).hasClass('required')) {
            error_msg = 'This field is required.';

        }

        if (!(error_msg == null)) {
            $(this).parents('.controls').append(error_prefix + error_msg + error_suffix);
            clean = false;
        }

    })

    if (clean) {
        selected_node.status = status;
        selected_node.label = $("#node-form #id_model :selected").text()
        selected_node.disabled = 0;
        if (status.model.indexOf("meter") != -1 || status.model.indexOf('detector') != -1) {
            selected_node.type = 'output'
            if ('synapse' in selected_node) {delete selected_node["synapse"];}
        } else if (status.model.indexOf("generator") != -1) {
            selected_node.type = 'input'
            if ('synapse' in selected_node) {delete selected_node["synapse"];}
        } else {
            selected_node.type = 'neuron';
            selected_node.synapse = 'excitatory';
        }

        link_validation();
        update_after_change();
    } else {
        $('#node-form .portlet-body').prepend('<h4 class="text-warning" style="margin:10px">Oh snap! You got an error!</h4>')
    }

    return false;
}

function link_form_validation(formData, jqForm, options) { 
    // jqForm is a jQuery object which wraps the form DOM element 
    // 
    // To validate, we can access the DOM elements directly and return true 
    // only if the values of both the username and password fields evaluate 
    // to true 

    $('#link-form').find(".errorlist").remove();
    $('#link-form').find(".text-warning").remove();

    var error_prefix = '<ul class="errorlist"><li>';
    var error_suffix = '</li></ul>';

    var synapse = selected_link.source.synapse;

    var weight_val = $('#link-form').find('input#id_weight').val();
    var weight_error_msg;
    if ( weight_val == '' ) {
        weight_val = (synapse == 'excitatory' ? 1.0 : -1.0) ;
    } else if ( !(isNumber( weight_val )) ) {
        weight_error_msg = 'Enter a valid number value.';
    } else if (parseFloat(weight_val) < 0.0 && synapse == 'excitatory' && selected_link.source.type == 'neuron') {
        weight_error_msg = 'This neuron contains only excitatory synapses.\n Enter a positive value.';
    } else if (parseFloat(weight_val) < 0.0 && (selected_link.target.type == 'output' || selected_link.source.type == 'output')) {
        weight_error_msg = 'The output device accepts only positive weight.\n Enter a positive value.';
    } else if (parseFloat(weight_val) > 0.0 && synapse == 'inhibitory'  && selected_link.source.type == 'neuron' && selected_link.target.type != 'output') {
        weight_error_msg = 'This neuron contains only inhibitory synapses.\n Enter a negative value.';
    }
    if (!(weight_error_msg == null)) {$('#link-form').find('#id_weight').parents('.controls').append(error_prefix + weight_error_msg + error_suffix);}

    var delay_val = $('#link-form').find('input#id_delay').val();
    var delay_error_msg;
    if ( delay_val == '' ) {
        delay_val = 1.0;
    } else if ( !(isNumber( delay_val )) ) {
        delay_error_msg = 'Enter a valid positive value.';
    } else if (parseFloat(delay_val) < 0.0) {
        delay_error_msg ='Delay value cannot be negative.<br> Enter a positive value.';
    } else if (parseFloat(delay_val) >= 10.0) {
        delay_error_msg = 'Delay value is too large.\n Enter a value that is smaller than 10 ms.';
    }
    if (!(delay_error_msg == null)) {$('#link-form').find('#id_delay').parents('.controls').append(error_prefix + delay_error_msg + error_suffix);}

    if (weight_error_msg == null && delay_error_msg == null) {
        selected_link.weight = parseFloat(weight_val);
        selected_link.delay = parseFloat(delay_val);
        update_after_change();
    } else {
        $('#link-form .portlet-body').prepend('<h4 class="text-warning" style="margin:10px">Oh snap! You got an error!</h4>')
    }

    return false;
}


function link_validation() {
    var links_copy = links.slice();
    var invalid_links = new Array();
    var warning = false;

    for (var link_idx in links_copy) {
        if ((links_copy[link_idx].source.status.model == 'spike_detector')
        || (links_copy[link_idx].target.status.model == 'voltmeter')
        || (links_copy[link_idx].target.type == 'input')) {
            invalid_links.push(links.splice(links.indexOf(links_copy[link_idx]), 1)[0]);
            warning = true;
        }
    }
    if (warning) {
        $( "#global_warning .alert-content").html('<b>Attention!</b> All invalid links had to been deleted.<ul class="invalid_links"></ul>');
        for (var link_idx in invalid_links) {
            $( "#global_warning .invalid_links").append('<li>Link from ' + invalid_links[link_idx].source.id + ' to ' + invalid_links[link_idx].target.id + '</li>');
        }
        $( "#global_warning").removeClass("hide fade");
    }
}

