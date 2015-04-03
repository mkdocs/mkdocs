
/* Highlight */
$( document ).ready(function() {
    hljs.initHighlightingOnLoad();
    $('table').addClass('table table-striped table-hover');
});


/* Scrollspy */
var navHeight = $('.navbar').outerHeight(true) + 10;

$('body').scrollspy({
    target: '.bs-sidebar',
    offset: navHeight
});

/* Prevent disabled links from causing a page reload */
$("li.disabled a").click(function() {
    event.preventDefault();
});
