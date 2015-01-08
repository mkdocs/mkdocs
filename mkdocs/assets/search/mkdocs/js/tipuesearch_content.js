/*
 * This contains the full search index for tipuesearch. which is
 * essentially a large JSON object. See mre about the structure
 * at http://www.tipue.com/search/docs/
 */
var tipuesearch = {{ search_index }};
/*
 * To make the search index work well on all pages, re-write the
 * paths to be relative to the current page.
 */
for (var i=0; i < tipuesearch.pages.length; i++){
    tipuesearch.pages[i].loc = base_url + tipuesearch.pages[i].loc;
}
