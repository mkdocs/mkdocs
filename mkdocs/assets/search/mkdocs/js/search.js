require([
    base_url + '/mkdocs/js/mustache.min.js',
    base_url + '/mkdocs/js/lunr-0.5.7.min.js',
    'text!search-results-template.mustache',
    'text!../search_index.json',
], function (Mustache, lunr, results_template, data) {

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

    var index = lunr(function () {
        this.field('title', {boost: 10});
        this.field('text');
        this.ref('location');
    });

    data = JSON.parse(data);
    var documents = {};

    $.each(data.docs, function(i, doc){
        doc.location = base_url + doc.location;
        index.add(doc);
        documents[doc.location] = doc;
    });

    var search = function(){

        var query = $('#mkdocs-search-query').val();
        var search_results = $('#mkdocs-search-results');
        search_results.empty();

        if(query === ''){
            return;
        }

        var results = index.search(query);

        if (results.length > 0){
            $.each(results, function(i, result){
                doc = documents[result.ref];
                doc.base_url = base_url;
                doc.summary = doc.text.substring(0, 200);
                search_results.append(Mustache.to_html(results_template, doc));
            });
        } else {
            search_results.append("<p>No results found</p>");
        }

        $('#search_modal a').click(function(){
            $('#search_modal').modal('hide');
        })

    };

    var term = getSearchTerm();
    if (term){
        $('#mkdocs-search-query').val(term);
        search();
    }

    $('#mkdocs-search-query').keyup(search);

});
