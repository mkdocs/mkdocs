// Simple decorator shim for fetch, which makes the search_index.json file fetchable (ONLY if you enable search:local_search_shim in mkdocs.yml)
fetch_native = fetch
fetch = function(url, options){

    // Simple helper to resolve relative url (./search/search_index.json) to absolute (file://C:/Users...)
    var absolutePath = function(href) {
        var link = document.createElement("a");
        link.href = href;
        absolute = link.href;
        link.remove();
        return absolute;
    }

    // Check if this fetch call is one we need to "intercept"
    if (absolutePath(url).startsWith("file:") && absolutePath(url).endsWith("search_index.json")) {
        // If we detect that this IS a call trying to fetch the search index, then...
        console.log("LOCAL SEARCH SHIM: Detected search_index fetch attempt! Using search index shim for " + url)

        // Return a "forged" object that mimics a normal fetch call's output
        // This looks messy, but it essentially just slips in the search index wrapped in
        // all the formatting that normally results from the fetch() call
        return new Promise(
            function(resolve, reject){
              var shimResponse = {
                  json: function(){
                  // This should return the search index
                  return shim_localSearchIndex;
                }
              }
              resolve( shimResponse ) 
            }
        )
    }
    // In all other cases, behave normally
    else {
        console.log("LOCAL SEARCH SHIM: Using native fetch code for " + url)
        return fetch_native(url, options);
    }
}