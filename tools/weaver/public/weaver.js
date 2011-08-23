Weaver = {
  linkFor: function(article) {
    var name = decodeURIComponent(article.name),
        type = article.type,
        href = (type === 'story' ? '/stories/' : '/wiki/') + encodeURIComponent(name);

    return '<a href="' + href + '">' + name + '</a>';
  }
};

Weaver.Saved = function(selector) {
  var storage = new Weaver.Storage();

  storage.getSavedArticles(function(articles) {
    $.each(articles, function(i, article) {
      $(selector).append('<li>' + Weaver.linkFor(article) + '</li>');
    });
  });
};

Weaver.Storage = function() {};
$.extend(Weaver.Storage.prototype, {

  saveArticle: function(article) {
    var list = this._getSaved();
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
    var articles = this._getSaved().map(function(name) {
      return JSON.parse(localStorage.getItem('article:' + name));
    });
    callback.call(context, articles);
  },

  getSavedArticle: function(name, callback, context) {
    var articleJSON = localStorage.getItem('article:' + name);
    if (!articleJSON) return callback.call(context, false);

    var articleData = JSON.parse(articleJSON),
        article = new Weaver.Article(articleData.name, articleData.type);

    article.relationships = articleData.relationships;
    article.text = articleData.text;

    callback.call(context, article);
  },

  _getSaved: function() {
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

Weaver.Article.find = function (name, callback) {
  storage.getSavedArticle(name, callback)
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
  }
});

