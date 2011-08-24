Network = function(container, width, height) {
  var el = $('#' + container);

  this._paper = Raphael(container, width, height);
  this._nodes = {};
  this._edges = {};

  this.bgColor      = '#fff';
  this.pathWidth    = 8;
  this.nodeRadius   = 0.9 * this.pathWidth;
  this.nodeStroke   = 0.5 * this.pathWidth;
  this.cornerRadius = 16;

  var self   = this,
      width  = el.width(),
      height = el.height(),
      wrap   = $('<div></div>');

  wrap.css({
    position: 'relative',
    width:    width + 'px',
    height:   height + 'px',
    overflow: 'hidden'
  });
  el.css({
    position: 'absolute',
    width:    width + 'px',
    height:   height + 'px'
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
};
$.extend(Network.prototype, {
  addNode: function(data) {
    var node = new Network.Node(this, data);
    node.id = this._nextId();
    this._nodes[node.id] = node;
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
    for (var id in this._edges) this._edges[id].draw();
    for (var id in this._nodes) this._nodes[id].draw();
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
    this._container.css({
      left: (this._offsetLeft + this._dragLeft) + 'px',
      top:  (this._offsetTop  + this._dragTop ) + 'px'
    });
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
    return this._data.position;
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
        pos    = this._data.position,
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
        pos    = data.position,
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

