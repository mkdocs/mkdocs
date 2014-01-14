/* Prettyify */
$( document ).ready(function() {
    prettyPrint();
});

/* Scrollspy */
var navHeight = $('.navbar').outerHeight(true) + 10

$('body').scrollspy({
  target: '.bs-sidebar',
  offset: navHeight
})

/* We need to adjust the scroll height of anchor links to adjust for the
fixed height navbar */
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

$("ul.nav a" ).click(function() {
    /*
    This deals with clicks on nav links that do not change the current
    anchor link, by forcing a 'hashchange' event to occur after the click.
    */
    var href = this.href;
    var suffix = location.hash;
    var matchesCurrentHash = (href.indexOf(suffix, href.length - suffix.length) !== -1);
    if (location.hash && matchesCurrentHash) {
        /* Force a single 'hashchange' event to occur after the click event */
        window.disableShift = true;
        location.hash='';
    };
});

/* Prevent disabled links from causing a page reload */
$("li.disabled a").click(function() {
    event.preventDefault();
});
