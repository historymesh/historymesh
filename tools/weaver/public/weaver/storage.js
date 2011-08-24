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
    article.storyLine = articleData.storyLine;

    callback.call(context, article);
  },

  _getSaved: function() {
    var saved = localStorage.getItem('saved'),
        list  = (saved === null) ? [] : JSON.parse(saved);

    return list;
  }

});


