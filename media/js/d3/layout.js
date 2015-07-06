var layout_force, drag_line;
var svg = {};

// mouse event vars
var selected_node = null,
    selected_node2 = null,
    selected_link = null;

var last_selected_node = null;

var mousedown_link = null,
    mousedown_node = null,
    mouseup_node = null;

var focused_node = null,
    focused_link = null;

// only respond once per keydown
var lastKeyDown = -1;

function resetMouseVars() {
    mousedown_node = null;
    mouseup_node = null;
    mousedown_link = null;
}

function log10(val) {
  return Math.log(val) / Math.LN10;
}

// update force layout (called automatically each iteration)
function tick() {

    // draw curved edges with proper padding from node centers
    svg.links.attr('d', function(d) {
        var deltaX = d.target.x - d.source.x,
            deltaY = d.target.y - d.source.y,
            dist = Math.sqrt(deltaX * deltaX + deltaY * deltaY),
            normX = deltaX / dist,
            normY = deltaY / dist,
            sourceX = d.source.x + (15 * normX),
            sourceY = d.source.y + (15 * normY),
            targetX = d.target.x - (19 * normX),
            targetY = d.target.y - (19 * normY);

        return 'M' + sourceX + ',' + sourceY + "A" + dist + "," + dist + " 0 0," + (options.layout.links.curve == 'left' ? "1 " : "0 ") + targetX + ',' + targetY;
    });

    svg.internodes.attr('transform', function(d) {
            var deltaX = d.target.x - d.source.x,
                deltaY = d.target.y - d.source.y,
                medianX = (d.target.x + d.source.x) / 2,
                medianY = (d.target.y + d.source.y) / 2;

            var x = (options.layout.links.curve == 'left') ? medianX+(deltaY/10) :medianX-(deltaY/10),
                y = (options.layout.links.curve == 'left') ? medianY-(deltaX/10) : medianY+(deltaX/10);

            return 'translate(' + x + ',' + y + ')';
         });

    svg.weights.attr('transform', function(d) {
            var deltaX = d.target.x - d.source.x,
                deltaY = d.target.y - d.source.y,
                medianX = (d.target.x + d.source.x) / 2,
                medianY = (d.target.y + d.source.y) / 2;

            var x = (options.layout.links.curve == 'left') ? medianX+(deltaY/10) :medianX-(deltaY/10),
                y = (options.layout.links.curve == 'left') ? medianY-(deltaX/10) : medianY+(deltaX/10);

            return 'translate(' + x + ',' + y + ')';
         });

    svg.nodes.attr('transform', function(d) {
        return 'translate(' + d.x + ',' + d.y + ')';
    });
}

function active_link(d) {

    return selected_node || selected_link ? 
                selected_node ? (options.layout.links.display.pre ? d.target === selected_node : false) || (options.layout.links.display.post ? d.source === selected_node : false) 
                : (options.layout.links.display.pre ? d.target === selected_link.source : false) || (options.layout.links.display.post ? d.source === selected_link.target : false) || (d === selected_link)
              : (d.source.type == 'neuron') && (d.target.type == 'neuron');

}

function active_weight(d) {
    return options.layout.links.display.weight ? 
       (selected_node || selected_link ? 
            selected_node ? (options.layout.links.display.pre ? d.target === selected_node : false) || (options.layout.links.display.post ? d.source === selected_node : false) 
                : (options.layout.links.display.pre ? d.target === selected_link.source : false) || (options.layout.links.display.post ? d.source === selected_link.target : false) || (d === selected_link)
            : (d.source.type == 'neuron') && (d.target.type == 'neuron'))
         : false

}

// update graph (called when needed)
function update_layout() {

    // path (link) group
    svg.links = svg.links.data(links);

    // update existing links
    svg.links.classed('selected', function(d) { return d === selected_link; })
        .classed('active', active_link)
        .classed('hidden', function(d) { return !(options.layout.nodes.display[d.source.type]) || !(options.layout.nodes.display[d.target.type])})
        .classed('excitatory', function(d) { return d.weight > 0})
        .classed('inhibitory', function(d) { return d.weight < 0})
        .classed('pre', function(d) { return selected_node ? d.target === selected_node : false })
        .classed('post', function(d) { return selected_node ? d.source === selected_node : false })
        .style('marker-end', function(d) { return d.weight > 0 ? 'url(#arrow-marker)' : 'url(#circle-marker)'; });

    // add new links
    svg.links.enter().append('svg:path')
        .attr('class', 'link')
        .classed('selected', function(d) { return d === selected_link; })
        .classed('active', active_link)
        .classed('hidden', function(d) { return !(options.layout.nodes.display[d.source.type]) || !(options.layout.nodes.display[d.target.type])})
        .classed('excitatory', function(d) { return d.weight > 0})
        .classed('inhibitory', function(d) { return d.weight < 0})
        .classed('neuron', function(d) { return (d.source.type == 'neuron') && (d.target.type == 'neuron'); })
        .classed('input', function(d) { return d.source.type == 'input'})
        .classed('output', function(d) { return (d.source.type == 'output') || (d.target.type == 'output'); })
        .style('marker-end', function(d) { return d.weight > 0 ? 'url(#arrow-marker)' : 'url(#circle-marker)'; })
        .on('mouseover', function(d) { focused_link = d; })
        .on('mouseout', function(d) { focused_link = null; })
        .on('mousedown', function(d) {
            if(d3.event.ctrlKey) return;

            // select link
            mousedown_link = d;
            selected_link = d;
            focused_link = d;

            selected_node = null;
            selected_node2 = null;
            update_after_select();
        });

    // remove old links
    svg.links.exit().remove();



    // circle (internode) group
    svg.internodes = svg.internodes.data(links);

    // update existing internodes (selected visual states)
    svg.internodes
        .classed('active', active_weight)
        .classed('hidden', function(d) { return !(options.layout.nodes.display[d.source.type]) || !(options.layout.nodes.display[d.target.type])});

    // add new internodes
    svg.internodes.enter().append('svg:ellipse')
        .attr('class', 'internode')
        .classed('active', active_weight)
        .classed('hidden', function(d) { return !(options.layout.nodes.display[d.source.type]) || !(options.layout.nodes.display[d.target.type])})
        .classed('neuron', function(d) { return (d.source.type == 'neuron') && (d.target.type == 'neuron'); })
        .classed('input', function(d) { return d.source.type == 'input'})
        .classed('output', function(d) { return (d.source.type == 'output') || (d.target.type == 'output'); })
        .attr('rx', function(d) {return (Math.abs(log10(Math.abs(d.weight)))*4+7)})
        .attr('ry', 8)
        .on('mouseover', function(d) { focused_link = d; })
        .on('mouseout', function(d) { focused_link = null; })
        .on('mousedown', function(d) {
            if(d3.event.ctrlKey) return;

            // select link
            mousedown_link = d;
            if(mousedown_link === selected_link) selected_link = null;
            else selected_link = mousedown_link;
            selected_node = null;
            selected_node2 = null;
            last_selected_node = 'A';
            update_after_select();
        });

    // remove old internodes
    svg.internodes.exit().remove();



    // text (weight) group
    svg.weights = svg.weights.data(links);

    // update existing internodes (selected visual states)
    svg.weights
        .classed('active', active_weight)
        .classed('hidden', function(d) { return !(options.layout.nodes.display[d.source.type]) || !(options.layout.nodes.display[d.target.type])})
        .text(function(d) { return d.weight; });

    // add new internodes
    svg.weights.enter().append('svg:text')
        .attr('class', 'weight')
        .classed('active', active_weight)
        .classed('hidden', function(d) { return !(options.layout.nodes.display[d.source.type]) || !(options.layout.nodes.display[d.target.type])})
        .classed('neuron', function(d) { return (d.source.type == 'neuron') && (d.target.type == 'neuron'); })
        .classed('input', function(d) { return d.source.type == 'input'})
        .classed('output', function(d) { return (d.source.type == 'output') || (d.target.type == 'output'); })
        .classed('active', active_weight)
        .attr('x', 0)
        .attr('y', 4)
        .text(function(d) { return d.weight; });

    // remove old internodes
    svg.weights.exit().remove();



    // circle (node) group
    // NB: the function arg is crucial here! nodes are known by id, not by index!
    svg.nodes = svg.nodes.data(nodes, function(d) { return d.id; });

    svg.nodes.classed('hidden', function(d) { return !(options.layout.nodes.display[d.type])});

    // update existing nodes (selected visual states)
    svg.nodes.selectAll('circle')
        .classed('selected', function(d) { return (d === selected_node); })
        .classed('selected2', function(d) { return (d === selected_node2); })
        .classed('active', function(d) { return selected_link ? ((d === selected_link.source) || (d === selected_link.target)) : (d === selected_node || d === selected_node2) ;});

    // add new nodes
    var g = svg.nodes.enter().append('svg:g');

    g.classed('neuron', function(d) { return d.type == 'neuron'})
        .classed('input', function(d) { return d.type == 'input'})
        .classed('output', function(d) { return d.type == 'output'})
        .classed('hidden', function(d) { return !(options.layout.nodes.display[d.type])});

    g.append('svg:circle')
        .attr('class', 'node')
        .classed('selected', function(d) { return (d === selected_node); })
        .attr('r', 12)

        .on('mouseover', function(d) {

            focused_node = d;
//            if(!mousedown_node || d === mousedown_node) return;

            // enlarge target node
            d3.select(this).attr('transform', 'scale(1.1)');

            if (mousedown_node) {
                if (mousedown_node.type == 'neuron') {
                    d3.select(this).classed('conflict', (d.type == 'neuron' && SPIC_group == 1) || d.type == 'input' || d.status.model == 'voltmeter')
                }
                else {
                    if (d.type != 'neuron') {
                        d3.select(this).classed('conflict', true)
                    }
                }
            } else if (d.status.model == 'spike_detector') {
                d3.select(this).classed('conflict', true)
            }

        })

        .on('mouseout', function(d) {
            focused_node = null;

//            if(!mousedown_node || d === mousedown_node) return;
            // unenlarge target node
            d3.select(this).attr('transform', '')
                .classed('conflict', false);
        })

        .on('mousedown', function(d) {
//            if (d3.event.ctrlKey) return;
            mousedown_node = d;

            // select node
//            if (d3.event.shiftKey && selected_node) {
//                selected_node2 = mousedown_node;
//            } else {
//                selected_node = mousedown_node;
//                selected_node2 = null;
//            }

            if (last_selected_node == 'A') {
                selected_node2 = mousedown_node;
                last_selected_node = 'B';
            } else {
                selected_node = mousedown_node;
                last_selected_node = 'A';
            }

            selected_link = null;

            // reposition drag line
            drag_line
                .style('marker-end', mousedown_node.synapse == 'inhibitory' ? 'url(#circle-marker)' : 'url(#arrow-marker)')
                .classed('excitatory', mousedown_node.synapse == 'excitatory')
                .classed('inhibitory', mousedown_node.synapse == 'inhibitory')
                .classed('hidden', false)
                .attr('d', 'M' + mousedown_node.x + ',' + mousedown_node.y + 'L' + mousedown_node.x + ',' + mousedown_node.y);

            update_after_select();
        })

        .on('mouseup', function(d) {
            if (!mousedown_node) return;

            // needed by FF
            drag_line
                .classed('hidden', true)
                .style('marker-end', '');

            // check for drag-to-self
            mouseup_node = d;
            if (mouseup_node === mousedown_node) { resetMouseVars(); return; }

            // unenlarge target node
            d3.select(this).attr('transform', '').classed('conflict', false);

            if (mouseup_node.type == 'input' || mouseup_node.status.model == 'voltmeter' || mousedown_node.status.model == 'spike_detector') { resetMouseVars(); return; }
            if (!(mousedown_node.type == 'neuron' || mouseup_node.type == 'neuron')) { resetMouseVars(); return; }
            if (mousedown_node.disabled == 1 && mouseup_node.disabled == 1) { resetMouseVars(); return; }

            source = mousedown_node;
            target = mouseup_node;

            var link;
            link = links.filter(function(l) {
                return (l.source === source && l.target === target);
            })[0];

            if (!(link)) {
                link = {source: source, target: target};
                link = {source: mousedown_node, target: mouseup_node,
                    weight: (mousedown_node.synapse != 'inhibitory' || mouseup_node.status.model == 'spike_detector') ? 1: -1, delay:1};
                links.push(link);
            }

//          links = links.sort(function(a,b) {return a.target.id - b.target.id});;
            // select new link
            selected_link = link;
            selected_node = null;
            selected_node2 = null;
            last_selected_node = null;
            update_after_change();
        });

    // show node IDs
    g.append('svg:text')
        .attr('x', 0)
        .attr('y', 4)
        .attr('class', 'id')
        .text(function(d) { return d.type != 'output' ? d.id : (d.status.model == 'voltmeter' ? 'Vm' : 'SD'); });

    // remove old nodes
    svg.nodes.exit().remove();

    // set the graph in motion
    layout_force.start();
}

function dblclick() {
    // prevent I-bar on drag
    d3.event.preventDefault();

    // because :active only works in WebKit?
    svg.layout.classed('active', true);

    if(d3.event.ctrlKey || mousedown_node || mousedown_link) return;

    var uid = Math.random().toString(36).substring(2,7);
//     insert new node at point
    var point = d3.mouse(this);

    if (SPIC_group == 1) {
        var node = {type: 'input', label: 'AC generator', status: {model: 'ac_generator'}};
    } else {
        var node = {type: 'neuron', label: 'IAF Neuron', synapse: 'excitatory', status: {model: 'iaf_neuron'}};
    }
    node.uid = uid;
    node.id = ++lastNodeId;
    node.fixed = true;
    node.disabled = 0;
    node.x = point[0];
    node.y = point[1];
    nodes.push(node);

    selected_node = node;
    update_after_change();
}

function mousedown() {
    // prevent I-bar on drag
    d3.event.preventDefault();

    // because :active only works in WebKit?
    svg.layout.classed('active', true);

    if (d3.event.shiftKey || d3.event.ctrlKey || mousedown_node || mousedown_link) return;

    selected_node = null;
    selected_node2 = null;
    last_selected_node = null;
    selected_link = null;

    update_after_select();
}

function mousemove() {
    if (!mousedown_node) return;
    selected_node = mousedown_node;

    // update drag line
    var sourceX = mousedown_node.x,
        sourceY = mousedown_node.y,
        targetX = d3.mouse(this)[0],
        targetY = d3.mouse(this)[1],
        deltaX = targetX - sourceX,
        deltaY = targetY - sourceY,
        dist = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

    drag_line.classed('active', true)
//        .attr('d', 'M' + sourceX + ',' + sourceY + "A" + dist + "," + dist + " 0 0," + (options.layout.links.curve == 'left' ? "1 " : "0 ") + targetX + ',' + targetY);
        .attr('d', 'M' + sourceX + ',' + sourceY + "," + targetX + ',' + targetY);

    update_layout();
}

function mouseup() {
    if (mousedown_node) {
        // hide drag line
        drag_line
            .classed('hidden', true)
            .style('marker-end', '');
    }

    // because :active only works in WebKit?
    svg.layout.classed('active', false);

    // clear mouse event vars
    resetMouseVars();
}

function spliceLinksForNode(node) {
    var toSplice = links.filter(function(l) {
        return (l.source === node || l.target === node);
    });
    toSplice.map(function(l) {
        links.splice(links.indexOf(l), 1);
    });
}

function keydown() {

    if (lastKeyDown !== -1) return;
    lastKeyDown = d3.event.keyCode;

    // ctrl
    if (d3.event.keyCode === 17) {
        svg.nodes.call(layout_force.drag);
        svg.layout.classed('ctrl', true);
    }

    if (!focused_node && !focused_link) return;

    if (SPIC_group == 1) {
        if (focused_node) {
            if (focused_node.type == 'neuron' || focused_node.type == 'output') return;
        }

        if (focused_link) {
            if (focused_link.source.type == 'neuron' && focused_link.target.type == 'neuron') return;
        }
    }

    switch(d3.event.keyCode) {
        case 8: // backspace
        case 46: // delete
            if (focused_node) {
                nodes.splice(nodes.indexOf(focused_node), 1);
                spliceLinksForNode(focused_node);
            } else if (focused_link) {
                links.splice(links.indexOf(focused_link), 1);
            }
            focused_link = null;
            focused_node = null;

            update_after_change();
            break;
        case 70: // F
            if (focused_node) {
                // toggle node reflexivity
                focused_node.fixed = !focused_node.fixed;
            }
            update_after_select();
            break;
        case 82: // R
            if (focused_node) {
                if (focused_node.type != 'neuron') return;
                // toggle node reflexivity
                focused_node.synapse = (focused_node.synapse== 'excitatory' ? 'inhibitory' : 'excitatory');
            }
            update_after_select();
            break;
    }
}

function keyup() {
    lastKeyDown = -1;

    // ctrl
    if(d3.event.keyCode === 17) {
        svg.nodes
            .on('mousedown.drag', null)
            .on('touchstart.drag', null);
        svg.layout.classed('ctrl', false);
    }
}

function initiate_layout(reference) {
    $(reference).empty();

    // set up SVG for D3
    var width  = options.layout.width,
        height = options.layout.height;

    svg.layout = d3.select(reference)
        .append('svg:svg')
            .attr('width', "100%")
            .attr('height', "100%")
            .attr('viewBox', '0 0 ' + width + ' ' + height)
            .attr('id', 'layout');

    // init D3 force layout
    layout_force = d3.layout.force()
        .nodes(nodes)
        .links(links)
        .size([options.layout.width, options.layout.height])
        .linkDistance(options.layout.linkDistance)
        .charge(options.layout.charge)
        .on('tick', tick);

    // define arrow markers for graph links
    svg.layout.append('svg:defs').append('svg:marker')
            .attr('id', 'arrow-marker')
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 6)
            .attr('markerWidth', 3)
            .attr('markerHeight', 3)
            .attr('orient', 'auto')
        .append('svg:path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('fill', '#000');

    // define arrow markers for graph links
    svg.layout.append('svg:defs').append('svg:marker')
            .attr('id', 'circle-marker')
            .attr('viewBox', '-5 -5 10 10')
            .attr('refX', 2)
            .attr('markerWidth', 3)
            .attr('markerHeight', 3)
            .attr('orient', 'auto')
        .append('svg:circle')
            .attr('r', '5')
            .attr('fill', '#000');

    // line displayed when dragging new nodes
    drag_line = svg.layout.append('svg:path')
        .attr('class', 'link dragline hidden')
        .attr('d', 'M0,0L0,0');

    // handles to link and node element groups
    svg.links = svg.layout.append('svg:g').attr("id", "links").selectAll('path');
    svg.internodes = svg.layout.append('svg:g').attr("id", "internodes").selectAll('ellipse');
    svg.weights = svg.layout.append('svg:g').attr("id", "weights").selectAll('text');
    svg.nodes = svg.layout.append('svg:g').attr("id", "nodes").selectAll('g');

    // app starts here
    svg.layout
        .on('dblclick', dblclick)
        .on('mousedown', mousedown)
        .on('mousemove', mousemove)
        .on('mouseup', mouseup);
    d3.select(this)
        .on('keydown', keydown)
        .on('keyup', keyup);
}
