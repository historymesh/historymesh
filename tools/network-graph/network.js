Network = function(container, width, height) {
  this._paper = Raphael(container, width, height);
  this._nodes = {};
  this._edges = {};

  this.bgColor    = '#fff';
  this.nodeRadius = 20;
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
      'stroke-width': radius * 0.75
    });
    circle.click(this.visit, this);

    return this._circle = circle;
  },

  leadsTo: function(node) {
    return this._network.addEdge(this, node);
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
        path    = paper.path('M' + fromPos[0] + ' ' + fromPos[1] + 'L' + toPos[0] + ' ' + toPos[1]);

    path.attr({
      'stroke':       color,
      'stroke-width': width
    });
  }
});

