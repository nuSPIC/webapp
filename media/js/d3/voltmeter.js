function draw_voltmeter(reference, times, values, title) {

    var margin = {top: 10, right: 10, bottom: 20, left: 40},
        width = options.voltmeter.width - margin.left - margin.right,
        height = options.voltmeter.height - margin.top - margin.bottom;

    var x = d3.scale.linear().range([0, width]),
        y = d3.scale.linear().range([height, 0]);

    x.domain(d3.extent(values.map(function(d, i) { return times[i]; })));
    y.domain(d3.extent(values.map(function(d) { return d; })));

    var xAxis = d3.svg.axis().scale(x).orient("bottom"),
        yAxis = d3.svg.axis().scale(y).orient("left");

    var brush = d3.svg.brush()
        .x(x)
        .on("brush", brushed);

    var line = d3.svg.line()
        .interpolate("monotone")
        .x(function(d, i) { return x(times[i]); })
        .y(function(d) { return y(d); });

    var svg = d3.select(reference).append("svg:svg")
        .attr("width", "100%")
        .attr("viewBox", "0 0 " + (width+margin.left+margin.right) + " " + (height+margin.top+margin.bottom))
        .attr("class", "voltmeter");

    svg.append("svg:defs").append("clipPath")
        .attr("id", "clip")
      .append("rect")
        .attr("width", width)
        .attr("height", height);

    var focus = svg.append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
        .attr("class", "focus");

    focus.append("svg:path")
      .datum(values)
      .attr("clip-path", "url(#clip)")
      .attr("d", line);

    focus.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

//    focus.append("g")
//      .attr("class", "y axis")
//      .call(yAxis);

    svg.append("svg:text")
        .attr("class", "title")
        .attr("y", (height+margin.top))
        .text(title);

    return (x, focus, line, xAxis)
}

function brushed() {
    x.domain(brush.empty() ? x2.domain() : brush.extent());
    focus.select("path").attr("d", line);
    focus.select(".x.axis").call(xAxis);
};
