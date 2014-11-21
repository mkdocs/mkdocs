tree
=================================

from <a href="api/mkdocs">mkdocs</a>.<a href="api/mkdocs/contrib">contrib</a>.tree



The mkdocs.contrib.tree extension will allow you to load a hierarchy of markdown files into your mkdocs project. Usage Create a folder structure of *.md files somewhere in your documents root, for ins... [More...](#details)




### Public Module


[build](api/mkdocs/contrib/tree/build)



[config](api/mkdocs/contrib/tree/config)



[tree_config](api/mkdocs/contrib/tree/config)





### Public Function


def [includeme](#def-includeme)(config)






Details
------------------
The `mkdocs.contrib.tree` extension will allow you to load a hierarchy of markdown files
into your `mkdocs` project.

### Usage

Create a folder structure of `*.md` files somewhere in your documents root, for instance

    [-] ./docs/api/mkdocs
     |- index.md
     |- [+] contrib
     |- [-] utils
     |   |- index.md

To serve this hierarchy, you will need to include the `mkdocs.contrib.tree` extension in your `mkdocs.yml`
configuration file:

    mkdocs_extensions:
        - mkdocs.contrib.tree

Once that is included, you can load your folder hierarchy by including it in your `pages` configuration:

    pages:
        - ['tree:api/mkdocs', 'API', 'mkdocs']

As you can see, the syntax is `tree:<path/to/root>`.  It will load only a _single_ page to the `API` header,
named `mkdocs`, but register all the sub-pages for reference within the documentation.


Functions
------------------







### `def includeme(config)`




Intitializes the `tree` extension for mkdocs.

### Parameters
    config | <dict>





