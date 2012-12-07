var draw_histogram = function(reference, values, time, bins){

$(reference).empty()

// A formatter for counts.
var formatCount = d3.format(",.0f");

var margin = {top: 10, right: 20, bottom: 35, left: 40},
    width = $(reference).width() - margin.left - margin.right,
    height = $(reference).height() - margin.top - margin.bottom;

var x = d3.scale.linear()
    .domain([0, time])
    .range([0, width]);

var data = d3.layout.histogram()
    .bins(x.ticks(bins))
    (values);

var y = d3.scale.linear()
    .domain([0, d3.max(data, function(d) { return d.y; })])
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

var svg = d3.select(reference).append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis);

svg.append("text")
    .attr("class", "x label")
    .attr("text-anchor", "middle")
    .attr("x", width/2)
    .attr("y", height + margin.bottom - 5)
    .text("Time (ms)");

svg.append("g")
    .attr("class", "y axis")
    .attr("transform", "translate(0,0)")
    .call(yAxis);

svg.append("text")
    .attr("class", "y label")
    .attr("text-anchor", "middle")
    .attr("x", -height/2)
    .attr("y", -35)
    .attr("dy", ".75em")
    .attr("transform", "rotate(-90)")
    .text("Spike count");

var bar = svg.selectAll(".bar")
    .data(data)
  .enter().append("g")
    .attr("class", "bar")
    .attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; });

bar.append("rect")
    .attr("x", 1)
    .attr("width", function(d) { return x(d.dx) - 1 })
    .attr("height", function(d) { return height - y(d.y); });
};
