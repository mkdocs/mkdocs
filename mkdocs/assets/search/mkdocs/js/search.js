require([
    base_url + '/mkdocs/js/mustache.min.js',
    'text!search-results-template.mustache',
    'text!../search_index.json',
], function (Mustache, results_template, data) {
   "use strict";

    function getSearchTerm()
    {
        var sPageURL = window.location.search.substring(1);
        var sURLVariables = sPageURL.split('&');
        for (var i = 0; i < sURLVariables.length; i++)
        {
            var sParameterName = sURLVariables[i].split('=');
            if (sParameterName[0] == 'q')
            {
                return decodeURIComponent(sParameterName[1].replace(/\+/g, '%20'));
            }
        }
    }

    data = JSON.parse(data);


    var search = function(){

        var query = document.getElementById('mkdocs-search-query').value;
        var search_results = document.getElementById("mkdocs-search-results");
        while (search_results.firstChild) {
            search_results.removeChild(search_results.firstChild);
        }

        if(query === ''){
            return;
        }

        var results = [];

        for (var i=0; i < data.docs.length; i++) {
            if ( !data.docs[i].location.match('#') ) {
                if ( data.docs[i].title.match(query) || data.docs[i].text.match(query) ) {
                    results.push(i);
                }
            }

        }

        if (results.length > 0){
            for (var i=0; i < results.length; i++){
                var result = results[i];
                var doc = data.docs[result];
                doc.location = base_url + doc.location;
                var match_index = doc.text.search(query);
                if (match_index == -1) { match_index = 0; }
                doc.summary = doc.text.slice(match_index, match_index + 200);
                var html = Mustache.to_html(results_template, doc);
                search_results.insertAdjacentHTML('beforeend', html);
            }
        } else {
            search_results.insertAdjacentHTML('beforeend', "<p>No results found</p>");
        }

        if(jQuery){
            /*
             * We currently only automatically hide bootstrap models. This
             * requires jQuery to work.
             */
            jQuery('#mkdocs_search_modal a').click(function(){
                jQuery('#mkdocs_search_modal').modal('hide');
            });
        }

    };

    var search_input = document.getElementById('mkdocs-search-query');

    var term = getSearchTerm();
    if (term){
        search_input.value = term;
        search();
    }

    search_input.addEventListener("keyup", search);

});
