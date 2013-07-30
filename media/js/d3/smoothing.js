// fill array with value
function newFilledArray(len, val) {
    var rv = new Array(len);
    while (--len >= 0) {
        rv[len] = val;
    }
    return rv;
}

// calculate psth
function psth_calc(fac) {
    var psth = newFilledArray(simTime, 0.);
    for (var n=0; n<times.length; n++) {
        psth[parseInt(times[n])] += fac;
    };
    return psth
};

// Various kernel function for smoothing psth
// http://en.wikipedia.org/wiki/Uniform_kernel#Kernel_functions_in_common_use

// uniform kernel
function weightUniform() {
    var weight = [];
    for (var i=-kw;i<=kw;i++) {
        weight.push(.5);
    }
    return weight
}

// triangular kernel
function weightTriangular() {
    var weight = [];
    for (var i=-kw;i<=kw;i++) {
        var u = i / kw;
        weight.push(1-Math.abs(u));
    }
    return weight
}

// cosine kernel
function weightCosine() {
    var weight = [];
    for (var i=-kw;i<=kw;i++) {
        var u = i / kw;
        weight.push(Math.PI/4 * Math.cos(Math.PI/2 * u));
    }
    return weight
}

// Epanechnikov kernel
function weightEpanechnikov() {
    var weight = [];
    for (var i=-kw;i<=kw;i++) {
        var u = i / kw;
        weight.push(3/4*(1-Math.pow(u,2)));
    }
    return weight
}

// Quartic kernel
function weightQuartic() {
    var weight = [];
    for (var i=-kw;i<=kw;i++) {
        var u = i / kw;
        weight.push(15/16*Math.pow(1-Math.pow(u,2),2));
    }
    return weight
}

// Triweight kernel
function weightTriweight() {
    var weight = [];
    for (var i=-kw;i<=kw;i++) {
        var u = i / kw;
        weight.push(35/32*Math.pow(1-Math.pow(u,2),3));
    }
    return weight
}

// Tricube kernel
function weightTricube() {
    var weight = [];
    for (var i=-kw;i<=kw;i++) {
        var u = i / kw;
        weight.push(70/81*Math.pow(1-Math.pow(Math.abs(u),3),3));
    }
    return weight
}

// Gauss kernel
function weightGauss(win) {
    var weight = [];
    for (var i=-win/2;i<=win/2;i++) {
        var u = i / kw;
        weight.push(Math.exp(-Math.pow(u,2)/2) / Math.sqrt(2*Math.PI));
    }
    return weight
}

// smooth all time values
function smooth(fac) {
    var win = 2*kw; 
    if (kernel_function == 'gauss') {
        win *= 4;
        weight = weightGauss(win)
    } else if (kernel_function == 'tricube') {
        weight = weightTricube()
    } else if (kernel_function == 'triweight') {
        weight = weightTriweight()
    } else if (kernel_function == 'quartic') {
        weight = weightQuartic()
    } else if (kernel_function == 'epanechnikov') {
        weight = weightEpanechnikov()
    } else if (kernel_function == 'cosine') {
        weight = weightCosine()
    } else if (kernel_function == 'triangular') {
        weight = weightTriangular()
    } else if (kernel_function == 'uniform') {
        weight = weightUniform()
    } else {
        return psth;
    }

    var weightSum = d3.sum(weight)
    
    var pre = newFilledArray(win/2, 0)
    var post = newFilledArray(win/2+1, 0)
    var psth_extented = pre.concat(psth, post)
    
    var smoothed = newFilledArray(psth.length, 0.)
    for (var i=0; i<smoothed.length; i++) {
        var psth_slice = psth_extented.slice(i, i+win+1)                                                // get a window of each time step
        var val = psth_slice.map(function(element,index,array){return element*weight[index]})           // overlay kernel weight on window
        smoothed[i] = fac * d3.sum(val) // weightSum                                                     // normalize values, the area has to be the same.
    }
    return smoothed;
};

// Data of Spikes.
var senders = spike_detector_data['senders'],
times = spike_detector_data['times'],
simTime = spike_detector_data['simTime'],
neurons = spike_detector_data['neurons'],
fig = spike_detector_data['fig'],
figures = {};

// Settings for PSTH
var hist_binwidth = 10;     // Bin width of histogram. default: 10ms
var nr_spikes = 1000,
kw = 100,               // smoothing area 100 ms at both side > 200 ms
sd_scale = true;

// Calculate PSTH
var psth = psth_calc(1);

// Smooth PSTH
var kernel_function = 'off';
var psth_smooth = smooth(1);

// Default settings for draw
var defaults = {
    "spikeDetectorThumbnail": {
        "margin": {top:0, right:0, bottom:75, left:0},
        "padding": {top:10, right:15, bottom:15, left:25},
        "neuronLineHeight": 10,
        "h2": 100,
    },
    "spikeDetectorView": {
        "margin": {top:20, right:5, bottom:75, left:5},
        "padding": {top:10, right:15, bottom:15, left:25},
        "neuronLineHeight": 12,
        "h2": 350,
    }
};

// Set global variable
function drawSpikeDetector(figID) {
    $( "#"+figID).find( "#spikes" ).html("")
    $( "#"+figID).find( "#psth" ).html("")
    
    $( "#"+figID).find( ".sd_scale").attr("checked", sd_scale);
    $( "#"+figID).find( ".kernel_width" ).find( ".spinedit" ).val(kw);
    $( "#"+figID).find( "."+ kernel_function ).attr("selected", true);
    
    var figure = d3.select("#"+figID);
    var defVal = defaults[figID.toString()];

      // The spikes panel.
    var padding_horizontal = defVal.padding.right + defVal.padding.left;
    var padding_vertical = defVal.padding.top + defVal.padding.bottom;

    var margin_horizontal = defVal.margin.right + defVal.margin.left;
    var margin_vertical = defVal.margin.top + defVal.margin.bottom;
    
      // Size of panels.
    var w = parseInt($("#"+figID).css("width")) - padding_horizontal - margin_horizontal;
    var h1 = defVal.neuronLineHeight * neurons.length;
    var h2 = defVal.h2;
    var h = h1 + h2 + padding_vertical + margin_vertical;   
    $("#"+figID).css("height", h);
    var response = {"w": w, "h2": h2};
    
    // Calculate scales and axis of spike panel.
    var xScale = d3.scale.linear().domain([0, simTime]).range([20, w]);
    var xTicks = d3.svg.axis().scale(xScale).ticks(w/50).tickSize(figID=="spikeDetectorView"? -h2: -9);
    
    var spikes_yScale = d3.scale.linear().domain([0,neurons.length]).range([0, h1]);
    var spikes_yTicks = d3.svg.axis().scale(spikes_yScale).ticks(neurons.length).orient("left").tickFormat(function(i) {return neurons[i-1]}).tickSize(-w);  
    
        // Prep for plot
    var psth_yScale = d3.scale.linear().domain([sd_scale? d3.min(psth_smooth):0, d3.max(psth_smooth)]).range([h2, 0]);
    var psth_yTicks = d3.svg.axis().scale(psth_yScale).ticks(h2/30).orient("left").tickSize(figID=="spikeDetectorView"? -w: -9);
  
    var psth_data = d3.range(psth_smooth.length).map(function(i) {
        return {x: i, y: psth_smooth[i]};
    });
    
    var psth_line = d3.svg.line()
        .x(function(d) { return xScale(d.x); })
        .y(function(d) { return psth_yScale(d.y); });
    
       
    var spikes_fig = figure.select("#spikes").append("svg:svg")
        .attr("width", w + padding_horizontal)
        .attr("height", h1 + padding_vertical)

    var spikes_panel = spikes_fig.append("svg:g")
        .attr("transform", "translate(" + defVal.padding.left + "," + defVal.padding.top + ")");

    // Add the y-axis.
    spikes_panel.append("g")
        .attr("class", "y axis spikes")
        .call(spikes_yTicks)
        .attr("transform", "translate("+ (parseInt(defVal.padding.left)-10).toString() +",0)");

    // Add circles of spikes.
    var spikes = spikes_panel.selectAll("circle")
        .data(senders)
        .enter().append("circle") 
        .attr("cx", function(d,i) {return xScale(times[i])})
        .attr("cy", function(i) {return spikes_yScale(i)}) 
        .attr("r", 1.5)
        .attr("id", function(d,i) {return "id_spike_"+i})
        .attr("sender", function(d) {return d})
        .attr("time", function(d,i) {return times[i]});


    // The PSTH panel
    var psth_fig = figure.select("#psth").append("svg")
        .attr("width", w + padding_horizontal)
        .attr("height", h2 + padding_vertical)

    spikes_fig.append("text").text(times.length +" spikes").attr("dy", "1em").attr("transform", "translate(" + w/2 + ",0)");

    var psth_panel = psth_fig.append("g")
        .datum(psth_data)
        .attr("transform", "translate(" + defVal.padding.left + "," + defVal.padding.top + ")");
    response["psth_panel"] = psth_panel

    // Add the x-axis.
    var xAxis = psth_panel.append("g")
        .attr("class", "x axis psth")
        .attr("transform", "translate(0," + h2 + ")")
        .call(xTicks);
       
    // Add the y-axis.
    var psth_yAxis = psth_panel.append("g")
        .attr("class", "y axis psth")
        .call(psth_yTicks)
        .attr("transform", "translate("+ (parseInt(defVal.padding.left)-10).toString() +",0)");
    response["psth_yAxis"] = psth_yAxis
        
    // Add path of psth
    psth_panel.append("path")
      .attr("class", "line psth")
      .attr("d", psth_line);

    return response
}

// Update plot
function update() {
    psth_smooth = smooth(1);
    var psth_data = d3.range(psth_smooth.length).map(function(i) {
        return {x: i, y: psth_smooth[i]};
    });
    
    $( ".spikeDetector" ).each(function() {
        var figID = $(this).attr("id");
        var fig = figures[figID];
        var defVal = defaults[figID];
        
        var xScale = d3.scale.linear().domain([0, simTime]).range([20, fig.w]);
        var psth_yScale = d3.scale.linear().domain([sd_scale? d3.min(psth_smooth):0, d3.max(psth_smooth)]).range([fig.h2, 0]);
        var psth_yTicks = d3.svg.axis().scale(psth_yScale).ticks(fig.h2/30).orient("left").tickSize(figID=="spikeDetectorView"? -fig.w: -9);
        
        var psth_line = d3.svg.line()
            .x(function(d) { return xScale(d.x); })
            .y(function(d) { return psth_yScale(d.y); });

        fig.psth_yAxis.call(psth_yTicks);
        fig.psth_panel.selectAll("path").datum(psth_data).attr("d", psth_line);
    })
}

function loadSpikeDetector() {
  
    $( ".kernel_width .spinedit" ).SpinEdit({'min': 1, 'max': simTime/5, 'step': 1})
    
    $( ".scale_to_fit .sd_scale" ).on("change", function() {
        sd_scale = this.checked;
        update();
        $( ".scale_to_fit .sd_scale").attr("checked", sd_scale)
    });
  
    $( ".kernel_width .spinedit" ).on("change mouseup mousewheel DOMMouseScroll", function () { 
        kw = parseFloat($(this).val());
        update()
        $( ".spinedit" ).val(kw);
    });
    
    $( ".kernel_function select" ).on("change", function() {
        kernel_function = $(this).val()
        update()
        $( "."+ kernel_function ).attr("selected", true);
    });
}
