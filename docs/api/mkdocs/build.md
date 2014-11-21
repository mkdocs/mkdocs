build
=================================

from <a href="api/mkdocs">mkdocs</a>.build






### Public Class


[PathToURL](api/mkdocs/build/PathToURL) 





### Public Function


def [build](#def-build)(config, live_server=False, dump_json=False, clean_site_dir=False)



def [build_pages](#def-build_pages)(config, dump_json=False)



def [convert_markdown](#def-convert_markdown)(markdown_source, extensions=())



def [get_context](#def-get_context)(page, content, nav, toc, meta, config)



def [post_process_html](#def-post_process_html)(html_content, nav=None)



def [site_directory_contains_stale_files](#def-site_directory_contains_stale_files)(site_directory)







Functions
------------------





### `def build(config, live_server=False, dump_json=False, clean_site_dir=False)`




Perform a full site build.





### `def build_pages(config, dump_json=False)`




Builds all the pages and writes them into the build directory.





### `def convert_markdown(markdown_source, extensions=())`




Convert the Markdown source file to HTML content, and additionally
return the parsed table of contents, and a dictionary of any metadata
that was specified in the Markdown file.

`extensions` is an optional sequence of Python Markdown extensions to add
to the default set.





### `def get_context(page, content, nav, toc, meta, config)`








### `def post_process_html(html_content, nav=None)`








### `def site_directory_contains_stale_files(site_directory)`




Check if the site directory contains stale files from a previous build.
Right now the check returns true if the directory is not empty.
A more sophisticated approach should be found to trigger only if there are
files that won't be overwritten anyway.



