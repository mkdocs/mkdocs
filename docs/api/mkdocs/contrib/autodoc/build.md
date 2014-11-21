build
=================================

from <a href="api/mkdocs">mkdocs</a>.<a href="api/mkdocs/contrib">contrib</a>.<a href="api/mkdocs/contrib/autodoc">autodoc</a>.build






### Public Function


def [create_api_content](#def-create_api_content)(event)



def [create_api_page](#def-create_api_page)(event)



def [generate_markdown](#def-generate_markdown)(event)







Functions
------------------



### `def create_api_content(event)`




Callback for the GenerateContent event.  If the page stored within the event is an ApiPage, it will
will create HTML content based on the page's object.  Otherwise, it will pass along to the base instruction.

### Parameters
    event | <mkdocs.events.BuildPage>

### Returns
    <bool> | consumed





### `def create_api_page(event)`




Processes all the auto-generated API pages for the documentation.

### Parameters
    event | <mkdocs.events.PreBuild>

### Returns
    <bool> | consumed





### `def generate_markdown(event)`






