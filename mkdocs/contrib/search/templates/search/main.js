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

function displayResults (results) {
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

if (!window.Worker) {
  console.log('Web Worker API not supported');
  // load index in main thread
  $.getScript(base_url + "/search/lunr.js", function () {
    $.getScript(base_url + "/search/worker.js", function () {
      init();

      function doSearch () {
        var query = document.getElementById('mkdocs-search-query').value;
        if (query.length > 2) {
          console.log('Searching with query: ' + query);
          var results = search(query);
          displayResults(results);
        }
      }

      $(function() {
        var search_input = document.getElementById('mkdocs-search-query');
        if (search_input) {
          search_input.addEventListener("keyup", doSearch);
        }

        var term = getSearchTermFromLocation();
        if (term) {
          search_input.value = term;
          doSearch();
        }
      });
    });
  });
} else {
  // Wrap search in a web worker
  function onWorkerMessage (e) {
    if (e.data.results) {
      var results = e.data.results;
      displayResults(results);
    }
  }

  var searchWorker = new Worker(base_url + "/search/worker.js");
  searchWorker.postMessage({baseUrl: base_url});
  searchWorker.onmessage = onWorkerMessage;

  function doSearch () {
    var query = document.getElementById('mkdocs-search-query').value;
    if (query.length > 2) {
      console.log('Sending search query for: ' + query);
      searchWorker.postMessage({query: query});
    }
  }

  $(function() {
    var search_input = document.getElementById('mkdocs-search-query');
    if (search_input) {
      search_input.addEventListener("keyup", doSearch);
    }

    var term = getSearchTermFromLocation();
    if (term) {
      search_input.value = term;
      doSearch();
    }
  });
}
