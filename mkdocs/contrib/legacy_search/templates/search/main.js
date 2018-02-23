function getSearchTermFromLocation() {
  var sPageURL = window.location.search.substring(1);
  var sURLVariables = sPageURL.split('&');
  for (var i = 0; i < sURLVariables.length; i++) {
    var sParameterName = sURLVariables[i].split('=');
    if (sParameterName[0] == 'q') {
      return decodeURIComponent(sParameterName[1].replace(/\+/g, '%20'));
    }
  }
}

function formatResult (location, title, summary) {
  return '<article><h3><a href="'+ location + '">'+ title + '</a></h3><p>' + summary +'</p></article>';
}

function onWorkerMessage (e) {
  if (e.data.results) {
    var results = e.data.results;
    var search_results = document.getElementById("mkdocs-search-results");
    while (search_results.firstChild) {
      search_results.removeChild(search_results.firstChild);
    }
    if (results.length > 0){
      for (var i=0; i < results.length; i++){
        var result = results[i];
        var html = formatResult(result.location, result.title, result.summary);
        search_results.insertAdjacentHTML('beforeend', html);
      }
    } else {
        search_results.insertAdjacentHTML('beforeend', "<p>No results found</p>");
    }
  }
}

function search () {
  var query = document.getElementById('mkdocs-search-query').value;
  if (query.length > 2) {
    console.log('Sending search query for: ' + query);
    searchWorker.postMessage({query: query});
  }
}

if (!window.Worker) {
  console.error('Web Worker API not supported');
  // TODO: load legacy search.js?
} else {
  var searchWorker = new Worker("/search/worker.js");
  searchWorker.postMessage({baseUrl: base_url});
  searchWorker.onmessage = onWorkerMessage;

  $(function() {
    var search_input = document.getElementById('mkdocs-search-query');
    if (search_input) {
      search_input.addEventListener("keyup", search);
    }

    var term = getSearchTermFromLocation();
    if (term) {
      search_input.value = term;
      search();
    }
  });
}
