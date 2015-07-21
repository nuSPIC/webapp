// Set the font size
$(".font-size").on('click', function(e) {
    $( "#network-content" ).css("font-size", $(this).css("font-size"));
});

// Toggle options content
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

// Toggle nodes display on layout
$( "button.nodes-display" ).on('click', function() {
    options.layout.nodes.display[$(this).val()] = !(options.layout.nodes.display[$(this).val()])
    update_after_change();
});

// Toggle links display on layout
$( "button.links-display" ).on('click', function() {
    options.layout.links.display[$(this).val()] = !(options.layout.links.display[$(this).val()])
    update_after_select();
});

// Toggle the link weight display on layout
$( "button.links-weight-display" ).on('click', function() {
    options.layout.links.display.weight = ($(this).val() == 'true' ? true : false)
    update_after_select();
});

// Change the mode of the curve
$( "button.links-curve" ).on('click', function() {
    options.layout.links.curve = $(this).val();
    update_after_select();
});

// Redisplay the form content for selected model
node_form.find('#id_model').on('change', function() {
    show_form($(this).val());
});

// Generate spike times for spike generator
node_form.find("#id_step" ).on('keyup', function() {
    var step = parseFloat(this.value);
    var spike_times = [];
    if (step > 0) {
        var start = node_form.find( "#id_start" ).val();
        var stop = node_form.find( "#id_stop" ).val();
        if (start == '') {
            start = step;
        }
        if ((stop == 'inf') || (stop == '')) {
            stop = simulation_stop;
        }
        var spike_times = [];
        for (var tt = parseFloat(start); tt <= parseFloat(stop); tt += step) {
            spike_times.push(tt);
        };
    };
    node_form.find( "#id_spike_times" ).val(spike_times.toString());
});

// Live validation check
node_form.find('.form-control').on('change', function() {
    field_validation($(this));
});

link_form.find('.form-control').on('change', function() {
    field_validation($(this));
});

network_form.find('.form-control').on('change', function() {
    field_validation($(this));
});

// Validation check on submit
node_form.on('submit', node_form_validation );
link_form.on('submit', link_form_validation );
network_form.on('submit', network_form_validation );

// Reset the form field
node_form.find('button-id-reset').on('click', function(e) {
    e.preventDefault(); // stops the form from resetting after this function
    node_form.get(0).reset();  // resets the form before continuing the function
    node_form.find("#id_model #" + selected_model).prop('selected', true);
});

// Toggle comment form content
$( '#network-comment' ).on('click', function (e) {
    e.preventDefault();
    $("#network-comment-form").toggleClass("hide").toggleClass("fade");

});

// Save comment via ajax
$( "#id-comment-form" ).on('submit',  function(e) {
        e.preventDefault();
        $.post('/network/ajax/'+ network_id +'/comment/',
            $( this ).serialize(), function(data){
                $('#network_label').html(data.label);
                $('#network_comment').html(data.comment);
                if (data.comment[0].length > 0) {
                    $("#network_description").addClass("hide fade");
                } else {
                    $("#network_description").removeClass("hide fade");
                }
                $('#history_'+local_id).attr("data-content", data.comment).attr("data-original-title", data.label).popover('destroy').popover({trigger:'hover', html:true})
        }, 'json');
});

// Check favorite
$( '#network-like' ).on('click', function (e) {
    e.preventDefault();
    $.post('/network/ajax/'+ network_id +'/like/',
        {csrfmiddlewaretoken: csrf_token },
        function(){
            $( "#network-like" ).addClass('hide fade');
            $( "#network-dislike" ).removeClass('hide fade');
            $( "#history_"+ local_id ).find( ".favorite" ).addClass('fa-thumbs-o-up');
    });
});

// Uncheck favorite
$( '#network-dislike' ).on('click', function (e) {
    e.preventDefault();
    $.post('/network/ajax/'+ network_id +'/dislike/',
        {csrfmiddlewaretoken: csrf_token },
        function(){
            $( "#network-like" ).removeClass('hide fade');
            $( "#network-dislike" ).addClass('hide fade');
            $( "#history_"+ local_id ).find( ".favorite" ).removeClass('fa-thumbs-o-up');
    });
});

// Display instruction
$( '#tour' ).on('click', function() {
    // Instance the tour
    var tour = new Tour({
        debug: true,
        storage: false,
        steps: tour_steps,
    })

    // Initialize the tour
    tour.init();

    // Start the tour
    tour.start();
});
