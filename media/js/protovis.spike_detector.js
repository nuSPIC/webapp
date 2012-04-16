Array.prototype.sum = function(){
    for(var i=0,sum=0;i<this.length;sum+=this[i++]);
    return sum;
}

function newFilledArray(len, val) {
    var rv = new Array(len);
    while (--len >= 0) {
        rv[len] = val;
    }
    return rv;
}

Object.prototype.clone = function() {
    var newObj = (this instanceof Array) ? [] : {};
    for (i in this) {
        if (i == 'clone') continue;
        if (this[i] && typeof this[i] == "object") {
            newObj[i] = this[i].clone();
        } else newObj[i] = this[i]
        } return newObj;
    };

function psth_calc() {
    psth = newFilledArray(simTime, 0);
    for (var n = 0; n < times.length; n++) {
        psth[parseInt(times[n])] += 1000;
    };
    return psth
};

function triangleSmooth(list, degree) {
    smoothed = newFilledArray(list.length, 0);
    for (var n = 0; n < times.length; n++) {
        smoothed[parseInt(times[n])] += 2/kw * 1000 / nr_spikes;
        for (var m = 1; m <= kw/2; m++) {
            if (parseInt(times[n] - m) >= 0) {
                smoothed[parseInt(times[n] - m)] += 2/kw * ( 1 - (2/kw) * m) * 1000 / nr_spikes;
            }
            if (parseInt(times[n] + m) < smoothed.length) {
                smoothed[parseInt(times[n] + m)] += 2/kw * ( 1 - (2/kw) * m) * 1000 / nr_spikes;
            }
        }
    };
    return smoothed
};

function gaussSmooth(list, degree) {
    var win = degree*2-1;
    weightGauss = [];
    for (i=0;i<=win;i++) {
        j = i-degree+1;
        frac = j/win;
        gauss = 1 / Math.exp((4*(frac))*(4*(frac)));
        weightGauss.push(gauss);
    }
    weightGaussSum = weightGauss.sum()
    
    first_val = newFilledArray(degree-1, list.slice(0,degree).sum()/degree)
    last_val = newFilledArray(degree, list[list.length-1])
    new_list = first_val.concat(list, last_val)
    
    smoothed = newFilledArray(list.length, 0.)
    for (i=0; i < smoothed.length; i++) {
        list_slice = new_list.slice(i, i+win)
        val_gauss = list_slice.map(function(element,index,array){return element*weightGauss[index]})
        smoothed[i] = val_gauss.sum() / weightGaussSum
        }
    return smoothed;
};
  
function prep_vis() {
    
    /* The root panel. */
    var vis = new pv.Panel()
        .width(w)
        .height(h)
        .top(20)
        .right(15) 
        .bottom(15)
        .left(25)
        .canvas("#chart");

    /* The spike panel. */
    var spikes_panel = vis.add(pv.Panel)
        .top(0)
        .height(h1);    

    /* Y-axis and ticks. */
    spikes_panel.add(pv.Rule)
        .data(neuronScale)
        .top(yScale)
        .strokeStyle("rgbs(0,0,0,0)")
      .anchor("left").add(pv.Label)
        .text(function () {return neurons[this.index]});

    /* The dot plot! */
    spikes_panel.add(pv.Dot)
        .data(times)
        .left(function(d) {return xScale(d)})
        .top(function() {return yScale(senders[this.index])})
        .strokeStyle("#000")
        .fillStyle("#000")
        .size(1);

    spikes_panel.add(pv.Label)
        .top(-5)
        .textBaseline("bottom")
        .left(-28)
        .textAlign("left")
        .textStyle("grey")
        .text("neuron id");

    spikes_panel.add(pv.Label)
        .top(-5)
        .textBaseline("bottom")
        .right(0)
        .textAlign("right")
        .textStyle("grey")
        .text(senders.length +" spikes");


    /* The PSTH panel */
    var psth_panel = vis.add(pv.Panel)
        .def("init", function() {
            if (times.length/simTime > 1) {
                var psth_smooth = gaussSmooth(psth, kw);
            } else {
                var psth_smooth = triangleSmooth(psth, kw);                   
            }
            psth_yScale.domain(0, pv.max(psth_smooth, function(d) {return d+1}));
            return psth_smooth;
            })
        .bottom(10)
        .height(h2);

    
    var psth_y = psth_panel.add(pv.Rule)
        .data(psth_yScale.ticks(fig.yticks))
        .bottom(psth_yScale)
        .strokeStyle(function(d) {return d ? "#eee" : "#000"});

    psth_y.anchor("left").add(pv.Label)
        .text(psth_yScale.tickFormat);
        
    psth_panel.add(pv.Rule)
        .data(xScale.ticks(5))
        .left(xScale)
        .strokeStyle(function(d) {return d ? "#eee" : "#000"})
      .anchor("bottom").add(pv.Label)
        .text(xScale.tickFormat);

    psth_panel.add(pv.Label)
        .top(-1)
        .textBaseline("bottom")
        .left(w/2)
        .textAlign("center")
        .text("PSTH");

    /* X-axis label */
    psth_panel.add(pv.Label)
        .bottom(-10)
        .textBaseline("top")
        .left(w/2)
        .textAlign("center")
        .textStyle("grey")
        .text("Time (ms)");

    psth_panel.add(pv.Label)
        .top(-1)
        .textBaseline("bottom")
        .left(-25)
        .textAlign("left")
        .textStyle("grey")
        .text("Hz");
        
    var psth_area = psth_panel.add(pv.Area)
        .data(function() {return psth_panel.init()})
        .left(function(d) {return xScale(this.index)})
        .height(function(d) {return psth_yScale(d)})
        .bottom(1)
        .fillStyle("rgba(0, 0, 0, 0) ")
        .interpolate("cardinal");

    /* Number of spikes label */
    psth_area.anchor("top").add(pv.Line)
        .strokeStyle("#000")
        .lineWidth(3);

        return vis;
}; 