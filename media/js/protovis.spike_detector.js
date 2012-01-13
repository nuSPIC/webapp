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

Object.prototype.smooth = function () {
    var smooth = this.clone();
    for (idx in bins) {
        var nr_bins = 0;
        x = -kw;
        while (x <= kw) {
            if (parseInt(idx) + x > 0 && parseInt(idx)+x < this.length) {
                nr_bins += (kw-Math.abs(x))/kw * bins[parseInt(idx)+x].y
                };
            x++;
            };
        smooth[idx].y = nr_bins;
        } return smooth;
  };
  
function psth_calc() {

    /* Update PSTH */
    psth = newFilledArray(simTime, 0);

    for (var n = 0; n < times.length; n++) {
        psth[parseInt(times[n])] += 2/kw * 1000 / nr_spikes;
        for (var m = 1; m <= kw/2; m++) {
            if (parseInt(times[n] - m) >= 0) {
                psth[parseInt(times[n] - m)] += 2/kw * ( 1 - (2/kw) * m) * 1000 / nr_spikes;
            }
            if (parseInt(times[n] + m) < psth.length) {
                psth[parseInt(times[n] + m)] += 2/kw * ( 1 - (2/kw) * m) * 1000 / nr_spikes;
            }
        }
    };
    
    return psth
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
        .text(function () neurons[this.index]);

    /* The dot plot! */
    spikes_panel.add(pv.Dot)
        .data(times)
        .left(function(d) xScale(d))
        .top(function() yScale(senders[this.index]))
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
            var psth = psth_calc();
            psth_yScale.domain(0, pv.max(psth, function(d) d+1));
            return psth;
            })
        .bottom(10)
        .height(h2);

    
    var psth_y = psth_panel.add(pv.Rule)
        .data(psth_yScale.ticks(fig.yticks))
        .bottom(psth_yScale)
        .strokeStyle(function(d) d ? "#eee" : "#000");

    psth_y.anchor("left").add(pv.Label)
        .text(psth_yScale.tickFormat);
        
    psth_panel.add(pv.Rule)
        .data(xScale.ticks(5))
        .left(xScale)
        .strokeStyle(function(d) d ? "#eee" : "#000")
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
        .data(function() psth_panel.init())
        .left(function(d) xScale(this.index))
        .bottom(1)
        .height(function(d) psth_yScale(d))
        .fillStyle("rgba(0, 0, 0, 0) ")
        .interpolate("cardinal");

    /* Number of spikes label */
    psth_area.anchor("top").add(pv.Line)
        .strokeStyle("#000")
        .lineWidth(3);

        return vis;
//     return [vis, psth_y, psth_area];

}; 