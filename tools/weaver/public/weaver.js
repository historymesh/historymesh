Weaver = {};

Weaver.Article = function(name, type) {
  this.name = name;
  this.type = type || 'unknown';
  this.relationships = {};
};

$.extend(Weaver.Article.prototype, {
  setType: function (type) {
    this.type = type;
  },

  addRelationship: function (relatedObj, type) {
    if (!this.relationships[type]) this.relationships[type] = [];
    this.relationships[type].push(relatedObj);
  }
});

Weaver.Faves = function() {

};

Weaver.Storage = function() {};
$.extend(Weaver.Storage.prototype, {

  faveArticle: function(name) {
    var list = this._getFaveList();
    if (list.indexOf(name) < 0) list.push(name);
    localStorage.setItem('faves', list.join('||'));
  },

  getFaves: function(callback, context) {
    callback.call(context, this._getFaveList());
  },

  _getFaveList: function() {
    var faves = localStorage.getItem('faves'),
        list  = (faves === null) ? [] : faves.split('||');

    return list;
  }
});

(function() {

  var storage = new Weaver.Storage();

  $('a.star').live('click', function() {
    var name = $(this).attr('href').replace(/^.*\/fave\//g, '');
    storage.faveArticle(name);

    return false;
  });

})();

