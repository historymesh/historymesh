var storage = new Weaver.Storage();

Weaver.Article = function(name, type) {
  this.name = name;
  this.type = type || 'unknown';
  this.relationships = {};
  this.storyLine = [];
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
      if (article.type === "story") Weaver.Article.findOrCreate(article.name, callback);
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

  addToStoryLine: function (before, after) {

    console.log("before (existing) ", before.name, "after (new) ", after.name);

    if (!this.type === 'story') throw "This isn't a story.";

    if (!this.storyLine) this.storyLine = [];

    // remove the thing we're inserting if it already exists.
    var aftLoc = this.storyLine.indexOf(after.name);
    if (aftLoc >= 0) {
      console.log('removing ' + after.name);
      console.log('pre: ' + JSON.stringify(this.storyLine));
      var a = this.storyLine.slice(0, aftLoc);
      var b = this.storyLine.slice(aftLoc + 1);

      this.storyLine = a.concat(b);
      console.log('post: ' + JSON.stringify(this.storyLine));
    }

    var insLoc;
    if (before) {
      insLoc = this.storyLine.indexOf(before.name);

      // If our "before" item doesn't exist in the storyline, insert it at the end.
      if (insLoc < 0) {
        this.storyLine.push(before.name);
        insLoc = this.storyLine.indexOf(before.name) + 1;
      }

    } else {
      insLoc = this.storyLine.length;
    }

    var a = this.storyLine.slice(0, insLoc);
    var b = this.storyLine.slice(insLoc);

    this.storyLine = a.concat(after.name).concat(b);
    this.save();
  },

});
