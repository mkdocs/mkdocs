if( 'function' === typeof importScripts ){
  importScripts('lunr.js');

  var base_url = '.';
}

var index;
var documents = {};

function onLoad () {
  var data = JSON.parse(this.responseText);
  var lang = ['en'];
  if (data.config) {
    if (data.config.lang && data.config.lang.length) {
      lang = data.config.lang;
      if (lang.length > 1 || lang[0] !== "en") {
        importScripts('lunr.stemmer.support.js');
        if (lang.length > 1) {
          importScripts('lunr.multi.js');
        }
        for (var i=0; i < lang.length; i++) {
          if (lang[i] != 'en') {
            importScripts(['lunr', lang[i], 'js'].join('.'));
          }
        }
      }
    }
    if (data.config.seperator && data.config.seperator.length) {
      lunr.tokenizer.seperator = new RegExp(data.config.seperator);
    }
  }
  index = lunr(function () {
    if (lang.length === 1 && lang[0] !== "en" && lunr[lang[0]]) {
      this.use(lunr[lang[0]])
    } else if (lang.length > 1) {
      this.use(lunr.multiLanguage(...lang))
    }
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
