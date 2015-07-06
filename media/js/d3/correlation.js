function getPearsons(x, y) {
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

function calc_correlation(array1, array2, mode) {
    var values = [];

    if (mode == 'same') {
        return getPearson(array1, array2);
    } else if (mode == 'full') {
        var values = {};

        for (var i=0; i<array1.length; i++) {
            var array1_part = array1.slice(array1.length-i-1,array1.length);
            var coef = getPearsons(array1_part, array2)
            if (!(isNaN(coef))) {
                values[i] = {x: i*10, y: coef};
            }
        }

        for (var i=1; i<array2.length; i++) {
            var array2_part = array2.slice(i,array2.length+1);
            var coef = getPearsons(array1, array2_part);
            if (!(isNaN(coef))) {
                values[i+array1.length] = {x: (i+array1.length)*options.histogram.binwidth, y: coef};
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
                values.push({x: i*options.histogram.binwidth - options.histogram.binwidth/2 - data.spike_detector.meta.simTime/2, y: coef});
            } else {
                values.push({x: i*options.histogram.binwidth - options.histogram.binwidth/2 - data.spike_detector.meta.simTime/2, y: 0.});
            }
        }
    }

    return values;
}

function draw_correlation_plot(reference, data) {
    $(reference).empty();

    var margin = {top: 30, right: 20, bottom: 35, left: 45},
        width = options.correlation.width - margin.left - margin.right,
        height = options.correlation.height - margin.top - margin.bottom;

    var x = d3.scale.linear()
        .domain([data[0].x, data[data.length-1].x + options.histogram.binwidth])
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
        .ticks(2);

    var svg = d3.select(reference).append("svg:svg")
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("viewBox", "0 0 " + (width+margin.left+margin.right) + " " + (height+margin.top+margin.bottom))
        .attr('class', 'spike_detector');

    svg.append("svg:text")
        .attr("class", "title")
        .attr("x", margin.right)
        .attr("y", (margin.top/2+5))
        .text("Correlation plot");

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
        .text("Delay (ms)");

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
        .text("Score");

    var bar = g.selectAll(".bar")
        .data(data)
      .enter().append("g")
        .attr("class", "bar")
        .attr("transform", function(d) { return "translate(" + x(d.x) + ","+ (d.y>0? y(d.y): y(0)) + ")"; });

    bar.append("svg:rect")
        .attr("x", 1)
        .attr("width", width/data.length-2)
        .attr("height", function(d) { return d.y>=0? height/2 - y(d.y): y(d.y)- y(0); });

}

function update_correlation(reference) {
    $(reference).empty();
    if (selected_node2 && selected_node) {
        if (selected_node.id in data.spike_detector.hist[options.histogram.binwidth] && selected_node2.id in data.spike_detector.hist[options.histogram.binwidth]) {
            var array1 = data.spike_detector.hist[options.histogram.binwidth][selected_node.id]['hist'],
                array2 = data.spike_detector.hist[options.histogram.binwidth][selected_node2.id]['hist'];
            draw_correlation_plot(reference, calc_correlation(array1, array2, 'valid'))
        };
    } else if (selected_node) { 
        if (selected_node.id in data.spike_detector.hist[options.histogram.binwidth]) {
            var array1 = data.spike_detector.hist[options.histogram.binwidth][selected_node.id]['hist'];
            draw_correlation_plot(reference, calc_correlation(array1, array1, 'valid'))
        };
    };
}

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

