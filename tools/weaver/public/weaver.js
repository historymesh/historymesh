Weaver = {};

Weaver.Storage = function() {};
$.extend(Weaver.Storage.prototype, {

  saveArticle: function(article) {
    var list = this._getSavedArticles();
    if (list.indexOf(article.name) < 0) list.push(article.name);

    localStorage.setItem('saved', JSON.stringify(list));
    localStorage.setItem('article:' + article.name, JSON.stringify(article));
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
    return false;
  },

});

$('a.save').live('click', function() {
  var name = $(this).attr('href').replace(/^.*\/wiki\/(.*)$/, '$1');
  var article = new Weaver.Article(name);

  return article.save();
});
