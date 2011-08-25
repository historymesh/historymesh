Network = function(container, width, height) {
  var el = $('#' + container);

  this._viewport = {width: width, height: height};
  this._bounding = {n: null, s: null, e: null, w: null};

  this.bgColor      = '#fff';
  this.pathWidth    = 8;
  this.nodeRadius   = 0.9 * this.pathWidth;
  this.nodeStroke   = 0.5 * this.pathWidth;
  this.cornerRadius = 16;
  this.minSize      = 50;

  this.canvasSize = 10000;

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
    width:    this.canvasSize + 'px',
    height:   this.canvasSize + 'px'
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
  this._scales = {};
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

  addEdge: function(fromNode, toNode, color, secondary) {
    var edge = new Network.Edge(this, fromNode, toNode, color, secondary);
    edge.id = this._nextId();
    this._edges[edge.id] = edge;
    return edge;
  },

  // The point x,y defines a century mark we want. We will draw a horz/vertical line as appropriate
  addCentruryMark: function(label, x, y) {
    var scale = new Network.Scale(this, label, x, y);
    scale.id = this._nextId();
    this._scales[scale.id] = scale;
    return scale;
  },

  draw: function() {
    this._paper.clear();
    this._normalize();
    this._center();
    for (var id in this._scales) this._scales[id].draw();
    for (var id in this._edges) this._edges[id].draw();
    for (var id in this._nodes) this._nodes[id].draw();
  },

  _normalize: function() {
    var box        = this._bounding,
        view       = this._viewport,
        boxWidth   = (box.e - box.w) < this.minSize ? this.minSize : (box.e - box.w),
        boxHeight  = (box.s - box.n) < this.minSize ? this.minSize : (box.s - box.n),
        viewAspect = view.width / view.height,
        boxAspect  = boxWidth / boxHeight,
        vertical   = (this.vertical === undefined) ? (boxAspect < viewAspect) : this.vertical,
        padding    = this.padding || (vertical ? (0.1 * view.width) : (0.1 * view.height)),
        factor     = vertical ? (view.width - 2*padding) / boxWidth : (view.height - 2*padding) / boxHeight,

        node,
        scale;

    this._vertical = vertical;
    this._padding  = padding;

    for (var id in this._nodes) {
      node = this._nodes[id];
      node._normal = [
        padding + factor * (node.getPosition()[0] - box.w),
        padding + factor * (node.getPosition()[1] - box.n)
      ];
    }
    for (var id in this._scales) {
      scale = this._scales[id];
      if (vertical) {
        scale._normal = [
          0,
          padding + factor * (scale.getPosition()[1] - box.n),
          this.canvasSize,
          padding + factor * (scale.getPosition()[1] - box.n)
        ];
      }
      else {
        scale._normal = [
          padding + factor * (scale.getPosition()[0] - box.w),
          0,
          padding + factor * (scale.getPosition()[0] - box.w),
          this.canvasSize
        ];
      }
    }

    this._bounding = {
      n:  padding,
      s:  padding + factor * (box.s - box.n),
      e:  padding + factor * (box.e - box.w),
      w:  padding
    };
  },

  _center: function() {
    var box       = this._bounding,
        view      = this._viewport,
        boxWidth  = box.e - box.w,
        boxHeight = box.s - box.n,
        padding   = 2 * this._padding;

    if (this._vertical)
      this._offsetTop = (view.height - boxHeight - padding) / 2;
    else
      this._offsetLeft = (view.width - boxWidth - padding) / 2;

    this._updateCSSOffset();
  },

  _updateCSSOffset: function() {
    this._container.css({left: this._offsetLeft + 'px', top: this._offsetTop + 'px'});
  },

  moveBy: function(left, top) {
    this._offsetLeft += left;
    this._offsetTop  += top;
    this._updateCSSOffset();
  },

  snapNode: function(node, x, y) {
    var pos  = node.getPosition(),
        diff = [x - pos[0], y - pos[1]];

    if (this._vertical)
      this._offsetTop = diff[1];
    else
      this._offsetLeft = diff[0];

    this._updateCSSOffset();
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
                      '<a class="node-preview" href="' +
                       this._data.url + '">' +
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
      display:    'table',
    });
    el.append(preview);

    preview.mouseover(function() { self.preview() });
    //preview.click(function() { self.visit() });

    return preview;
  },

  _renderCircle: function() {
    var paper  = this._network._paper,
        pos    = this._normal,
        radius = this._network.nodeRadius,
        color  = this._color,
        circle = paper.circle(pos[0], pos[1], radius);

    circle.attr({
      'cursor':       'pointer',
      'fill':         this._network.bgColor,
      'stroke':       color,
      'stroke-width': this._network.nodeStroke,
      'href':         this._data.url
    });
    return circle;
  },

  leadsTo: function(node, color, secondary) {
    this._color = this._color || color;
    node._color = color;
    return this._network.addEdge(this, node, color, secondary );
  },

  preview: function() {
    this._network.hidePreviews();
    this._preview.addClass('selected');
  },

  hide: function() {
    this._preview.removeClass('selected');
  },

  visit: function() {
    // alert('Something something ' + this._data.name);
    window.location.href = this._data.url;
  }
});

Network.Edge = function(network, fromNode, toNode, color, secondary) {
  this._network = network;
  this._from    = fromNode;
  this._to      = toNode;
  this._color   = color;
  this._secondary = secondary;
};
$.extend(Network.Edge.prototype, {
  draw: function() {
    if (this._path) return this._path;

    var paper   = this._network._paper,
        color   = this._color,
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

    // If the line is very close to 45 degrees, just draw it
    if (Math.abs(diffX - diffY) < 10) {
      var pathString = 'M' + fromPos[0] + ' ' + fromPos[1] +
                       'L' + toPos[0]   + ' ' + toPos[1];
    } else {
      // Otherwise, do the nice line.
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
    }

    var path = paper.path(pathString);

    path.attr({
      'stroke':       color,
      'stroke-width': this._network.pathWidth
    });

    if (this._secondary)
      path.attr('opacity', 0.4);

    return this._path = path;
  }
});

Network.Scale = function(network, label, x, y) {
  this._network = network;
  this._label = label;
  this._position = [x,y];
}
$.extend(Network.Scale.prototype, {
  getPosition: function() {
    return this._normal || this._position;
  },

  draw: function() {
    if (this._path) return this._path;

    var paper   = this._network._paper,
        color   = this._color;

    var pathString = [
      'M', this._normal[0], this._normal[1],
      'L', this._normal[2], this._normal[3]
    ].join(' ');

    var path = paper.path(pathString);

    path.attr({
      'stroke':       '#e2e2e2',
      'stroke-width': 1
    });

    // this._label = paper.text( this._normal[0] + 10, this._normal[1] - 10, this._label )
    // this._label.attr({
    //   'text-anchor': 'start',
    //   'fill': '#aaa'
    // });

    this._label = this._renderLabel();

    return this._path = path;
  },

  _renderLabel: function() {
    var div = $('<div class="century-mark">' + this._label + '</div>');

    var radius = this._network.nodeRadius,
        pos    = this._normal,
        el     = this._network._container,
        self   = this;

    div.css({
      position:   'absolute',
      left:       (pos[0] + 8) + 'px',
      top:        (pos[1] - 18 ) + 'px',
      textAlign:  'left',
      color:      '#aaa',
      fontSize:   '12px'
    });
    el.append(div);

    //preview.click(function() { self.visit() });

    return div;
  }

});