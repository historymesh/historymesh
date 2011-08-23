Weaver = {};

Weaver.Storage = function() {};
$.extend(Weaver.Storage.prototype, {

  saveArticle: function(article) {
    var list = this._getSavedArticles();
    if (list.indexOf(article.name) < 0) list.push(article.name);
    localStorage.setItem('saved', JSON.stringify(list));
  },

  getSavedArticles: function(callback, context) {
    callback.call(context, this._getSavedArticles());
  },

  _getSavedArticles: function() {
    var saved = localStorage.getItem('saved'),
        list  = (saved === null) ? [] : JSON.parse(saved);

    return list;
  }
});

var storage = new Weaver.Storage();

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
  },

  save: function () {
    storage.saveArticle(this.name);
    return false;
  }
});

$('a.save').live('click', function() {
  var name = $(this).attr('href').replace(/^.*\/wiki/(.*)$/, '\1');
  var article = new Weaver.Article(name);

  return article.save();
});
