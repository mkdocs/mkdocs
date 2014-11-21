"""
Defines helper building methods for the `mkdocs.contrib.tree` extension.
"""

import os
import re
from mkdocs import nav, utils
from . import config

def create_tree(event):
    """
    Processes all the auto-generated API pages for the documentation.

    ### Parameters
        event | <mkdocs.events.PreBuild>

    ### Returns
        <bool>
    """
    # generate a set of autodoc pages
    match = re.match('^tree:(.*)$', event.path)
    if match:
        root = match.group(1)
        path = os.path.abspath(os.path.join(config.docs_dir, root))
        base = path[:-(len(root) + 1)]
        pages = []
        for base_path, folder, files in os.walk(path):
            files.sort()
            if 'index.md' in files:
                files.remove('index.md')
                files.insert(0, 'index.md')

            for file in files:
                filepath = os.path.join(base_path, file)
                filepath = filepath.replace('\\', '/')
                if file == 'index.md':
                    title = nav.filename_to_title(os.path.basename(base_path))
                else:
                    title = nav.filename_to_title(file)

                base_file_path = filepath[len(base) + 1:].replace('\\', '/')
                url = utils.get_url_path(base_file_path, True)
                page = nav.Page(title=title,
                                url=url,
                                path=base_file_path,
                                url_context=event.url_context)

                page.base_path = base_path

                # Add in previous and next information.
                if pages:
                    pages[-1].next_page = page
                    page.previous_page = pages[-1]
                pages.append(page)

        event.pages = pages
        return True
    else:
        return False
