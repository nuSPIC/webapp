$.fn.reset = function () {
    $(this).each (function() { this.reset(); });
    return this
};

$.fn.loadTheme = function (options) {
        $( this ).addClass( "ui-widget ui-helper-clearfix" )
            .find( ".portlet-header" )
                    .addClass( "ui-widget-header ui-corner-tl tipTip-top" )
                    .prepend( "<span class='ui-icon toggle ui-icon-minusthick'></span>")
//                  .prepend( "<span class='ui-icon dialog ui-icon-newwin'></span>")
                    .end()
            .find( ".portlet-content" )
                    .addClass( "ui-widget-content ui-shadow" );
                    
                    
        $( this ).find( ".portlet-header .toggle" ).click(function() {
                $( this ).toggleClass( "ui-icon-minusthick" ).toggleClass( "ui-icon-plusthick" );
                $( this ).parents( ".portlet:first" ).find( "div.portlet-content" ).slideToggle();
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
                
        $( this ).find( "div.field-wrapper" ).tipTip({
                defaultPosition: 'right',
                delay: 500,
        });
};