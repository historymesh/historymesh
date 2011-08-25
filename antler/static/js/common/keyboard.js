jQuery(function($) {
    $('body').keyup(function(event) {
        var link;
        if (event.ctrlKey || event.altKey || event.shiftKey) {
            return true;
        }
        switch(event.keyCode) {
            case 37: // left
            case 75: // k
                link = $('a[rel=prev]:first');
                break;
            case 39: // right
            case 74: // j
                link = $('a[rel=next]:first');
                break;
        }
        if(link) {
            if(history.pushState) {
                link.click();
            } else {
                window.location.href = link.attr('href');
            }
        }
    });
    $('input').keyup(function(event) {
        // Stop keyboard events in form inputs triggering page changes
        event.stopPropagation();
        return true;
    })
});

