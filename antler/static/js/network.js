Network = function(container, width, height) {
  var el = $('#' + container);

  this._viewport = {width: width, height: height};
  this._bounding = {n: null, s: null, e: null, w: null};

  this.bgColor      = '#fff';
  this.pathWidth    = 8;
  this.nodeRadius   = 0.9 * this.pathWidth;
  this.nodeStroke   = 0.5 * this.pathWidth;
  this.cornerRadius = 16;

  var self   = this,
      wrap   = $('<div></div>');

  wrap.css({
    position: 'relative',
    width:    width + 'px',
    height:   height + 'px',
    overflow: 'hidden'
  });
  el.css({
    position: 'absolute',
    width:    '10000px',
    height:   '10000px'
  });
  el.before(wrap);
  wrap.append(el);

  wrap.mousedown (function(e) { self.initDrag(e) });
  wrap.mousemove (function(e) { self.moveDrag(e) });
  wrap.mouseleave(function(e) { self.endDrag(e)  });
  wrap.mouseup   (function(e) { self.endDrag(e)  });

  this._wrapper = wrap;
  this._container = el;

  this._offsetLeft = 0;
  this._offsetTop  = 0;

  this._paper = Raphael(container);
  this._nodes = {};
  this._edges = {};
};
$.extend(Network.prototype, {
  addNode: function(data) {
    var node = new Network.Node(this, data);
    node.id = this._nextId();
    this._nodes[node.id] = node;

    var box = this._bounding, pos = data.position;
    box.n = Math.min(box.n === null ?  Infinity : box.n, pos[1]);
    box.s = Math.max(box.s === null ? -Infinity : box.s, pos[1]);
    box.e = Math.max(box.e === null ? -Infinity : box.e, pos[0]);
    box.w = Math.min(box.w === null ?  Infinity : box.w, pos[0]);

    return node;
  },

  addEdge: function(fromNode, toNode) {
    var edge = new Network.Edge(this, fromNode, toNode);
    edge.id = this._nextId();
    this._edges[edge.id] = edge;
    return edge;
  },

  draw: function() {
    this._paper.clear();
    this._normalize();
    this._center();
    for (var id in this._edges) this._edges[id].draw();
    for (var id in this._nodes) this._nodes[id].draw();
  },

  _normalize: function() {
    var box        = this._bounding,
        view       = this._viewport,
        boxWidth   = box.e - box.w,
        boxHeight  = box.s - box.n,
        viewAspect = view.width / view.height,
        boxAspect  = boxWidth / boxHeight,
        vertical   = boxAspect < viewAspect,
        factor     = vertical ? view.width / boxWidth : view.height / boxHeight,
        f          = 0.8 * factor,
        padding    = vertical ? (0.1 * view.width) : (0.1 * view.height),
        node;

    this._vertical = vertical;
    this._padding  = padding;

    for (var id in this._nodes) {
      node = this._nodes[id];
      node._normal = [
        padding + f * (node.getPosition()[0] - box.w),
        padding + f * (node.getPosition()[1] - box.n)
      ];
    }
    this._bounding = {
      n:  padding,
      s:  padding + f * (box.s - box.n),
      e:  padding + f * (box.e - box.w),
      w:  padding
    };
  },

  _center: function() {
    var box       = this._bounding,
        view      = this._viewport,
        boxWidth  = box.e - box.w,
        boxHeight = box.s - box.n,
        padding   = 2 * this._padding;

    console.log(boxWidth, view.width, padding);

    if (this._vertical) {
      this._offsetTop = (view.height - boxHeight - padding) / 2;
      this._container.css({top: this._offsetTop + 'px'});
    } else {
      this._offsetLeft = (view.width - boxWidth - padding) / 2;
      this._container.css({left: this._offsetLeft + 'px'});
    }
  },

  initDrag: function(event) {
    if (this._dragStart) return;
    this._dragStart = {x: event.clientX, y: event.clientY};
  },

  moveDrag: function(event) {
    var start = this._dragStart;
    if (!start) return;

    this._dragLeft = event.clientX - start.x;
    this._dragTop  = event.clientY - start.y;

    if (this._vertical)
      this._container.css({top: (this._offsetTop  + this._dragTop ) + 'px'});
    else
      this._container.css({left: (this._offsetLeft + this._dragLeft) + 'px'});
  },

  endDrag: function() {
    if (!this._dragStart) return;
    delete this._dragStart;
    this._offsetLeft += this._dragLeft;
    this._offsetTop  += this._dragTop;
  },

  hidePreviews: function() {
    for (var id in this._nodes)
      this._nodes[id].hide();
  },

  _nextId: function() {
    this._autoinc = this._autoinc || 0;
    this._autoinc += 1;
    return this._autoinc.toString(36);
  }
});

Network.Node = function(network, data) {
  this._network = network;
  this._data    = data;
};
$.extend(Network.Node.prototype, {
  getColor: function() {
    return this._data.color;
  },

  getPosition: function() {
    return this._normal || this._data.position;
  },

  draw: function() {
    if (this._circle) return this._circle;

    this._preview = this._renderPreview();
    return this._circle = this._renderCircle();
  },

  _renderPreview: function() {
    var preview = $('<div>' +
                      '<div class="node-preview">' +
                        '<h4>' + this._data.name + '</h4>' +
                      '</div>' +
                    '</div>');

    var radius = this._network.nodeRadius,
        pos    = this._normal,
        el     = this._network._container,
        self   = this;

    preview.css({
      position:   'absolute',
      left:       (pos[0] - radius / 2) + 'px',
      top:        (pos[1] - radius / 2) + 'px',
      width:      radius + 'px',
      height:     radius + 'px',
      textAlign:  'center',
      display:    'table'
    });
    el.append(preview);

    preview.mouseover(function() { self.preview() });
    preview.click(function() { self.visit() });

    return preview;
  },

  _renderCircle: function() {
    var paper  = this._network._paper,
        data   = this._data,
        pos    = this._normal,
        radius = this._network.nodeRadius,
        color  = data.color,
        circle = paper.circle(pos[0], pos[1], radius);

    circle.attr({
      'cursor':       'pointer',
      'fill':         this._network.bgColor,
      'stroke':       color,
      'stroke-width': this._network.nodeStroke
    });
    return circle;
  },

  leadsTo: function(node) {
    return this._network.addEdge(this, node);
  },

  preview: function() {
    this._network.hidePreviews();
    this._preview.addClass('selected');
  },

  hide: function() {
    this._preview.removeClass('selected');
  },

  visit: function() {
    alert('Something something ' + this._data.name);
  }
});

Network.Edge = function(network, fromNode, toNode) {
  this._network = network;
  this._from    = fromNode;
  this._to      = toNode;
};
$.extend(Network.Edge.prototype, {
  draw: function() {
    if (this._path) return this._path;

    var paper   = this._network._paper,
        color   = this._to.getColor(),
        fromPos = this._from.getPosition(),
        toPos   = this._to.getPosition(),
        width   = this._network.nodeRadius * 0.75,

        angle   = Math.PI / 4,
        cornerR = this._network.cornerRadius,
        chop    = cornerR * Math.tan(angle / 2),
        chopX   = chop * Math.sin(angle),
        chopY   = chop * Math.cos(angle),

        vector  = {x: toPos[0] - fromPos[0], y: toPos[1] - fromPos[1]},
        diffX   = Math.abs(vector.x),
        diffY   = Math.abs(vector.y),
        signX   = (vector.x < 0) ? -1 : 1,
        signY   = (vector.y < 0) ? -1 : 1,

        corner, alpha, beta, gamma, sweep;

    if (diffX > diffY) {
      corner = [fromPos[0] + diffY * signX , toPos[1]];
      alpha  = [corner[0] - chopX * signX, corner[1] - chopY * signY];
      beta   = [corner[0] + chop * signX, corner[1]];
      sweep  = (signX === signY) ? '0' : '1';
    } else {
      corner = [toPos[0] , fromPos[1] + diffX * signY];
      alpha  = [corner[0] - chopX * signX, corner[1] - chopY * signY];
      beta   = [corner[0], corner[1] + chop * signY];
      sweep  = (signX !== signY) ? '0' : '1';
    }

    var pathString = 'M' + fromPos[0] + ' ' + fromPos[1] +
                     'L' + alpha[0]   + ' ' + alpha[1]   +
                     'A' + cornerR    + ',' + cornerR + ' 0 0,' + sweep + ' ' +
                           beta[0]    + ' ' + beta[1]    +
                     'L' + toPos[0]   + ' ' + toPos[1];

    var path = paper.path(pathString);

    path.attr({
      'stroke':       color,
      'stroke-width': this._network.pathWidth
    });

    return this._path = path;
  }
});

