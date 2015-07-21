function draw_raster_plot(reference) {
    $(reference).empty()

    var margin = {top: 30, right: 20, bottom: 10, left: 40},
        width = options.raster_plot.width - margin.left - margin.right,
        height = options.raster_plot.height_per_neuron * data.spike_detector.meta.neurons.length;

    var x = d3.scale.linear()
        .domain([0, data.spike_detector.meta.simTime])
        .range([0, width]);

    var y = d3.scale.linear()
        .domain([0, data.spike_detector.meta.neurons.length])
        .range([0, height]);

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left")
        .tickSize(-width)
        .ticks(data.spike_detector.meta.neurons.length);

    var svg = d3.select(reference).append("svg:svg")
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("viewBox", "0 0 " + (width+margin.left+margin.right) + " " + (height+margin.top+margin.bottom))
        .attr('class', 'spike_detector')
        .attr('id', 'raster_plot');

    svg.append("svg:text")
        .attr("class", "title")
        .attr("x", margin.right)
        .attr("y", (margin.top/2+5))
        .text("Raster plot");

    var g = svg.append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    g.append("svg:text")
        .attr("class", "y label")
        .attr("text-anchor", "middle")
        .attr("x", -height/2)
        .attr("y", -(margin.left-5))
        .attr("dy", ".75em")
        .attr("transform", "rotate(-90)")
        .text(data.spike_detector.meta.neurons.length > 3 ? "Neuron ID": "ID");

    var yrule = g.selectAll("g.y")
        .data(data.spike_detector.meta.neurons)
      .enter().append("g")
        .attr("class", "y")
        .attr("id", function(d) {return "neuron" + d.id;});

    yrule.append("svg:line")
        .attr("x1", 0)
        .attr("x2", width)
        .attr("y1", function(d) {return y(data.spike_detector.meta.neurons.indexOf(d)); })
        .attr("y2", function(d) {return y(data.spike_detector.meta.neurons.indexOf(d)); });

    yrule.append("svg:text")
        .attr("x", -3)
        .attr("y", function(d) {return y(data.spike_detector.meta.neurons.indexOf(d)); })
        .attr("dy", ".35em")
        .attr("text-anchor", "end")
        .text( function(d) {return d.id });

    g.selectAll("circle")
        .data(data.spike_detector.senders)
      .enter().append("svg:circle")
        .attr("class", function(d) { return "dot neuron_" + data.spike_detector.meta.neurons[d].id})
        .attr("cx", function(d, i) { return x(data.spike_detector.times[i]); })
        .attr("cy", function(d) { return y(d); })
        .attr("r", 1.5);
}
