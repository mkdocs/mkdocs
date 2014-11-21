"""
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
"""

from mkdocs import events

from . import build
from . import config as tree_config

def includeme(config):
    """
    Intitializes the `tree` extension for mkdocs.

    ### Parameters
        config | <dict>
    """
    tree_config.docs_dir = config.get('docs_dir', 'docs')
    events.register_callback(events.BuildPage, build.create_tree)