// fill array with value
function newFilledArray(len, val) {
    var rv = new Array(len);
    while (--len >= 0) {
        rv[len] = val;
    }
    return rv;
}

function fillArray(value, len) {
    var arr = [];
    for (var idx = 0; idx < value.length; idx++) {
        for (var i = 0; i < len; i++) {
            arr.push(1000.0 * parseFloat(value[idx].y) / parseFloat(value[idx].dx));
        };
    };
    return arr;
}

// Various kernel function for smoothing psth
// http://en.wikipedia.org/wiki/Uniform_kernel#Kernel_functions_in_common_use

// uniform kernel
function weightUniform(kw) {
    var weight = [];
    for (var i=-kw;i<=kw;i++) {
        weight.push(.5);
    }
    return weight
}

// triangular kernel
function weightTriangular(kw) {
    var weight = [];
    for (var i=-kw;i<=kw;i++) {
        var u = i / kw;
        weight.push(1-Math.abs(u));
    }
    return weight
}

// cosine kernel
function weightCosine(kw) {
    var weight = [];
    for (var i=-kw;i<=kw;i++) {
        var u = i / kw;
        weight.push(Math.PI/4 * Math.cos(Math.PI/2 * u));
    }
    return weight
}

// Epanechnikov kernel
function weightEpanechnikov(kw) {
    var weight = [];
    for (var i=-kw;i<=kw;i++) {
        var u = i / kw;
        weight.push(3/4*(1-Math.pow(u,2)));
    }
    return weight
}

// Quartic kernel
function weightQuartic(kw) {
    var weight = [];
    for (var i=-kw;i<=kw;i++) {
        var u = i / kw;
        weight.push(15/16*Math.pow(1-Math.pow(u,2),2));
    }
    return weight
}

// Triweight kernel
function weightTriweight(kw) {
    var weight = [];
    for (var i=-kw;i<=kw;i++) {
        var u = i / kw;
        weight.push(35/32*Math.pow(1-Math.pow(u,2),3));
    }
    return weight
}

// Tricube kernel
function weightTricube(kw) {
    var weight = [];
    for (var i=-kw;i<=kw;i++) {
        var u = i / kw;
        weight.push(70/81*Math.pow(1-Math.pow(Math.abs(u),3),3));
    }
    return weight
}

// Gauss kernel
function weightGauss(kw, win) {
    var weight = [];
    for (var i=-win/2;i<=win/2;i++) {
        var u = i / kw;
        weight.push(Math.exp(-Math.pow(u,2)/2) / Math.sqrt(2*Math.PI));
    }
    return weight
}

// smooth histogram
function smooth_hist(hist) {
    var kw = options.smoothed_histogram.kw,
        kernel_function = options.smoothed_histogram.kernel_function,
        fac = 1;

    var win = 2*kw;
    if (kernel_function == 'gauss') {
        win *= 4;
        weight = weightGauss(kw, win)
    } else if (kernel_function == 'tricube') {
        weight = weightTricube(kw)
    } else if (kernel_function == 'triweight') {
        weight = weightTriweight(kw)
    } else if (kernel_function == 'quartic') {
        weight = weightQuartic(kw)
    } else if (kernel_function == 'epanechnikov') {
        weight = weightEpanechnikov(kw)
    } else if (kernel_function == 'cosine') {
        weight = weightCosine(kw)
    } else if (kernel_function == 'triangular') {
        weight = weightTriangular(kw)
    } else if (kernel_function == 'uniform') {
        weight = weightUniform(kw)
    } else {
        return hist;
    }

    var weightSum = d3.sum(weight)

    var pre = newFilledArray(win/2, 0)
    var post = newFilledArray(win/2+1, 0)
    var filled_hist = fillArray(hist, options.histogram.binwidth)
    var extended_hist = pre.concat(filled_hist, post)

    var smoothed_hist = newFilledArray(filled_hist.length, 0.0)
    for (var i=0; i<smoothed_hist.length; i++) {
        var hist_slice = extended_hist.slice(i, i+win+1)                                                // get a window of each time step
        var val = hist_slice.map(function(element,index,array){return element*weight[index]})           // overlay kernel weight on window
        smoothed_hist[i] = fac * d3.sum(val) / weightSum                                                     // normalize values, the area has to be the same.
    }
    return [smoothed_hist, d3.max(smoothed_hist)]
};

function draw_smoothed_histogram(reference) {
    $(reference).empty();

    var times = d3.range(0,simulation_stop)

    var margin = {top: 30, right: 20, bottom: 35, left: 40},
        width = options.smoothed_histogram.width - margin.left - margin.right,
        height = options.smoothed_histogram.height - margin.top - margin.bottom;

    var xScale = d3.scale.linear().range([0, width]).domain([0, simulation_stop]),
        yScale = d3.scale.linear().range([height, 0]).domain([-2, Math.ceil(data.spike_detector.hist[options.histogram.binwidth]['smooth_ymax'])+2]);

    var xAxis = d3.svg.axis().scale(xScale).orient("bottom").ticks(5),
        yAxis = d3.svg.axis().scale(yScale).orient("left").tickSize(-width).ticks(2);

    var line = d3.svg.line()
        .interpolate("monotone")
        .x(function(d, i) { return xScale(times[i]); })
        .y(function(d) { return yScale(d); });

    var svg = d3.select(reference).append("svg:svg")
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("viewBox", "0 0 " + (width+margin.left+margin.right) + " " + (height+margin.top+margin.bottom))
        .attr("class", "spike_detector smoothed_histogram")
        .call(d3.behavior.zoom().x(xScale).on("zoom", zoomed));

    svg.append("svg:text")
        .attr("class", "title")
        .attr("x", margin.right)
        .attr("y", (margin.top/2+5))
        .text("Smoothed histogram of neural activity");

    svg.append("svg:defs").append("clipPath")
        .attr("id", "clip")
      .append("rect")
        .attr("width", width)
        .attr("height", height);

    var g = svg.append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
        .attr("class", "smoothed_histogram");

    g.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

    g.append("g")
      .attr("class", "y axis")
      .attr("transform", "translate(0,0)")
      .call(yAxis);

    for (var i in data.spike_detector.meta.neurons) {
        g.append("svg:path")
            .datum(data.spike_detector.hist[options.histogram.binwidth][data.spike_detector.meta.neurons[i].id]['smooth'])
            .attr("class", "line")
            .attr("clip-path", "url(#clip)")
            .attr("d", line)
            .attr("id", "neuron_" +data.spike_detector.meta.neurons[i].id.toString());
    }

    g.append("svg:text")
        .attr("class", "y label")
        .attr("text-anchor", "middle")
        .attr("x", -height/2)
        .attr("y", -(margin.left-5))
        .attr("dy", ".75em")
        .attr("transform", "rotate(-90)")
        .text("Rate (Hz)");

    function zoomed() {
        svg.select(".x.axis").call(xAxis);
        svg.select(".y.axis").call(yAxis);
        svg.selectAll(".line").attr("d", line);
    }
}
