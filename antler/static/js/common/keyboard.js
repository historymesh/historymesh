jQuery(function($) {
    $('body').keyup(function(event) {
        var url;
        if (event.ctrlKey || event.altKey || event.shiftKey) {
            return true;
        }
        switch(event.keyCode) {
            case 37: // left
            case 75: // k
                url = $('a[rel=prev]').attr('href');
                break;
            case 39: // right
            case 74: // j
                url = $('a[rel=next]').attr('href');
                break;
        }
        if(url) {
            window.location.href = url;
        }
    });
    $('input').keyup(function(event) {
        // Stop keyboard events in form inputs triggering page changes
        event.stopPropagation();
        return true;
    })
});

