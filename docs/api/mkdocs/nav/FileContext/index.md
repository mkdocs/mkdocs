FileContext
==========================
from <a href="api/mkdocs">mkdocs</a>.<a href="api/mkdocs/nav">nav</a>





The FileContext is used to ensure that we can generate the appropriate full path for other pages given their relative path from a particular page. This is used when we have relative hyperlinks in the ... [More...](#details)




### Public Method


def [make_absolute](#def-make_absolute)(path)



def [set_current_path](#def-set_current_path)(current_path)







### Private Builtin


def [__init__](#def-__init__)(self)






Details
---------------
The FileContext is used to ensure that we can generate the appropriate
full path for other pages given their relative path from a particular page.

This is used when we have relative hyperlinks in the documentation, so that
we can ensure that they point to markdown documents that actually exist
in the `pages` config.


Methods
---------------







### `def __init__(self)`












### `def make_absolute(path)`




Given a relative file path return it as a POSIX-style
absolute filepath, given the context of the current page.





### `def set_current_path(current_path)`





