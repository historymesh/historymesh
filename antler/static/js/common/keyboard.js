jQuery(function($) {
    $('body').keydown(function(event) {
        var url;
        switch(event.keyCode) {
            case 37: // left
                url = $('a[rel=prev]').attr('href');
                break;
            case 39: // right
                url = $('a[rel=next]').attr('href');
                break;
        }
        if(url) {
            window.location.href = url;
        }
    });
});

