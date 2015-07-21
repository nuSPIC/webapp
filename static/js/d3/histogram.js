function draw_histogram(reference) {
    $(reference).empty()

    // A formatter for counts.
    var formatCount = d3.format(",.0f");

    var margin = {top: 30, right: 20, bottom: 35, left: 40},
        width = options.histogram.width - margin.left - margin.right,
        height = options.histogram.height - margin.top - margin.bottom;

    var xScale = d3.scale.linear()
        .range([0, width])
        .domain([0, simulation_stop]);

    var hist = d3.layout.histogram()
        .bins(xScale.ticks(parseInt(simulation_stop / options.histogram.binwidth)))
        (data.spike_detector.times);

    var yScale = d3.scale.linear()
        .range([height, 0])
        .domain(d3.extent(hist, function(d) { return d.y }))
        .nice(10);

    var xAxis = d3.svg.axis()
        .scale(xScale)
        .orient("bottom")
        .ticks(5);

    var yAxis = d3.svg.axis()
        .scale(yScale)
        .orient("left")
        .tickSize(-width)
        .ticks(2);

    var svg = d3.select(reference).append("svg")
        // .attr('width', width + margin.right + margin.left)
        // .attr('height', height + margin.top + margin.bottom)
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("viewBox", "0 0 " + (width+margin.left+margin.right) + " " + (height+margin.top+margin.bottom))
      .append('g')
        .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')
        .attr("class", "spike_detector")
      .call(d3.behavior.zoom().x(xScale).on("zoom", zoomed));

    svg.append("rect")
          .attr("x", 0)
          .attr("y", 0)
          .attr("width", width )
          .attr("height", height )
          .style("fill", 'white');

    svg.append("text")
        .attr("class", "title")
        .attr("x", margin.right)
        .attr("y", -10)
        .text("Histogram of population activity");

    svg.selectAll(".bar")
        .data(hist)
      .enter().append("rect")
        .attr("class", "bar")
        .attr("x", function(d) {return xScale(d.x)+.5; })
        .attr("y", function(d) {return yScale(d.y); })
        .attr("width", width / hist.length - 1)
        .attr("height", function(d) { return height - yScale(d.y); });

    // draw the x axis
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)

    // draw the y axis
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)

    svg.append("text")
        .attr("class", "x label")
        .attr("text-anchor", "middle")
        .attr("x", width/2)
        .attr("y", height + margin.bottom - 5)
        .text("Time (ms)");

    svg.append("text")
        .attr("class", "y label")
        .attr("text-anchor", "middle")
        .attr("y", -38)
        .attr('x', -height/2)
        .attr("dy", ".71em")
        .attr("transform", "rotate(-90)")
        .text("Spike count");

    function zoomed() {
        svg.select(".x.axis").call(xAxis);
        svg.select(".y.axis").call(yAxis);
        svg.selectAll(".bar").attr("transform", "translate(" + d3.event.translate[0] + ",0)scale(" + d3.event.scale + ", 1)");
    }

};
