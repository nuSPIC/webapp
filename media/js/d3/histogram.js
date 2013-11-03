function draw_histogram(reference) {
    $(reference).empty()

    // A formatter for counts.
    var formatCount = d3.format(",.0f");

    var margin = {top: 30, right: 20, bottom: 35, left: 50},
        width = options.histogram.width - margin.left - margin.right,
        height = options.histogram.height - margin.top - margin.bottom;

    var xScale = d3.scale.linear().range([0, width]).domain([0, simulation_stop]);

    var hist = d3.layout.histogram()
        .bins(xScale.ticks(parseInt(simulation_stop / options.histogram.binwidth)))
        (data.spike_detector.times);

    yScale = d3.scale.linear().range([height, 0]).domain([0, Math.ceil(d3.max(hist, function(d) { return d.y*1000.0/d.dx/data.spike_detector.meta.neurons.length; }))]);

    var xAxis = d3.svg.axis().scale(xScale).orient("bottom").ticks(5);
    var yAxis = d3.svg.axis().scale(yScale).orient("left").tickSize(-width).ticks(2);

    var svg = d3.select(reference).append("svg:svg")
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("viewBox", "0 0 " + (width+margin.left+margin.right) + " " + (height+margin.top+margin.bottom))
        .attr("class", "spike_detector");

    svg.append("svg:text")
        .attr("class", "title")
        .attr("x", margin.right)
        .attr("y", (margin.top/2+5))
        .text("Histogram of population activity");

    var g = svg.append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    g.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    g.append("svg:text")
        .attr("class", "x label")
        .attr("text-anchor", "middle")
        .attr("x", width/2)
        .attr("y", height + margin.bottom - 5)
        .text("Time (ms)");

    g.append("g")
        .attr("class", "y axis")
        .attr("transform", "translate(0,0)")
        .call(yAxis);

    g.append("svg:text")
        .attr("class", "y label")
        .attr("text-anchor", "middle")
        .attr("x", -height/2)
        .attr("y", -(margin.left-5))
        .attr("dy", ".75em")
        .attr("transform", "rotate(-90)")
        .text("Rate (Hz)");

    var bar = g.selectAll(".bar")
        .data(hist)
      .enter().append("g")
        .attr("class", "bar")
        .attr("transform", function(d) { return "translate(" + xScale(d.x) + "," + yScale(d.y*1000.0/d.dx/data.spike_detector.meta.neurons.length) + ")"; });

    bar.append("svg:rect")
        .attr("x", 1)
        .attr("width", function(d) { return xScale(d.dx) - 2 })
        .attr("height", function(d) { return height - yScale(d.y*1000.0/d.dx/data.spike_detector.meta.neurons.length); });
};
