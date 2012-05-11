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

function psth_calc(fac) {
    psth = newFilledArray(simTime, 0.);
    for (var n=0; n<times.length; n++) {
        psth[parseInt(times[n])] += fac;
    };
    return psth
};

function triangleSmoothSpike(list, kw) {
    smoothed = newFilledArray(list.length, 0.);
    for (var n=0; n<times.length; n++) {
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

function winStep(win) {
    weightStep = newFilledArray(win, 1.);
    return weightStep
}

function winTriangle(win) {
    weightTriangle = [];
    for (i=0;i<=win;i++) {
        j = i-kw+1;
        triangle = kw-Math.abs(j);
        weightTriangle.push(triangle);
    }
    return weightTriangle
}

function winGauss(win) {
    weightGauss = [];
    for (i=0;i<=win;i++) {
        j = i-kw+1;
        frac = j/win;
        gauss = 1 / Math.exp((4*(frac))*(4*(frac)));
        weightGauss.push(gauss);
    }
    return weightGauss
}

function smooth(smooth_method, fac) {
    if (smooth_method == 'gauss') {
        var win = kw*2-1;        
        weight = winGauss(win)
    } else if (smooth_method == 'triangle') {
        var win = kw*2-1;   
        weight = winTriangle(win)
    } else {
        var win = kw;   
        weight = winStep(win)
    }
    weightSum = weight.sum()
    
    first_val = newFilledArray(parseInt((win+1)/2-1), 0)
    last_val = newFilledArray(parseInt((win+1)/2), 0)
    //first_val = list.slice(0, degree)
    //last_val = list.slice(list.length-degree-1, list.length)
    psth_extented = first_val.concat(psth, last_val)
    
    smoothed = newFilledArray(psth.length, 0.)
    for (i=0; i < smoothed.length; i++) {
        psth_slice = psth_extented.slice(i, i+win)
        val = psth_slice.map(function(element,index,array){return element*weight[index]})
        smoothed[i] = fac * val.sum() / weightSum
    }
    return smoothed;
};