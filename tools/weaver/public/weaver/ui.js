var storage = new Weaver.Storage();

var findSaved = function () {
  storage.getSavedArticles(function(articles) {
    var names = articles.map(function(a) { return a.name });

    $('a').each(function(i, link) {
      var href = $(link).attr('href');

      if (!href) return;

      var slug = href.replace(/^.*\/wiki\/(.*)$/, '$1'),
          name = decodeURIComponent(slug);

      if (names.indexOf(name) < 0) return;

      $(link).addClass('saved')

      if ($(link).html == 'Save') {
        $(link).html('Saved!');
      }
    });
  });
};

findSaved();

var urlToArticle = function (uri) {
  var slug = uri.replace(/^.*\/wiki\/(.*)$/, '$1'),
      name = decodeURIComponent(slug),
      article = new Weaver.Article(name);

  return article;
}

$('a').each( function(link) {
});
