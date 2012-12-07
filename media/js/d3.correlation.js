var getPearsons = function(x, y) {
    var n = 0;

    if (x.length <= y.length) {
        n = x.length;
    } else {
        n = y.length;
    }

    var ax = 0, ay = 0;
    for (var i=0; i<n; i++) {
    // finds the mean
        ax += x[i].y;
        ay += y[i].y;
    }
    ax /= n;
    ay /= n;

    var xt = 0, yt = 0, sxx = 0, syy = 0, sxy = 0;
    for (var j=0; j<n; j++) {
    // compute correlation coefficient
        xt=x[j].y-ax;
        yt=y[j].y-ay;
        sxx += xt*xt;
        syy += yt*yt;
        sxy += xt*yt;
    }

    return sxy/Math.sqrt(sxx*syy);
}

var calc_correlation = function(array1, array2, mode, binwidth) {
    var values = [];

    if (mode == 'same') {
        return getPearson(array1, array2);
    } else if (mode == 'full') {
        var values = {};

        for (var i=0; i<array1.length; i++) {
            var array1_part = array1.slice(array1.length-i-1,array1.length);
            var coef = getPearsons(array1_part, array2)
            if (!(isNaN(coef))) {
                values[i] = {x: i*10, y: coef, dx: 10};
            }
        }

        for (var i=1; i<array2.length; i++) {
            var array2_part = array2.slice(i,array2.length+1);
            var coef = getPearsons(array1, array2_part);
            if (!(isNaN(coef))) {
                values[i+array1.length] = {x: (i+array1.length)*binwidth, y: coef, dx: binwidth};
            }
        }
    } else if (mode == 'valid') {

        for (var i=0; i<=array1.length; i++) {

            if (i < array1.length/2) {
                var A1 = array1.slice(array1.length/2-i,array1.length+1);
                var A2 = array2;
            } else if (i > array1.length/2) {
                var A1 = array1;
                var A2 = array2.slice(i-array2.length/2,array2.length+1);
            } else {
                var A1 = array1;
                var A2 = array2;
            }

            var coef = getPearsons(A1, A2);
            if (!(isNaN(coef))) {
                values.push({x: i*binwidth, y: coef, dx: binwidth});
            }
        }
    }

    return values;
}

var draw_correlation_plot = function(reference, data) {
    var x_shift = data[data.length-1].x/2
$(reference).empty()

var margin = {top: 10, right: 20, bottom: 35, left: 40},
    width = $(reference).width() - margin.left - margin.right,
    height = $(reference).height() - margin.top - margin.bottom;

var x = d3.scale.linear()
    .domain([data[0].x-data[data.length-1].dx/2-x_shift, data[data.length-1].x + data[data.length-1].dx/2-x_shift])
    .range([0, width]);

var y = d3.scale.linear()
    .domain([-1, 1])
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
    .text("Delay (ms)");

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
    .text("Score");

var bar = svg.selectAll(".bar")
    .data(data)
  .enter().append("g")
    .attr("class", "bar")
    .attr("transform", function(d) { return "translate(" + x(d.x-d.dx/2-x_shift) + ","+ (d.y>0? y(d.y): y(0)) + ")"; });

bar.append("rect")
    .attr("x", 1)
    .attr("width", function(d) { return x(d.dx/2-x_shift) - 1 })
    .attr("height", function(d) { return d.y>=0? height/2 - y(d.y): y(d.y)- y(0); })
    .attr("fill", function(d) {
//        return "rgb(" + (d.y<0? parseInt(d.y * 100 + 155):0) + ", " + (d.y==1? 255:0) + ", " + (d.y>0? parseInt(d.y * 100+155):0) + ")";
        return "rgb(0, " + (d.y==1? 205:0) + "," +  (d.y==1? 50:0) + ")";
    });

//    var dataset = d3.range(delay.length).map(function(i) {
//        return {x: delay[i], y: corr[i]};
//    });

//    var line = d3.svg.line()
//        .x(function(d) { return x(d.x); })
//        .y(function(d) { return y(d.y); });

//    var svg = d3.select(reference).append("svg")
//        .datum(dataset)
//        .attr("width", width + margin.left + margin.right)
//        .attr("height", height + margin.top + margin.bottom)
//      .append("g")
//        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

//    svg.append("g")
//        .attr("class", "x axis")
//        .attr("transform", "translate(0," + height + ")")
//        .call(xAxis);

//    svg.append("g")
//        .attr("class", "y axis")
//        .call(yAxis);

//    svg.append("path")
//        .attr("class", "line")
//        .attr("d", line);
}
