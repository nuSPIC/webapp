/*!
 * Form numeric validation with bootstrap v0.1
 * https://github.com/babsey/form-numeric-validation
 *
 * Copyright 2015 Sebastian Spreizer
 * Released under the BSD 2-clause "Simplified" Licence
 */

function clear_field(field) {
    field.parents('.form-group').removeClass('has-error has-success has-feedback');
    field.parent().find(".error-text").remove();
    field.parent().find("span.glyphicon").remove();
};

function clear_form(form) {
    form.find(".alert").remove();
    form.find('.form-group').removeClass('has-error has-success has-feedback');
    form.find(".error-text").remove();
    form.find("span.glyphicon").remove();
};

function isNumber(n) { return !isNaN(parseFloat(n)) && isFinite(n); };

function numeric_validation(div, val) {
    var error_msg = [];
    if ( !(isNumber(val)) ) {
        error_msg.push('Enter a valid number value.');
    }
    if ( (div.hasClass('nonzero')) && (parseFloat(val) == 0.0) ) {
        error_msg.push('Enter a valid nonzero value.');
    }
    if ( (div.hasClass('positive')) && (parseFloat(val) < 0.0) ) {
        error_msg.push('Enter a valid positive value.');
    }
    if ( (div.hasClass('negative')) && (parseFloat(val) > 0.0) ) {
        error_msg.push('Enter a valid negative value.');
    }
    if (  div.hasClass('min') || div.hasClass('max') ) {
        var classes = div.attr("class").split(' ');
        if (classes.indexOf('max')) {
            var val_max = parseFloat(classes[classes.indexOf('max')+1]);
            if (parseFloat(val) > val_max) {
                error_msg.push('Enter a valid value that is smaller than ' + val_max +'.');
            }
        }
        if (classes.indexOf('min')) {
            var val_min = parseFloat(classes[classes.indexOf('min')+1]);
            if (parseFloat(val) < val_min) {
                error_msg.push('Enter a valid value that is greater than ' + val_min +'.');
            }
        }
    }
    return error_msg
};

function field_validation(field) {
    field.prop('disabled', true);
    clear_field(field);

    var val = field.val();
    var div = field.parents('.form-group');
    var error_msg = [];

    if ( val == '' && field.hasClass('required') ) {
        error_msg.push('This field is required.');
    } else if (val != '') {
        if (field.hasClass('number')) {
            if (field.hasClass('list')) {
                val_list = val.split(',');
                for (var i=0; i<val_list.length; i++) {
                    if (val_list[i] != '') {
                        error_msg = error_msg.length == 0 ? numeric_validation(field,val_list[i]) : error_msg;
                    }
                }
            } else {
                error_msg = numeric_validation(field, val);
            }
        }
    }
    if (error_msg.length == 0) {
        if (val || field.hasClass('required')) {
            div.addClass('has-success');
            $('<span aria-hidden="true" class="glyphicon glyphicon-ok form-control-feedback"></span>').insertAfter(field);
        }
    } else {
        div.addClass('has-error');
        $('<span class="glyphicon glyphicon-remove form-control-feedback" aria-hidden="true"></span>').insertAfter(field);
        for (var i=0; i<error_msg.length;i++) {
            $('<span class="error-text help-block"><strong>'+error_msg[i]+'</strong></span>').insertAfter(field);
        }
    }

    div.addClass('has-feedback');
    field.prop('disabled', false);
    return (error_msg.length == 0)
};

// Experiment
function form_validation(form, clean_form_action, clean_field_action) {
    form.find('input').prop('disabled', true);
    clear_form(form);

    var error_fields = [];
    form.find('input:visible:not(.checkboxinput):not(.btn)').each(function () {
        if ($(this).val() || $(this).hasClass('required')) {
            if (field_validation($(this))) {
                clean_field_action
            } else {
                error_fields.push($(this));
            }
        }
    })

    if (error_fields.length == 0) { clean_form_action }
    else { form.prepend('<h4 class="alert alert-danger">Oh snap! You got an error!</h4>') }

    form.find('input').prop('disabled', false);
    return error_fields
};

// Experiment
function clean_node_form_action() {
    if (selected_model == 'spike_generator') {
        selected_node.status = {'spike_times': status.spike_times, 'model': status.model};
    } else {
        selected_node.status = status;
    }
    selected_node.label = node_form.find("#id_model :selected").text()
    selected_node.disabled = 0;
    if (status.model.indexOf("meter") != -1 || status.model.indexOf('detector') != -1) {
        selected_node.type = 'output'
        if ('synapse' in selected_node) {delete selected_node["synapse"];}
    } else if (status.model.indexOf("generator") != -1) {
        selected_node.type = 'input'
        if ('synapse' in selected_node) {delete selected_node["synapse"];}
    } else {
        selected_node.type = 'neuron';
        selected_node.synapse = node_form.find("#id_synapse :selected").text();
    }
    link_validation();
    update_after_change();
};

function node_form_validation(e) {
    e.preventDefault();
    var form = $(this);
    form.find('input').prop('disabled', true);
    clear_form(form);

    var status = {'model': form.find("#id_model :selected").val()};
    var error_fields = [];
    form.find('input:visible').each(function () {
        if ($(this).val()) {
            var clean_field = field_validation($(this));

            if (clean_field) {
                status[$(this).attr('id').substr(3)] = $(this).hasClass('list') ? $(this).val() : parseFloat($(this).val());
            } else {
                error_fields.push($(this));
            }
        }
    })

    if (error_fields.length == 0) {
        if (selected_model == 'spike_generator') {
            selected_node.status = {'spike_times': status.spike_times, 'model': status.model}
        } else {
            selected_node.status = status;
        }
        selected_node.label = form.find("#id_model :selected").text()
        selected_node.disabled = 0;
        if (status.model.indexOf("meter") != -1 || status.model.indexOf('detector') != -1) {
            selected_node.type = 'output'
            if ('synapse' in selected_node) {delete selected_node["synapse"];}
        } else if (status.model.indexOf("generator") != -1) {
            selected_node.type = 'input'
            if ('synapse' in selected_node) {delete selected_node["synapse"];}
        } else {
            selected_node.type = 'neuron';
            selected_node.synapse = form.find("#id_synapse :selected").text();
        }

        link_validation();
        update_after_change();
    } else {
        form.prepend('<h4 class="alert alert-danger">Oh snap! You got an error!</h4>');
        error_fields[0].focus();
    }
    form.find('input').prop('disabled', false);
};

function link_form_validation(e) {
    e.preventDefault();
    var form = $(this);
    form.find('input').prop('disabled', true);
    clear_form(form);

    var synapse = selected_link.source.synapse;

    var weight_val = form.find('input#id_weight').val();
    var weight_error_msg = null;
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
    if (weight_error_msg == null) {
        form.find('#div_id_weight').addClass('has-success');
    } else {
        form.find('#div_id_weight').find("p.help-block").prepend('<span class="help-block"><strong>'+weight_error_msg+'</strong></span>');
        form.find('#div_id_weight').addClass('has-error');
    }

    var delay_val = form.find('input#id_delay').val();
    var delay_error_msg = null;
    if ( delay_val == '' ) {
        delay_val = 1.0;
    } else if ( !(isNumber( delay_val )) ) {
        delay_error_msg = 'Enter a valid positive value.';
    } else if (parseFloat(delay_val) < 0.0) {
        delay_error_msg ='Delay value cannot be negative.<br> Enter a positive value.';
    } else if (parseFloat(delay_val) > 10.0) {
        delay_error_msg = 'Delay value is too large.\n Enter a value that is smaller than 10 ms.';
    }
    if (delay_error_msg == null) {
        form.find('#div_id_delay').addClass('has-success');
    } else {
        form.find('#div_id_delay').find("p.help-block").prepend('<span class="help-block"><strong>'+delay_error_msg+'</strong></span>');
        form.find('#div_id_delay').addClass('has-error');
    }

    if (weight_error_msg == null && delay_error_msg == null) {
        selected_link.weight = parseFloat(weight_val);
        selected_link.delay = parseFloat(delay_val);
        update_after_change();
    } else {
        form.prepend('<h4 class="alert alert-danger">Oh snap! You got an error!</h4>')
    }
    form.find('input').prop('disabled', false);
};

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
};

function network_form_validation(e) {
    e.preventDefault();

    var error_fields = form_validation($(this));
    if (error_fields.length != 0) {
        error_fields[0].focus();
        return
    };

    clear_form($(this));
    if (links.filter(connect_to_output).length <1) {
        show_msg('<i class="fa fa-exclamation-triangle"></i> Warning', 'No <b>recording device</b> connected. <p>Check your output connections.</p>', 'warning');
    } else if (links.filter(connect_to_input).length <1) {
        show_msg('<i class="fa fa-exclamation-triangle"></i> Warning', 'No <b>input device</b> connected. Network may be silent. <p>Do you want to continue?</p>', 'simulation-confirm');
    } else if ($( "#id_duration" ).val() > 5000.0) {
        show_msg('<i class="fa fa-exclamation-triangle"></i> Warning', 'The simulation lasts more than 5 seconds and it could have a speed effect on page loading time. <p>Are you sure?</p>', 'simulation-confirm');
    } else {
        simulate();
    }
};
