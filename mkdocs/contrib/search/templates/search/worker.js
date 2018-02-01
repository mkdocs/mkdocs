if( 'function' === typeof importScripts ){
  importScripts('lunr.js');

  var base_url = '.';
}

var index;
var documents = {};

function onLoad () {
  var data = JSON.parse(this.responseText);
  index = lunr(function () {
    this.field('title', { boost: 10 });
    this.field('text');
    this.ref('location');

    for (var i=0; i < data.docs.length; i++) {
      var doc = data.docs[i];
      doc.location = base_url + doc.location;
      this.add(doc);
      documents[doc.location] = doc;
    }
  });
}

function init () {
  var oReq = new XMLHttpRequest();
  oReq.addEventListener("load", onLoad);
  var index_path = base_url + '/search/search_index.json';
  if( 'function' === typeof importScripts ){
      index_path = 'search_index.json';
  }
  oReq.open("GET", index_path);
  oReq.send();
}

function search (query) {
  var resultDocuments = [];
  var results = index.search(query);
  for (var i=0; i < results.length; i++){
    var result = results[i];
    doc = documents[result.ref];
    doc.base_url = base_url;
    doc.summary = doc.text.substring(0, 200);
    resultDocuments.push(doc);
  }
  return resultDocuments;
}

if( 'function' === typeof importScripts ){
  onmessage = function (e) {
    if (e.data.baseUrl) {
      base_url = e.data.baseUrl;
      init();
    } else if (e.data.query) {
      postMessage({ results: search(e.data.query) });
    } else {
      console.error("Worker - Unrecognized message: " + e);
    }
  };
}
