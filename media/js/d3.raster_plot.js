var draw_raster_plot = function(reference, dataset, time, neurons, xticks) {

$(reference).empty()

var margin = {top: 0, right: 20, bottom: 0, left: 40},
    width = $(reference).width() - margin.left - margin.right,
    height = neurons.length*12 - margin.top - margin.bottom;

var x = d3.scale.linear()
    .domain([0, time])
    .range([0, width]);

var y = d3.scale.linear()
    .domain([0, neurons.length+1])
    .range([0, height]);

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left")
    .tickSize(-width)
    .ticks(neurons.length);

var svg = d3.select(reference).append("svg:svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

//svg.append("g")
//    .attr("class", "y axis")
//    .attr("transform", "translate(0,0)")
//    .call(yAxis);

//var xrule = svg.selectAll("g.x")
//    .data(x.ticks(xticks))
//  .enter().append("g")
//    .attr("class", "x");

//xrule.append("line")
//    .attr("x1", x)
//    .attr("x2", x)
//    .attr("y1", 0)
//    .attr("y2", height);

//xrule.append("text")
//    .attr("x", x)
//    .attr("y", height + 3)
//    .attr("dy", ".71em")
//    .attr("text-anchor", "middle");

var yrule = svg.selectAll("g.y")
    .data(neurons)
  .enter().append("g")
    .attr("class", "y");

yrule.append("line")
    .attr("x1", 0)
    .attr("x2", width)
    .attr("y1", y)
    .attr("y2", y);

yrule.append("text")
    .attr("x", -3)
    .attr("y", y)
    .attr("dy", ".35em")
    .attr("text-anchor", "end")
    .text(y.tickFormat(neurons.length));

svg.append("text")
    .attr("class", "y label")
    .attr("text-anchor", "middle")
    .attr("x", -height/2)
    .attr("y", -35)
    .attr("dy", ".75em")
    .attr("transform", "rotate(-90)")
    .text("Neuron ID");

svg.selectAll("circle")
    .data(dataset)
  .enter().append("circle")
    .attr("class", "dot")
    .attr("cx", function(d) { return x(d.x); })
    .attr("cy", function(d) { return y(d.y); })
    .attr("r", 1.5);
}
