jQuery(function($) {

    // Check we're on a relevant page and the browser supports our navigation
    if(!$('body').hasClass('view-node') && !history.pushState) {
        return;
    }

    // Responsible for transitioning the DOM from one state to another
    var transition = (function() {
        var outInProgress = false,
            inWaiting = null;

        var goOut = function() {
            // Indicate out is in progress so that in won't try running at the
            // same time
            outInProgress = true;

            // Transition out
            $('article .textual').children().fadeOut();

            // If in has been attempted while out was still running we should
            // run in again.
            outInProgress = false;
            if(inWaiting) {
                goIn(inWaiting);
                inWaiting = null;
            }
        };

        var goIn = function(data) {
            $(document).trigger('node:transition', {slug: data.objectId});

            // Don't transition in if we're still transitioning out
            // By setting inWaiting we instruct out to call in when it finishes
            if(outInProgress) {
                inWaiting = data;
                return;
            }

            // Transition in
            var newContent = $(data.html).hide();
            $('article .textual').html('').append(newContent);
            $('article .textual').children().stop().fadeIn();
        };

        return function(targetURL, push) {
            goOut();
            load(targetURL, function(data) {
                $('title').html(data.title);
                var state = {
                    'url': targetURL
                };
                if(push) {
                    history.pushState(state, data.title, targetURL);
                }
                goIn(data);
            });
        };
    })();

    // Load function. Responsible from fetching data from either a cache or from
    // the server.
    var load = (function() {
        var loadCache = {};
        return function(targetURL, callback) {
            var jsonURL = targetURL;
            if(jsonURL.indexOf('?') > -1) {
                jsonURL = jsonURL.replace('?', 'json/?');
            } else {
                jsonURL = jsonURL + 'json/';
            }

            if(loadCache.hasOwnProperty(targetURL)) {
                callback(loadCache[targetURL]);
            } else {
                jQuery.ajax({
                    "url": jsonURL,
                    "success": function(data) {
                        loadCache[targetURL] = data;
                        callback(data);
                    }
                });
            }
        };
    }());

    // Enhance the previous and next links to transition
    $('a[rel=next], a[rel=prev]').live('click', function() {
        $(document).trigger('node:navigate', {url: $(this).attr('href')});
        return false;
    });

    $(document).bind('node:navigate', function(event, data) {
        transition(data.url, true);
    });

    // Handle history events
    window.onpopstate = function(event) {
        if(event.state) {
            transition(event.state.url, false);
        }
    };

    // Set initial state
    history.replaceState(
        {'url': window.location.href},
        window.title,
        window.location.href
    );

});

