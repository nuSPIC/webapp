
function prep_vis() {

    /* Root panel. */
    var vis = new pv.Panel()
        .width(w)
        .height(h1 + 20 + h2)
        .bottom(20)
        .left(30)
        .right(10)
        .top(5);

    /* Focus panel (zoomed in). */
    var focus = vis.add(pv.Panel)
        .def("init", function() {
            var d1 = x.invert(i.x),
            d2 = x.invert(i.x + i.dx),
            dd = data.slice(
                Math.max(0, pv.search.index(data, d1, function(d) d.x) - 1),
                pv.search.index(data, d2, function(d) d.x) + 1);
            fx.domain(d1, d2);
            fy.domain(scale.checked ? [pv.min(dd, function(d) d.y)-0.001, pv.max(dd, function(d) d.y)] : y.domain());
            return dd;
        })
        .top(0)
        .height(h1);

    /* X-axis ticks. */
    focus.add(pv.Rule)
        .data(function() fx.ticks())
        .left(fx)
        .strokeStyle("#eee")
    .anchor("bottom").add(pv.Label)
        .text(fx.tickFormat);

    /* Y-axis ticks. */
    focus.add(pv.Rule)
        .data(function() fy.ticks(7))
        .bottom(fy)
        .strokeStyle("#eee")
    .anchor("left").add(pv.Label)
        .text(fy.tickFormat);

    /* Focus area chart. */
    focus.add(pv.Panel)
        .overflow("hidden");

    var line = focus.add(pv.Line)
        .data(function() focus.init())
        .left(function(d) fx(d.x))
        .bottom(function(d) fy(d.y));

    var j = -1;
    var dot = line.add(pv.Dot)
        .visible(function() j >= 0)
        .data(function() [data[j]])
        .fillStyle("#ff7f0e")
        .strokeStyle("#000")
        .size(20)
        .lineWidth(1);

    dot.add(pv.Dot)
        .left(10)
        .top(0)
      .anchor("right").add(pv.Label)
        .text(function(d) d.x.toFixed(2) +"ms: "+ d.y.toFixed(2) +"mV");


    focus.add(pv.Bar)
        .fillStyle("rgba(0,0,0,.001)")
        .event("mouseout", function() {
            j = -1;
            return focus;
          })
        .event("mousemove", function() {
            var mx = fx.invert(focus.mouse().x);
            j = pv.search(data.map(function(d) d.x), mx);
            j = j < 0 ? (-j - 2) : j;
            return focus;
          });



    /* Context panel (zoomed out). */
    var context = vis.add(pv.Panel)
        .bottom(0)
        .height(h2);

    /* X-axis ticks. */
    context.add(pv.Rule)
        .data(x.ticks())
        .left(x)
        .strokeStyle("#eee")
    .anchor("bottom").add(pv.Label)
        .text(x.tickFormat);

    /* Y-axis ticks. */
    context.add(pv.Rule)
        .bottom(0);

    /* Context area chart. */
    context.add(pv.Line)
        .data(data)
        .left(function(d) x(d.x))
        .bottom(function(d) y(d.y));

    /* The selectable, draggable focus region. */
    context.add(pv.Panel)
        .data([i])
        .cursor("crosshair")
        .events("all")
        .event("mousedown", pv.Behavior.select())
        .event("select", focus)
    .add(pv.Bar)
        .left(function(d) d.x)
        .width(function(d) d.dx)
        .fillStyle("rgba(255, 128, 128, .4)")
        .cursor("move")
        .event("mousedown", pv.Behavior.drag())
        .event("drag", focus);

    return vis
}