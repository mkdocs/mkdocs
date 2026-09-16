var lunr = require('./templates/search/lunr'),
    stdin = process.stdin,
    stdout = process.stdout,
    buffer = [];

stdin.resume();
stdin.setEncoding('utf8');

stdin.on('data', function (data) {
  buffer.push(data);
});

stdin.on('end', function () {
  var data = JSON.parse(buffer.join('')),
      lang = ['en'];

  if (data.config) {
    if (data.config.lang && data.config.lang.length) {
      lang = data.config.lang;
      if (lang.length > 1 || lang[0] !== "en") {
        require('./lunr-language/lunr.stemmer.support')(lunr);
        if (lang.length > 1) {
          require('./lunr-language/lunr.multi')(lunr);
        }
        if (lang.includes("ja") || lang.includes("jp")) {
          require('./lunr-language/tinyseg')(lunr);
        }
        for (var i=0; i < lang.length; i++) {
          if (lang[i] != 'en') {
            require('./lunr-language/lunr.' + lang[i])(lunr);
          }
        }
      }
    }
    if (data.config.separator && data.config.separator.length) {
      lunr.tokenizer.separator = new RegExp(data.config.separator);
    }
  }

  var idx = lunr(function () {
    if (lang.length === 1 && lang[0] !== "en" && lunr[lang[0]]) {
      this.use(lunr[lang[0]]);
    } else if (lang.length > 1) {
      this.use(lunr.multiLanguage.apply(null, lang));
    }
    // Remove the stop-word filter so that common English words used as
    // programming-language keywords — "for", "if", "in", "is", "from",
    // "while", "not", etc. — are indexed and searchable.
    // See https://github.com/mkdocs/mkdocs/issues/4167
    if (lunr.stopWordFilter) {
      this.pipeline.remove(lunr.stopWordFilter);
      this.searchPipeline.remove(lunr.stopWordFilter);
    }
    this.field('title');
    this.field('text');
    this.ref('location');

    data.docs.forEach(function (doc) {
      this.add(doc);
    }, this);
  });

  stdout.write(JSON.stringify(idx));
});
