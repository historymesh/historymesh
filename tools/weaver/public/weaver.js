Weaver = {

  linkFor: function(article) {
    if (!article.link) {
      article = new Weaver.Article(article.name, article.type);
    }
    return article.link();
  },

  Saved: function(selector) {
    storage.getSavedArticles(function(articles) {
      $.each(articles, function(i, article) {
        $(selector).append('<li>' + Weaver.linkFor(article) + '</li>');
      });
    });
  }

};
