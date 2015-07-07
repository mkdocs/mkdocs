from mkdocs.structure.pages import Page


class Navigation(object):
    def __init__(self, items, pages):
        self.items = items  # List with full navigation of Sections and Pages.
        self.pages = pages  # List of only Page instances, in order.

        if not pages:
            self.homepage = None
        else:
            self.homepage = pages[0]

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)


class Section(object):
    def __init__(self, title, children):
        self.title = title
        self.children = children

        self.parent = None

        self.is_section = True
        self.is_page = False


def get_navigation(data, files):
    items = _data_to_navigation(data)
    if not isinstance(items, list):
        items = [items]

    # Get only the pages from the navigation, ignoring any sections.
    pages = _get_pages(items)

    # Include next, previous and parent links.
    _add_previous_and_next_links(pages)
    _add_parent_links(items)

    # Validate that the 'pages' configuration matches with the
    # available documentation files.
    linked_filepaths = set([page._filepath for page in pages])
    existing_filepaths = set([file.input_path for file in files.documentation_pages()])

    missing_from_config = existing_filepaths - linked_filepaths
    missing_docs_file = linked_filepaths - existing_filepaths

    if missing_from_config:
        # TODO: This should be a properly logged warning.
        print (
            'The following pages exist in the docs directory, but are not '
            'included in the "pages" configuration:\n  - %s'
            % '\n  - '.join(sorted(list(missing_from_config)))
        )
    if missing_docs_file:
        # TODO: This should be a properly logged error.
        print (
            'The following pages are included in the "pages" configuration, '
            'but do not exist in the docs directory:\n  - %s'
            % '\n  - '.join(sorted(list(missing_docs_file)))
        )

    # Create interlinks between associated Page and File objects.
    for page in pages:
        file = files.input_paths.get(page._filepath, None)
        if file is not None:
            page.file = file
            file.page = page

    # Any documentation files not found in the nav should still
    # have an associated page. We can warn about these but still build
    # them. They won't have 'next' or 'previous' links, and will only
    # ever have default titles.
    for path in missing_from_config:
        page = Page(title=None, filepath=path)
        page.file = file
        file.page = page

    return Navigation(items, pages)


def _data_to_navigation(data):
    if isinstance(data, dict):
        return [
            Page(title=key, filepath=value)
            if isinstance(value, str) else
            Section(title=key, children=_data_to_navigation(value))
            for key, value in data.items()
        ]
    elif isinstance(data, list):
        return [
            _data_to_navigation(item)[0]
            if isinstance(item, dict) and len(item) == 1 else
            _data_to_navigation(item)
            for item in data
        ]
    return Page(title=None, filepath=str(data))


def _get_pages(nav):
    ret = []
    for item in nav:
        if isinstance(item, Page):
            ret.append(item)
        else:
            ret.extend(_get_pages(item.children))
    return ret


def _add_parent_links(nav):
    for item in nav:
        if item.is_section:
            for child in item.children:
                child.parent = item
            _add_parent_links(item.children)


def _add_previous_and_next_links(pages):
    bookended = [None] + pages + [None]
    zipped = zip(bookended[:-2], bookended[1:-1], bookended[2:])
    for page0, page1, page2 in zipped:
        page1.previous, page1.next = page0, page2


# http://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-mappings-as-ordereddicts
