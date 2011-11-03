$.fn.reset = function () {
    $(this).each (function() { this.reset(); });
    return this
};

$.fn.loadTheme = function (options) {
        $( this ).addClass( "ui-widget ui-helper-clearfix" )
            .find( ".portlet-header" )
                    .addClass( "ui-widget-header ui-corner-top tipTip-top" )
                    .end()
            .find( ".portlet-toggle" )
                    .prepend( "<span class='ui-icon toggle ui-icon-minusthick'></span>")
                    .end()
            .find( ".portlet-content" )
                    .addClass( "ui-widget-content ui-shadow" );
                    
                    
        $( this ).find( ".portlet-header .toggle" ).click(function() {
                $( this ).toggleClass( "ui-icon-minusthick" ).toggleClass( "ui-icon-plusthick" );
                $( this ).parents( ".portlet:first" ).find( "div.portlet-content" ).fadeToggle("slow");
        });
        
        $( this ).find( ".buttons")
            .find( "button" ).button().end()
            .find( ".delete" ).button({
                    icons: {
                        primary: "ui-icon-trash"
                    },})
                .end()
            .find( ".check" ).button({
                    icons: {
                        primary: "ui-icon-check"
                    },})
                .end()
            .find( ".reset" ).button({
                    icons: {
                        primary: "ui-icon-arrowreturnthick-1-w"
                    },})
                .end()
            .find( ".play" ).button({
                    icons: {
                        primary: "ui-icon-play"
                    },})
                .end()
            .find( ".zoomin" ).button({
                    icons: {
                        primary: "ui-icon-zoomin"
                    }})
                .end()
            .find( ".help" ).button({
                    icons: {
                        primary: "ui-icon-help"
                    }})
                .end()        
            .find( ".toggle" ).button({
                    icons: {
                        primary: "ui-icon-circle-arrow-s"
                    }})
                .end()
            .find( ".ui-state-highlight" ).button({
                    icons: {
                        primary: "ui-icon-circle-arrow-n"
                    }})
                .end()
            .find( ".document" ).button({
                    icons: {
                        primary: "ui-icon-document"
                    }})
                .end()
            .find( ".favorite" ).button({
                    icons: {
                        primary: "ui-icon-star"
                    }})
                .end();

        if ('tipTip' in options && options['tipTip']) {
            $( this ).find( "div.field-wrapper" ).tipTip({
                defaultPosition: 'right',
                delay: 500
            });
        }
                

};

    $(document).ready(function() {

        // CONTENT HEADER
        $( "#banner" ).css("background", "url(/media/images/special/nuspic_banner_small.png) no-repeat")
                .css('height','85px')
                .css('width', '880px');

        $( "#content-head" ).click(function(){
            $( "#network_header_toggle" ).slideToggle('fast', function () {
            });
        });



        // DEVICE TABLE
        $( "table#device-table tr" ).each(function(){
                $( this ).addClass("tipTip-right");
        });
        $( "table th" ).each(function(){
                $( this ).addClass("ui-state-default");
        });
        $( "table td" ).each(function(){
                $( this ).addClass("ui-widget-content");
        });
        $( "table tr.enabled" ).hover(
                function(){
                    $( this ).children("td").addClass("ui-state-hover");
                },function(){
                    $( this ).children("td").removeClass("ui-state-hover");
        });
        $( "table tr.enabled" ).click(function(){
                $( this ).children( "td" ).toggleClass("ui-state-highlight");
        });


        // SELECT DEVICE TO CHANGE PARAMETERS
        $( "tr.enabled" ).find( "td.selectable" ).click(function(e) {
                e.preventDefault();
                $( "ul.errorlist" ).remove();
                $( "option:first" ).attr('selected', 'selected');
                selected_device_id = $(this).parent( ".enabled" ).attr('id')
                var device = device_list[selected_device_id-1];
                var form = $( "#"+device[0].label );

                if ($( form ).is(":visible")) {
                    $( "#device_id" ).html("");
                    $( form ).toggle();
                    $( "#device-form" ).hide();
                } else {
                    $( "#device_id" ).html(selected_device_id)
                    $( "tr.enabled" ).each(function() {
                            if ($(this).attr('id') != selected_device_id && $(this).children("td").hasClass("ui-state-highlight")) {
                                $(this).children("td").toggleClass("ui-state-highlight");
                            }
                    });
                    $( ".device-form:visible" ).toggle();
                    $( form ).reset();
                    var form_content = $( form ).children();
                    $(form_content)
                        .find( "#id_model" ).val(device[0]['label']);
                    for (var key in device[1]) {
                        $(form_content).find( "#id_"+ key ).val(device[1][key]).removeClass('ui-state-hover');
                    };
                    for (var key in device[2]) {
                        $(form_content).find( "#id_"+ key ).val(device[2][key]).removeClass('ui-state-hover');
                    };
                    $( form ).toggle();
                    $( "#device-form" )
                          .find( "#selected_device_id" ).html(selected_device_id).end()
                          .find( "#selected_device_label" ).html(device[0]['label'].replace(/_/g, ' ')).end()
                          .show();
                }
        });


        // DELETE DEVICE
        $( "button#delete-devices" ).click(function(e) {
                e.preventDefault();
                $( this ).toggleClass( "ui-state-highlight" )
                    if ($( "table#device-table .delete" ).is(":visible") && $( "table#device-table .delete" ).find( "input" ).is(":checked")) {
                    $(".devices-form").submit();
                } else {
                    $( "table#device-table .delete" ).toggle();
                };
        });


        // GET HELP
        $( "button#help-network" ).click(function(e) {
            e.preventDefault()
            $( "#network_header_toggle" ).slideToggle('fast');
            $( "#youtube" ).html('<object style="height: 210px; width: 320px; margin:auto"><param name="movie" value="http://www.youtube.com/v/LE-JN7_rxtE?version=3&feature=player_detailpage"><param name="allowFullScreen" value="true"><param name="allowScriptAccess" value="always"><embed src="http://www.youtube.com/v/LE-JN7_rxtE?version=3&feature=player_detailpage" type="application/x-shockwave-flash" allowfullscreen="true" allowScriptAccess="always" width="320" height="180"></object>');
        });

        
        // SELECT A DEVICE TO ADD
        $( "select#id_label" ).change(function(e) {
                e.preventDefault()
                $( ".device-form:visible" ).hide();
                $( "#device-form" ).hide();
                $( "ul.errorlist" ).remove();
                selected_device_id = last_device_id+1
                $( "span#device_id" ).html(selected_device_id);
                $( "tr.enabled" ).each(function() {
                            if ($(this).attr('id') != selected_device_id && $(this).children("td").hasClass("ui-state-highlight")) {
                                $(this).children("td").toggleClass("ui-state-highlight");
                            }
                    });

                var form = $( "#"+ $(this).val() );
                if ($(this).val() != "") {
                    $( form ).reset().find( "#selected_device_id" ).html(selected_device_id).end()
                        .find( "#id_model" ).attr('value', $(this).val()).end()
                        .show();

                    $( "#device-form" )
                        .find( "#selected_device_id" ).html(selected_device_id).end()
                        .find( "#selected_device_label" ).html($(this).val().toString().replace(/_/g, ' ')).end()
                        .show();
                }
        });

        
        // DEVICE FORMS
        $( ".required input" ).each(function() {
            if ($(this).val() == '') {$(this).addClass('ui-state-hover')};
            });

        $( ".required input" ).keyup(function() {
            if (this.value == '') {
                $(this).addClass('ui-state-hover');
            } else {
                $(this).removeClass('ui-state-hover');
            }
        });


        // NETWORK LAYOUT
        $( "button#layout-legend" ).click(function() {
            $(this).toggleClass("ui-state-highlight");
            $( "div#layout-legend-content" ).slideToggle();
        });


        // HISTORY LIST
        $( "#history_"+ version_id).addClass( "ui-state-highlight" );

        $( "ul#history-list li" ).each(function(){
            $( this ).addClass("ui-widget-content");
        });

        $( "#history-list li" ).hover(
            function(){
                $( this ).addClass("ui-state-hover");
            },function(){
                $( this ).removeClass("ui-state-hover");
        });

        $( "ul#history-list div.version-link" ).click(function (e) {
                $(".ui-dialog-content" ).html($( this ).attr('title'));
                $( "#dialog-loading" ).dialog({
                        title: 'Loading... please wait.',
                        resizable: false,
                        modal: true,
                });
                window.location.href = $( this ).find( "a" ).attr('href')
        });

        $( "button#go-versions" ).click(function(e) {
                e.preventDefault();
                if ($( "ul#history-list input" ).is(":checked")) {
                    $( ".versions-form" ).submit();
                };
        });

        // tipTip
        $( ".tipTip-top" ).tipTip({
                delay: 1000,
                defaultPosition: 'top',
        });

        $( ".tipTip-right" ).tipTip({
                defaultPosition: 'right',
        });

        $( ".tipTip-left" ).tipTip({
                defaultPosition: 'left',
        });

    })