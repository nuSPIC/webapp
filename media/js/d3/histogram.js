function draw_histogram(reference){
    $(reference).empty()

    // A formatter for counts.
    var formatCount = d3.format(",.0f");

    var margin = {top: 30, right: 20, bottom: 35, left: 45},
        width = options.histogram.width - margin.left - margin.right,
        height = options.histogram.height - margin.top - margin.bottom;

    var x = d3.scale.linear()
        .domain([0, data.spike_detector.meta.simTime])
        .range([0, width]);

    var hist = d3.layout.histogram()
        .bins(x.ticks(parseInt(data.spike_detector.meta.simTime / options.histogram.binwidth)))
        (data.spike_detector.times);

    var y = d3.scale.linear()
        .domain([0, d3.max(hist, function(d) { return d.y; })])
        .range([height, 0]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom")
        .ticks(5);

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left")
        .tickSize(-width)
        .ticks(4);

    var svg = d3.select(reference).append("svg:svg")
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("viewBox", "0 0 " + (width+margin.left+margin.right) + " " + (height+margin.top+margin.bottom))
        .attr("class", "spike_detector");

    svg.append("svg:text")
        .attr("class", "title")
        .attr("x", margin.right)
        .attr("y", (margin.top/2+5))
        .text("Histogram");

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
        .text("Spike count");

    var bar = g.selectAll(".bar")
        .data(hist)
      .enter().append("g")
        .attr("class", "bar")
        .attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; });

    bar.append("svg:rect")
        .attr("x", 1)
        .attr("width", function(d) { return x(d.dx) - 2 })
        .attr("height", function(d) { return height - y(d.y); });
};
