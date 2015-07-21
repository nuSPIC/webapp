function draw_voltmeter(reference) {
    $(reference).empty();

    var times = data.voltmeter.times_reduced;

    var margin = {top: 30, right: 20, bottom: 40, left: 45},
        width = options.voltmeter.width - margin.left - margin.right,
        height = 300 - margin.top - margin.bottom;

    var xScale = d3.scale.linear().range([0, width]).domain([0, simulation_stop]),
        yScale = d3.scale.linear().range([height, 0]).domain([
            Math.floor(data.voltmeter.meta.Vm_min-2.0),
            Math.ceil(data.voltmeter.meta.Vm_max+2.0)]);

    var xAxis = d3.svg.axis().scale(xScale).orient("bottom").ticks(3),
        yAxis = d3.svg.axis().scale(yScale).orient("left").tickSize(-width).ticks(5);

    var line = d3.svg.line()
        .interpolate("monotone")
        .x(function(d, i) { return xScale(times[i]); })
        .y(function(d) { return yScale(d); });

    var svg = d3.select(reference).append("svg:svg")
        .attr("width", "100%")
        .attr("viewBox", "0 0 " + (width+margin.left+margin.right) + " " + (height+margin.top+margin.bottom))
        .attr("class", "voltmeter")
        .call(d3.behavior.zoom().x(xScale).on("zoom", zoomed));

    svg.append("svg:defs").append("clipPath")
        .attr("id", "clip")
      .append("rect")
        .attr("width", width)
        .attr("height", height);

    var g = svg.append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
        .attr("class", "voltmeter");

    g.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

    g.append("g")
      .attr("class", "y axis")
      .call(yAxis);

    for (var i = 0; i < data.voltmeter.V_m.length; i++) {
        g.append("svg:path")
            .datum(data.voltmeter.V_m[i].values_reduced)
            .attr("class", "line")
            .attr("clip-path", "url(#clip)")
            .attr("d", line)
            .attr("id", "neuron_" + data.voltmeter.meta.neurons[i].id.toString());
    }

    g.append("svg:text")
        .attr("class", "x label")
        .attr("text-anchor", "middle")
        .attr("x", width/2)
        .attr("y", height+margin.bottom-5)
        .text("Time (ms)");

    g.append("svg:text")
        .attr("class", "y label")
        .attr("text-anchor", "middle")
        .attr("x", -height/2)
        .attr("y", -(margin.left-5))
        .attr("dy", ".75em")
        .attr("transform", "rotate(-90)")
        .text("Membrane potential (mV)");

    function zoomed() {
        svg.select(".x.axis").call(xAxis);
        svg.select(".y.axis").call(yAxis);
        svg.selectAll(".line").attr("d", line)
    }
}
