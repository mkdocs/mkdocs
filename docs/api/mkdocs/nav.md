nav
=================================

from <a href="api/mkdocs">mkdocs</a>.nav



Deals with generating the site-wide navigation.

This consists of building a set of interlinked page and header objects.




### Public Class


[FileContext](api/mkdocs/nav/FileContext) 



[Header](api/mkdocs/nav/Header) 



[Page](api/mkdocs/nav/Page) 



[SiteNavigation](api/mkdocs/nav/SiteNavigation) 



[URLContext](api/mkdocs/nav/URLContext) 





### Public Function


def [filename_to_title](#def-filename_to_title)(filename)





### Protected Function


def [_generate_site_navigation](#def-_generate_site_navigation)(pages_config, url_context, use_directory_urls=True)







Functions
------------------













### `def _generate_site_navigation(pages_config, url_context, use_directory_urls=True)`




Returns a list of Page and Header instances that represent the
top level site navigation.





### `def filename_to_title(filename)`




Automatically generate a default title, given a filename.



