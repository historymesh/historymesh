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
    var sequence = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65];
    var pos = 0;
    $('body').keyup(function(event) {
        if (event.keyCode == sequence[pos]) {
            pos += 1;
            if (pos == sequence.length) {
                pos = 0; // Reset
                var p = $('.story-automatons');
                if (p.length == 0) {
                    return true;
                }
                var poop = $('<span class="poop" />');
                poop.css('display', 'block');
                poop.css('position', 'absolute');
                poop.css('top', 70);
                poop.css('left', 65);
                poop.css('width', '6px');
                poop.css('height', '6px');
                poop.css('border-radius', '3px');
                poop.css('background-color', '#E03C31');
                p.append(poop);
                
                function scooper() { $(this).remove(); }
                /* Animate it to disappear approximately behind the icon below */
                poop.animate({'top': 280}, {'duration': 750, 'complete': scooper});
            }
        } else {
            post = 0;
        }
    })
    $('input').keyup(function(event) {
        // Stop keyboard events in form inputs triggering page changes
        event.stopPropagation();
        return true;
    })
});

