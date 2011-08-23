var storage;

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

      if ($(link).text() === 'Save') {
        $(link).html('Saved!');
      }
    });
  });
};

$(document).ready( function () {
  storage = new Weaver.Storage();
  findSaved();
} );

var urlToArticle = function (uri) {
  var slug = uri.replace(/^.*\/wiki\/(.*)$/, '$1'),
      name = decodeURIComponent(slug),
      article = new Weaver.Article(name);

  return article;
}

$('a.hovercat').live('hover', function(link) {
  var hover = $("<div class='relPanel'>");
  $(this).css('position', 'absolute');
  $(this).css('top', '-10px');
  $(this).css('left', '-10px');
});
