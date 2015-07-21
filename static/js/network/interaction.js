function capitalise(value) { return (typeof value == 'string') ? value.charAt(0).toUpperCase() + value.slice(1) : value };

function stringify(value) {
    if (!(typeof value == 'object')) {return value};
    var n = [];
    for (var key in value) {
        if (key != 'model') {
            var val = value[key];
            n.push('<span class="'+key+'">' + key.toString() + ': ' + (!isNaN(val) && val.toString().indexOf('.') != -1 ? parseFloat(val).toFixed(1).toString().slice(0,10) : val.toString().slice(0,10)) + '</span>');
        }
    }
    return n.join(', ');
};

function show_msg(title, content, mode) {
    var dialog_msg = $( "#dialog-msg");
    dialog_msg.find("#dialog-msg-title" ).html(title);
    dialog_msg.find("#dialog-msg-content" ).html(content);
    dialog_msg.find(".button").addClass('hide fade');
    dialog_msg.find("#dialog-msg-"+ mode).removeClass('hide fade');
    dialog_msg.modal('show');
};

function active_buttons() {
    var layout_option_content = $("#layout-option-content");

    layout_option_content.find("#nodes-display #input").addClass( (options.layout.nodes.display.input ? "active" : ""));
    layout_option_content.find("#nodes-display #neuron").addClass((options.layout.nodes.display.neuron ? "active" : ""));
    layout_option_content.find("#nodes-display #output").addClass((options.layout.nodes.display.output ? "active" : ""));

    layout_option_content.find("#links-display #pre").addClass((options.layout.links.display.pre ? "active" : ""));
    layout_option_content.find("#links-display #post").addClass((options.layout.links.display.post ? "active" : ""));
    layout_option_content.find("#links-weight-display" +(options.layout.links.display.weight ? "#true" : "#false")).addClass("active");
    layout_option_content.find("#links-curve #" + options.layout.links.curve).addClass("active");

    if (data.spike_detector.meta.neurons.length > 0) {
        $("#spike_detector #binwidth").find("button[value=" + options.histogram.binwidth + "]").addClass("active");
        if (options.correlation.neuronA < data.spike_detector.meta.neurons.length) {
            $("#correlated_neurons #neuronA").find(".title").html("Neuron " + data.spike_detector.meta.neurons[options.correlation.neuronA].id);}
        if (options.correlation.neuronB < data.spike_detector.meta.neurons.length) {
            $("#correlated_neurons #neuronB").find(".title").html("Neuron " + data.spike_detector.meta.neurons[options.correlation.neuronB].id);}
    }
};

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
};

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
    var model_choice = $("#div_id_model");
        synapse_choice = $("#div_id_synapse");

    // hide form
    node_form.addClass('hide fade');
    node_form.find(".form-group").addClass('hide fade');
    node_form.find(".form-actions").addClass('hide fade');
    model_choice.find("option").addClass('hide fade');
    link_form.addClass('hide fade');

    clear_form(node_form)
    clear_form(link_form)

    node_form.find("input").val('');

    if (selected_node) {
        if (selected_node.type == 'output') return;

        var status = selected_node.status;
        selected_model = (model == null ? status.model : model)

        for (var key in status) {
            key != 'model' ? node_form.find("#id_"+key).val(status[key]) : '';
        };

        // Display model choice
        model_choice.find("#" + selected_model).prop('selected', true).parents("#div_id_model").removeClass('hide fade');
        if (SPIC_group == 1) {
            model_choice.find("option."+selected_node.type).removeClass('hide fade');
        } else {
            model_choice.find("option").removeClass('hide fade');
        };
        node_form.find("#id_model").val(selected_model);

        // Display synapse choice
        if (SPIC_group != 1 && selected_node.type == 'neuron') {
            synapse_choice.find("#" + selected_node.synapse).prop('selected', true);
            synapse_choice.removeClass('hide fade');
        }

        // Display model choice if neuron not selected
        if (selected_node.type != 'neuron') {
            model_choice.removeClass('hide fade');
        }

        // hide output models if existed in nodes
        nodes.forEach(function(node) {
            if (node.type == 'output') {
                model_choice.find("#"+ node.status.model).addClass('hide fade');
            }
        })

        // display fields for selected node
        node_form.find("."+ selected_model).parents(".form-group").removeClass('hide fade');
        node_form.find(".form-actions").removeClass('hide fade');
        node_form.removeClass('hide fade');

        if (selected_node.disabled == 1) {
            node_form.find("input.neuron").prop('disabled', true);
            model_choice.addClass('hide fade');
            node_form.find(".form-actions").addClass('hide fade');
        }

        model_choice.removeClass('hide fade');

    } else if (selected_link) {
        link_form.find("#id_weight").val(selected_link.weight);
        link_form.find("#id_delay").val(selected_link.delay);
        link_form.find("input").prop('disabled', false);
        link_form.find(".form-actions").removeClass('hide fade');
        link_form.removeClass('hide fade');

        if (selected_link.source.disabled != 0 && selected_link.target.disabled != 0) {
            link_form.find("input").prop('disabled', true);
            link_form.find(".form-actions").addClass('hide fade');
        }
    }
};

function update_selected_node(reference, object) {
    var ref_obj = d3.select(reference);
    ref_obj.selectAll(object).classed('active', selected_node != null)
    ref_obj.selectAll(object).classed('selected', false)
    ref_obj.selectAll(object).classed('compared', false)

    if (selected_node) {
        ref_obj.select("#neuron_"+selected_node.id.toString()).classed('selected', true)
        if (compared_node) { ref_obj.select("#neuron_"+compared_node.id.toString()).classed('compared', true)};
    }
};

function update_after_select() {
    update_layout();
    highlight_selected();
    show_form(null);

    if (data.spike_detector.meta.neurons.length > 0) {
        update_selected_node("g.smoothed_histogram", "path");
        update_correlation("#correlation_plot");
    }
    if (data.voltmeter.meta.neurons.length > 0) { update_selected_node("g.voltmeter", "path"); }
};

function node_interaction() {
    var id = $(this).attr('id').substring(5);

    selected_node = nodes.filter(function(n) {
        return (n.id == id);
    })[0];
    selected_link = null;
    update_after_select();
};

function node_connection_interaction() {
    var id = $(this).parent().attr('id').substring(7);

    selected_node = nodes.filter(function(n) {
        return (n.id == id);
    })[0];
    update_after_select();
};

function link_interaction_click() {
    var source_id = $(this).parent().attr('id').substring(7);
    var target_id = $(this).attr('class').substring(7,9);

    selected_link = links.filter(function(l) { return (l.source.id == source_id && l.target.id == target_id); })[0];

    selected_node = null;
    update_after_select();
};

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
};

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
};
