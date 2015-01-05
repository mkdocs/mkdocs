var tipuesearch = {{ search_index }};
for (var i=0; i < tipuesearch.pages.length; i++){
    tipuesearch.pages[i].loc = base_url + tipuesearch.pages[i].loc;
}
