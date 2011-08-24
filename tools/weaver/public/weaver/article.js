var storage = new Weaver.Storage();

Weaver.Article = function(name, type) {
  this.name = name;
  this.type = type || 'unknown';
  this.relationships = {};
};

Weaver.Article.find = function (name, callback) {
  storage.getSavedArticle(name, callback)
};

Weaver.Article.findOrCreate = function (name, callback) {
  Weaver.Article.find(name, function (article) {
    if (!article) {
      article = new Weaver.Article(name);
    }

    callback(article);
  });
};

Weaver.Article.findStories = function (callback) {
  storage.getSavedArticles( function (articles) {
    $.each(articles, function (i, article) {
      if (article.type === "story") callback(article);
    });
  });
}

$.extend(Weaver.Article.prototype, {

  setType: function (type) {
    this.type = type;
  },

  addRelationship: function (relatedObj, type) {
    if (!this.relationships[type]) this.relationships[type] = [];
    this.relationships[type].push( relatedObj.name );

    Weaver.Article.findOrCreate(relatedObj.name, function (article) { article.save() });
    this.save();
  },

  save: function () {
    storage.saveArticle(this);
  },

  delete: function () {
    storage.deleteArticle(this);
  },

  link: function (relatable) {
    var name = decodeURIComponent(this.name),
        type = this.type,
        href = (type === 'story' ? '/stories/' : '/wiki/') + encodeURIComponent(name);

    if (relatable) {
      relatable = 'class="relatable"'
    }

    return '<a ' + relatable + ' href="' + href + '">' + name + '</a>';
  },

});
