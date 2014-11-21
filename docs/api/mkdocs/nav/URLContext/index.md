URLContext
==========================
from <a href="api/mkdocs">mkdocs</a>.<a href="api/mkdocs/nav">nav</a>





The URLContext is used to ensure that we can generate the appropriate relative URLs to other pages from any given page in the site. We use relative URLs so that static sites can be deployed to any loc... [More...](#details)




### Public Method


def [make_relative](#def-make_relative)(url)



def [set_current_url](#def-set_current_url)(current_url)







### Private Builtin


def [__init__](#def-__init__)(self)






Details
---------------
The URLContext is used to ensure that we can generate the appropriate
relative URLs to other pages from any given page in the site.

We use relative URLs so that static sites can be deployed to any location
without having to specify what the path component on the host will be
if the documentation is not hosted at the root path.


Methods
---------------







### `def __init__(self)`












### `def make_relative(url)`




Given a URL path return it as a relative URL,
given the context of the current page.





### `def set_current_url(current_url)`





