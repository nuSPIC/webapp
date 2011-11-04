
Raphael.fn.connection = function (obj1, obj2, line, bg, syn) {
    if (obj1.line && obj1.from && obj1.to) {
        line = obj1;
        obj1 = line.from;
        obj2 = line.to;
    }
    var bb1 = obj1.getBBox(),
        bb2 = obj2.getBBox(),
        p = [
//         box1
        {x: bb1.x + bb1.width / 2, y: bb1.y - 1}, // top
        {x: bb1.x + bb1.width / 2, y: bb1.y + bb1.height + 1}, // bottom
        {x: bb1.x - 1, y: bb1.y + bb1.height / 2}, // left
        {x: bb1.x + bb1.width + 1, y: bb1.y + bb1.height / 2}, // right
        
//         box2
        {x: bb2.x + bb2.width / 2, y: bb2.y - 11},
        {x: bb2.x + bb2.width / 2, y: bb2.y + bb2.height + 11},
        {x: bb2.x - 11, y: bb2.y + bb2.height / 2},
        {x: bb2.x + bb2.width + 11, y: bb2.y + bb2.height / 2}],
        d = {}, dis = [];
        
        
    for (var i = 0; i < 4; i++) {
        for (var j = 4; j < 8; j++) {
            var dx = Math.abs(p[i].x - p[j].x),
                dy = Math.abs(p[i].y - p[j].y);
            if ((i == j - 4) || (
                    ((i != 3 && j != 6) || p[i].x < p[j].x) &&
                    ((i != 2 && j != 7) || p[i].x > p[j].x) &&
                    ((i != 0 && j != 5) || p[i].y > p[j].y) &&
                    ((i != 1 && j != 4) || p[i].y < p[j].y))
                ) {
                dis.push(dx + dy);
                d[dis[dis.length - 1]] = [i, j];
            }
        }
    }
    if (dis.length == 0) {
        var res = [0, 4];
    } else {
        res = d[Math.min.apply(Math, dis)];
    }
    
    // Fix position
    var x1 = p[res[0]].x,
        y1 = p[res[0]].y,
        x4 = p[res[1]].x,
        y4 = p[res[1]].y;
    
    // Bend connections 
    dx = Math.max(Math.abs(x1 - x4) / 2, 10);
    dy = Math.max(Math.abs(y1 - y4) / 2, 10);
    var x2 = [x1, x1, x1 - dx, x1 + dx][res[0]].toFixed(3),
        y2 = [y1 - dy, y1 + dy, y1, y1][res[0]].toFixed(3),
        x3 = [0, 0, 0, 0, x4, x4, x4 - dx, x4 + dx][res[1]].toFixed(3),
        y3 = [0, 0, 0, 0, y1 + dy, y1 - dy, y4, y4][res[1]].toFixed(3);


    // Make Synaptics
    var cos = 0.866;
    var sin = 0.500;
    var dx = (x4 - x3);
    var dy = (y4 - y3);

    // Normailze to Synaptics.
    var length = Math.sqrt(dx * dx + dy * dy);
    dx = 10 * (dx / length) ;
    dy = 10 * (dy / length) ;

    var pX1 = x4 + (dx * cos + dy * -sin);
    var pY1 = y4 + (dx * sin + dy * cos);

    var pX2 = x4 + (dx * cos + dy * sin);
    var pY2 = y4 + (dx * -sin + dy * cos);
    
    var path = [
        "M", x1.toFixed(3), y1.toFixed(3),
        "C",  x2, y2, x3, y3, x4.toFixed(3), y4.toFixed(3),
        ].join(",");

    var syn_path = ["M", x4.toFixed(3), y4.toFixed(3), "L", x4, y4, pX1, pY1, pX2, pY2 ,x4, y4, ].join(",")
        
    if (line && line.line) {
            line.bg && line.bg.attr({path: path});
            line.line.attr({path: path});
            line.syn.attr({path: syn_path});

        } else {
            var color = typeof line == "string" ? line : "#000";
            return {
                bg: bg && bg.split && this.path(path).attr({
                                                           opacity: 0.7,
                                                           fill: "none",
                                                           stroke: bg.split("|")[0],
                                                           "stroke-width": bg.split("|")[1] || 3}).toBack(),
                line: this.path(path).attr({opacity:1, fill: "none", stroke: color}).toBack(),
                syn: syn && syn.split && this.path(syn_path).attr({        
                                                                  fill: syn.split("|")[0],
                                                                  "fill-opacity": 0.7,
                                                                  stroke: syn.split("|")[0],
                                                                  "stroke-opacity": 0.5,
                                                                  "stroke-width": syn.split("|")[1] || 3, 
                                                                  "stroke-linejoin": "round",}).toBack(),
                from: obj1,
                to: obj2
            };
    }

};

Array.prototype.inArray = function (value,caseSensitive)
// Returns true if the passed value is found in the
// array. Returns false if it is not.
{
   for (var i = 0; i < this.length; i++)
   {
        // use === to check for Matches. ie., identical (===),
        if (caseSensitive)
        {
           // performs match even the string is case sensitive
           if (this[i].toLowerCase() == value.toLowerCase())
           {
               return true;
           }
        } else {
           if (this[i] == value)
           {
               return true;
           }
        }
   }

   return false;
};


$.fn.loadLayout = function (device_list) {
  
    var start = function () {
        this.ox = this.attr("cx");
        this.oy = this.attr("cy");
        this.neuron_id = this.data("id");
        this.neuron_label = this.data("label");
        
        this.draggableset = draggablesets[this.neuron_id];
        this.draggableset.oBB = this.draggableset.getBBox();
        this.bb = this.draggableset.getBBox();

//         inputs[this.neuron_id-1].animate({"fill-opacity": 0}, 500);
//         outputs[this.neuron_id-1].animate({"fill-opacity": 0}, 500);
//         this.trial = this.glow();

//         $('#position').fadeIn().html([this.ox, this.oy].toString());
        },
        
    move = function (dx, dy) {
        this.bb = this.draggableset.getBBox();
        this.cx = parseInt(this.bb.x)+17;
        this.cy = parseInt(this.bb.y)+12;        
        this.draggableset.translate(this.draggableset.oBB.x - this.bb.x + dx, this.draggableset.oBB.y - this.bb.y + dy);
        
//        this.attr({cx: this.ox + dx, cy: this.oy + dy});
//         labels[this.neuron_id-1].attr({x: this.cx, y: this.cy});
//         inputs[this.neuron_id-1].attr({cx: this.cx - 10, cy: this.cy});
//         outputs[this.neuron_id-1].attr({cx: this.cx + 10, cy: this.cy});
        
        for (var i = connections.length; i--;) {
            paper.connection(connections[i]);
            }
        paper.safari();
        
        $('#position').fadeIn().html([this.cx, this.cy].toString());
        },
    
    up = function () {
//         this.trial.animate({"opacity": 0}, 1000);
//         inputs[this.neuron_id-1].animate({"fill-opacity": 1}, 500);
//         outputs[this.neuron_id-1].animate({"fill-opacity": 1}, 500);

        device_list[this.neuron_label-1][0]["position"] = [this.bb.x > 0 ? this.cx : 18, this.bb.y > 0 ? this.cy : 13];
        $('#position').fadeOut();
        };

    var x, y, id, edge, wcolors, 
    paper = Raphael("holder", layoutSize["x"]+30, layoutSize["y"]+30),
    shapes = [], connections = [];
    
    paper.clear();
    id = 0;
    for (var ii = 0; ii < device_list.length; ii++) {
        device = device_list[ii];
        if ("position" in device[0]) {
            x = device[0]["position"][0];
            y = device[0]["position"][1];
            label = device[0]["id"];

            shapes.push(
                paper.ellipse(x, y, 17, 12)
                     .data("id", id++)
                     .data("label", label)
                     .data("input", connect_to_input.inArray(label))
                     .data("output", connect_to_output.inArray(label))
                     .data("targets", device[2]["targets"])
                     .attr({cursor: "move",
                           fill: "#fff",
                           "fill-opacity": 0.1,
                           stroke: $( ".ui-widget-content" ).css("color"),
                           "stroke-width": 2,
                           "stroke-opacity": .8,
                           })
                     );
              
            }
        }
        
    var draggablesets = [];
    var labels = [], inputs = [], outputs = [];
    for (var ii = 0; ii < shapes.length; ii++) {
        draggableset = paper.set();
        
        shape = shapes[ii];
        draggableset.push(shape);
        
        x = shape.attr("cx");
        y = shape.attr("cy");
        
        draggableset.push(
            paper.text(x, y, shape.data("label").toString())
                .attr({fill: $( ".ui-widget-content" ).css("color"),
                    "font-family": "Helvetica, Arial",
                    "font-weight": "bold"}
                    )
                .toBack()
                );
                 
        if ( shape.data("input") ) {
            draggableset.push(
                paper.ellipse(x-10, y, 2, 2)
                     .attr({
                           fill: $( ".ui-widget-content" ).css("color"),
                           "fill-opacity": 1,
                           "stroke-width": 0}
                           )
                     .toBack()
                );
            }
            
        if ( shape.data("output") ) {
            draggableset.push(
                paper.ellipse(x+10, y, 2, 2)
                     .attr({
                           fill: $( ".ui-widget-content" ).css("color"),
                           "fill-opacity": 1,
                           "stroke-width": 0}
                           )
                     .toBack()
                );
            }

        draggableset.drag(move, start, up)
             .hover(
                function() {
                    this.animate({"stroke-width": 3}, 500);
                   
                    var neuron_label = this.data("label");
                    $( "table#device-table" ).find( "tr#"+ neuron_label).find( "td" ).addClass( "ui-state-highlight" );
                    $( "table#weight-table" ).find( "tr#neuron_"+ neuron_label ).find( "td.connections-table" ).addClass( "ui-state-highlight" );
                    $( "table#delay-table" ).find( "tr#neuron_"+ neuron_label ).find( "td.connections-table" ).addClass( "ui-state-highlight" );
                    
                    device = device_list[neuron_label-1];
                    if ("targets" in device[2]) {
                        var targets = device[2]["targets"].split(",");
                            for (idx in targets) {
                                var tgt = (targets[idx]);
                                $( "table#weight-table" )
                                    .find( "th#weight_" + tgt )
                                    .addClass( "ui-state-highlight" );
                                
                                $( "table#delay-table" )
                                    .find( "th#delay_" + tgt )
                                    .addClass( "ui-state-highlight" );
                            }
                        };
                    
                    },
                function () {
                    this.animate({"stroke-width": 2}, 500);
                    $( "table#device-table" ).find( "td" ).removeClass( "ui-state-highlight" );
                    $( "table#weight-table" ).find( ".connections-table" ).removeClass( "ui-state-highlight" );
                    $( "table#delay-table" ).find( ".connections-table" ).removeClass( "ui-state-highlight" );
                    });
                    
        draggablesets.push(draggableset)
    
        }

    for (var i = 0; i < edgelist.length; i++) {
        edge = edgelist[i];
        if ("weight" in edge[2]) { var weight = edge[2]["weight"] } else { var weight = 1. };
        
        wcolor =  weight < 0 ? "#B34846" : "#467AB3";
        connections.push(paper.connection(shapes[edge[0]-1], shapes[edge[1]-1], wcolor, wcolor +"|3", wcolor +"|2"));
    }
};