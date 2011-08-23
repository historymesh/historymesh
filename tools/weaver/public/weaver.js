Weaver = {};

Weaver.Storage = function() {};
$.extend(Weaver.Storage.prototype, {

  saveArticle: function(article) {
    var list = this._getSavedArticles();
    if (list.indexOf(article.name) < 0) list.push(article.name);

    localStorage.setItem('saved', JSON.stringify(list));
    localStorage.setItem('article:' + article.name, JSON.stringify(article));
  },

  deleteArticle: function (article) {
    var list = this._getSavedArticles();

    var loc = list.indexOf(article.name);

    if (loc >= 0) {
      list = list.slice(0, loc).concat(list.slice(loc + 1, list.length));
      localStorage.setItem('saved', JSON.stringify(list));
    }

    localStorage.removeItem('article:' + article.name);
  },

  getSavedArticles: function(callback, context) {
    callback.call(context, this._getSavedArticles());
  },

  getSavedArticle: function(name, callback) {
    var articleData = JSON.parse(localStorage.getItem('article:' + name));
    
    var article = new Weaver.Article(articleData.name, articleData.type);
    callback.call(article);
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

  this.find = function (name) {
  };
};

$.extend(Weaver.Article.prototype, {

  setType: function (type) {
    this.type = type;
  },

  addRelationship: function (relatedObj, type) {
    if (!this.relationships[type]) this.relationships[type] = [];
    this.relationships[type].push( relatedObj.name );
    this.save();
  },

  save: function () {
    storage.saveArticle(this);
  },

  delete: function () {
    storage.deleteArticle(this);
  },

});

$('a.save').live('click', function() {
  var name = $(this).attr('href').replace(/^.*\/wiki\/(.*)$/, '$1');
  var article = new Weaver.Article(name);

  article.save();

  return false;
});
