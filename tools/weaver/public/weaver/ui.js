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
});

var urlToArticle = function (uri) {
  var slug = uri.replace(/^.*\/wiki\/(.*)$/, '$1'),
      name = decodeURIComponent(slug),
      article = new Weaver.Article(name);

  return article;
}

$('a.relatable, section.article-text a.relatable').live('mouseenter', function() {

  var thisSlug = urlToArticle(document.location.href).name,
      thisArticle;
  Weaver.Article.findOrCreate(thisSlug, function (art) { thisArticle = art });
      // this may break if findOrCreate becomes asynchronous, but right now it's not asynchronous.

  var panelContainer = $(".panelContainer"),
      panel = $(".relPanel"),
      title = $(".relPanel .linkHeader"),
      relList = $(".relPanel .panelBody ul");

  panelContainer.hide();

  title.html('');
  title.append($(this).clone().removeClass('relatable'));

  var thatSlug = urlToArticle($(this).attr('href')).name;

  var relatedArticle;
  Weaver.Article.findOrCreate(thatSlug, function (art) { relatedArticle = art; });

  relList.html('');
  var relationships = [ 'invented', 'conceived', 'killed', 'preceded', 'befriended', 'married', 'parented', 'dined with', 'inspired', 'enabled', 'described' ];
  relationships.forEach(function (relation) {
    var relLink = $("<a class='relType'>" + relation + "</a>");

    relLink.click(function () {
      relatedArticle.addRelationship(thisArticle, relation);
    });

    var reverseRelLink = $("<a class='relType'> was " + relation + " by</a>");

    reverseRelLink.click(function () {
      thisArticle.addRelationship(relatedArticle, relation);
    });

    relList.append($("<li>").append(relLink).append(" / ").append(reverseRelLink).append(" " + thisSlug));
  });

  relList.append("<hr/>");

  Weaver.Article.findStories(function (story) {
    var fbLink = $("<a class='relType'>is followed by</a>");
    fbLink.click(function () {
      story.addToStoryLine(thisArticle, relatedArticle);
    });

    var fLink = $("<a class='relType'>follows</a>");
    fLink.click(function () {
      story.addToStoryLine(relatedArticle, thisArticle);
    });
    relList.append($("<li>").append(relatedArticle.name + " ").append(fbLink).append(" " + thisSlug + " in the " + story.name + " story."));
    relList.append($("<li>").append(relatedArticle.name + " ").append(fLink).append(" " + thisSlug + " in the " + story.name + " story."));
  });

  $(this).before(panelContainer);

  panel.mouseleave( function () {
    panelContainer.insertAfter($("header"));
    panelContainer.hide();
  });

  panelContainer.show();

});

