SiteNavigation
==========================
from <a href="api/mkdocs">mkdocs</a>.<a href="api/mkdocs/nav">nav</a>








### Public Variable


source_files : 





### Public Method


def [walk_pages](#def-walk_pages)()







### Private Builtin


def [__init__](#def-__init__)(self, pages_config, use_directory_urls=True)



def [__iter__](#def-__iter__)(self)



def [__str__](#def-__str__)(self)







Methods
---------------







### `def __init__(self, pages_config, use_directory_urls=True)`








### `def __iter__(self)`










### `def __str__(self)`












### `def walk_pages()`




Returns each page in the site in turn.

Additionally this sets the active status of the pages and headers,
in the site navigation, so that the rendered navbar can correctly
highlight the currently active page and/or header item.


