utils
=================================

from <a href="api/mkdocs">mkdocs</a>.utils



Standalone file utils.

Nothing in this module should have an knowledge of config or the layout
and structure of the site and pages in the site.




### Public Function


def [clean_directory](#def-clean_directory)(directory)



def [copy_file](#def-copy_file)(source_path, output_path)



def [copy_media_files](#def-copy_media_files)(from_dir, to_dir)



def [create_media_urls](#def-create_media_urls)(nav, url_list)



def [get_html_path](#def-get_html_path)(path)



def [get_url_path](#def-get_url_path)(path, use_directory_urls=True)



def [is_css_file](#def-is_css_file)(path)



def [is_homepage](#def-is_homepage)(path)



def [is_html_file](#def-is_html_file)(path)



def [is_javascript_file](#def-is_javascript_file)(path)



def [is_markdown_file](#def-is_markdown_file)(path)



def [write_file](#def-write_file)(content, output_path)







Functions
------------------



### `def clean_directory(directory)`




Remove the content of a directory recursively but not the directory itself.





### `def copy_file(source_path, output_path)`




Copy source_path to output_path, making sure any parent directories exist.





### `def copy_media_files(from_dir, to_dir)`




Recursively copy all files except markdown and HTML into another directory.





### `def create_media_urls(nav, url_list)`




Return a list of URLs that have been processed correctly for inclusion in a page.





### `def get_html_path(path)`




Map a source file path to an output html path.

Paths like 'index.md' will be converted to 'index.html'
Paths like 'about.md' will be converted to 'about/index.html'
Paths like 'api-guide/core.md' will be converted to 'api-guide/core/index.html'





### `def get_url_path(path, use_directory_urls=True)`




Map a source file path to an output html path.

Paths like 'index.md' will be converted to '/'
Paths like 'about.md' will be converted to '/about/'
Paths like 'api-guide/core.md' will be converted to '/api-guide/core/'

If `use_directory_urls` is `False`, returned URLs will include the a trailing
`index.html` rather than just returning the directory path.





### `def is_css_file(path)`




Return True if the given file path is a CSS file.





### `def is_homepage(path)`








### `def is_html_file(path)`




Return True if the given file path is an HTML file.





### `def is_javascript_file(path)`




Return True if the given file path is a Javascript file.





### `def is_markdown_file(path)`




Return True if the given file path is a Markdown file.

http://superuser.com/questions/249436/file-extension-for-markdown-files





### `def write_file(content, output_path)`




Write content to output_path, making sure any parent directories exist.



