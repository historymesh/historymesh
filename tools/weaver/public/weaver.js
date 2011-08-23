Weaver = {};

Weaver.Article = function() {
  this._storage = new Weaver.Storage();
  var self = this;

  $('a.star').live('click', function() {
    var name = $(this).attr('href').replace(/^.*\/fave\//g, '');
    self._storage.faveArticle(name);

    return false;
  });
};

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
