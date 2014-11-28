function getSearchTerm()
{
    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i++)
    {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == 'q')
        {
            return sParameterName[1];
        }
    }
}

$(document).ready(function() {

    // Tipue Search activation
    $('#tipue_search_input').tipuesearch({
        'mode': 'static',
        'show': 5
    });

    var search_term = getSearchTerm();
    if(search_term){
        $('#search_modal').modal();
    }

    // Highlight.js
    hljs.initHighlightingOnLoad();

    // Bootstrap table formatting
    $('table').addClass('table');

    // Scrollspy
    var navHeight = $('.navbar').outerHeight(true) + 10

    $('body').scrollspy({
        target: '.bs-sidebar',
        offset: navHeight
    })

    /* Prevent disabled links from causing a page reload */
    $("li.disabled a").click(function() {
        event.preventDefault();
    });


    /* Adjust the scroll height of anchors to compensate for the fixed navbar */
    window.disableShift = false;
    var shiftWindow = function() {
        if (window.disableShift) {
            window.disableShift = false;
        } else {
            /* If we're at the bottom of the page, don't erronously scroll up */
            var scrolledToBottomOfPage = (
                (window.innerHeight + window.scrollY) >= document.body.offsetHeight
            );
            if (!scrolledToBottomOfPage) {
                scrollBy(0, -60);
            };
        };
    };
    if (location.hash) {shiftWindow();}
    window.addEventListener("hashchange", shiftWindow);


    /* Deal with clicks on nav links that do not change the current anchor link. */
    $("ul.nav a" ).click(function() {
        var href = this.href;
        var suffix = location.hash;
        var matchesCurrentHash = (href.indexOf(suffix, href.length - suffix.length) !== -1);
        if (location.hash && matchesCurrentHash) {
            /* Force a single 'hashchange' event to occur after the click event */
            window.disableShift = true;
            location.hash='';
        };
    });

});
