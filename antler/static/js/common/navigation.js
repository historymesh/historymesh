jQuery(function($) {

    // Check we're on a relevant page and the browser supports our navigation
    if(!$('body').hasClass('view-node') && !history.pushState) {
        return;
    }

    // Builds a state object based on a URL
    function parseURL(url) {
        var urlParts,
            matches,
            state = {},
            name;

        urlParts = window.location.pathname.replace(/(^\/|\/$)/g, "").split("/");
        state.nodeType = urlParts[0];
        state.nodeSlug = urlParts[1];
        matches = (/story=([^&]+)/).exec(window.location.search);
        if(matches) {
            state.storySlug = matches[1];
        }

        name = [
            state.storySlug,
            state.nodeType,
            state.nodeSlug
        ].join(':');

        return [state, name, url];
    }

    // Takes a URL, derives state from it and passes that to replaceState
    function replaceState(url) {
        history.replaceState.apply(history, parseURL(url));
    }

    // Takes a URL, derives state from it and passes that to pushState
    function pushState(url) {
        history.pushState.apply(history, parseURL(url));
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
            $('article').children().fadeOut();

            // If in has been attempted while out was still running we should
            // run in again.
            outInProgress = false;
            if(inWaiting) {
                goIn(inWaiting);
                inWaiting = null;
            }
        };

        var goIn = function(data) {
            // Don't transition in if we're still transitioning out
            // By setting inWaiting we instruct out to call in when it finishes
            if(outInProgress) {
                inWaiting = data;
                return;
            }

            // Transition in
            var newContent = $(data.html).hide();
            $('article').html('').append(newContent);
            $('article').children().fadeIn();
        };

        return function(targetURL) {
            goOut();
            load(targetURL, function(data) {
                pushState(targetURL);
                goIn(data);
            });
        };
    }());

    // Load function. Responsible from fetching data from either a cache or from
    // the server.
    var load = (function() {
        var loadCache = {};
        return function(targetURL, callback) {
            if(targetURL.indexOf('?') > -1) {
                targetURL = targetURL.replace('?', 'json/?');
            } else {
                targetURL = targetURL + 'json/';
            }

            if(loadCache.hasOwnProperty(targetURL)) {
                callback(loadCache[targetURL]);
            } else {
                jQuery.ajax({
                    "url": targetURL,
                    "success": function(data) {
                        loadCache[targetURL] = data;
                        callback(data);
                    }
                });
            }
        };
    }());

    // Set some initial state
    replaceState(window.location.href);

    // Enhance the previous and next links to transition
    $('a[rel=next], a[rel=prev]').live('click', function() {
        var url = $(this).attr('href');
        transition(url);
        return false;
    });

    // Handle history events
    window.onpopstate = function(event) {
        console.log("onpopstate", event.state);
        if(event.state) {
            transition(window.location.href);
        }
    };

});

