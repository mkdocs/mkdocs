from __future__ import annotations

import json
import logging
import os
import re
import subprocess
from html.parser import HTMLParser
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mkdocs.structure.pages import Page

try:
    from lunr import lunr  # type: ignore

    haslunrpy = True
except ImportError:
    haslunrpy = False

log = logging.getLogger(__name__)
WHITESPACE_RE = re.compile(r'\s+')


class SearchIndex:
    """
    Search index is a collection of pages and sections (heading
    tags and their following content are sections).
    """

    def __init__(self, **config) -> None:
        self._entries: list[dict] = []
        self.config = config

    def _add_entry(self, title: str | None, text: str, loc: str) -> None:
        """A simple wrapper to add an entry, dropping bad characters."""
        text = text.replace('\u00a0', ' ')
        text = re.sub(r'[ \t\n\r\f\v]+', ' ', text.strip())

        self._entries.append({'title': title, 'text': text, 'location': loc})

    def add_entry_from_context(self, page: Page) -> None:
        """
        Create a set of entries in the index for a page. One for
        the page itself and then one for each of its' heading
        tags.
        """
        # Create the content parser and feed in the HTML for the
        # full page. This handles all the parsing and prepares
        # us to iterate through it.
        parser = ContentParser()
        assert page.content is not None
        parser.feed(page.content)
        parser.close()

        # Get the absolute URL for the page, this is then
        # prepended to the urls of the sections
        url = page.url

        # Create an entry for the full page.
        text = parser.stripped_html.rstrip('\n') if self.config['indexing'] == 'full' else ''
        self._add_entry(title=page.title, text=text, loc=url)

        if self.config['indexing'] in ['full', 'sections']:
            for section in parser.data:
                self.create_entry_for_section(section, url)

    def create_entry_for_section(self, section: ContentSection, abs_url: str) -> None:
        """
        Given a section of a page and the absolute url for the page
        create an entry in the index.
        """
        if section.id is not None:
            text = ' '.join(section.text) if self.config['indexing'] == 'full' else ''
            title = WHITESPACE_RE.sub(' ', section.title).strip()
            self._add_entry(title=title, text=text, loc=f'{abs_url}#{section.id}')

    def generate_search_index(self) -> str:
        """Python to json conversion."""
        page_dicts = {'docs': self._entries, 'config': self.config}
        data = json.dumps(page_dicts, sort_keys=True, separators=(',', ':'), default=str)

        if self.config['prebuild_index'] in (True, 'node'):
            try:
                script_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), 'prebuild-index.js'
                )
                p = subprocess.Popen(
                    ['node', script_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding='utf-8',
                )
                idx, err = p.communicate(data)
                if not err:
                    page_dicts['index'] = json.loads(idx)
                    data = json.dumps(page_dicts, sort_keys=True, separators=(',', ':'))
                    log.debug('Pre-built search index created successfully.')
                else:
                    log.warning(f'Failed to pre-build search index. Error: {err}')
            except (OSError, ValueError) as e:
                log.warning(f'Failed to pre-build search index. Error: {e}')
        elif self.config['prebuild_index'] == 'python':
            if haslunrpy:
                lunr_idx = lunr(
                    ref='location',
                    fields=('title', 'text'),
                    documents=self._entries,
                    languages=self.config['lang'],
                )
                page_dicts['index'] = lunr_idx.serialize()
                data = json.dumps(page_dicts, sort_keys=True, separators=(',', ':'))
            else:
                log.warning(
                    "Failed to pre-build search index. The 'python' method was specified; "
                    "however, the 'lunr.py' library does not appear to be installed. Try "
                    "installing it with 'pip install lunr'. If you are using any language "
                    "other than English you will also need to install 'lunr[languages]'."
                )

        return data


class ContentSection:
    """
    Used by the ContentParser class to capture the information we
    need when it is parsing the HTML.
    """

    def __init__(
        self,
        text: list[str] | None = None,
        id_: str | None = None,
        title: str | None = None,
    ) -> None:
        self.text = text or []
        self.id = id_
        self.title = title or ''

    def __eq__(self, other):
        return self.text == other.text and self.id == other.id and self.title == other.title

    def __repr__(self):
        return f"{type(self).__name__}(text={self.text!r}, id={self.id!r}, title={self.title!r}"


_HEADER_TAGS = tuple(f"h{x}" for x in range(1, 7))


class ContentParser(HTMLParser):
    """
    Given a block of HTML, group the content under the preceding
    heading tags which can then be used for creating an index
    for that section.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.data: list[ContentSection] = []
        self.section: ContentSection | None = None
        self.is_header_tag = False
        self.is_permalink = False
        self._stripped_html: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Called at the start of every HTML tag."""
        # Check for permalink in header
        if self.is_header_tag and tag == 'a' and len(attrs):
            atts = dict(attrs)
            if 'headerlink' in (atts.get('class') or '').split():
                self.is_permalink = True
            return

        # We only care about the opening tag for headings.
        if tag not in _HEADER_TAGS:
            return

        # We are dealing with a new header, create a new section
        # for it and assign the ID if it has one.
        atts = dict(attrs)
        self.is_header_tag = True
        self.section = ContentSection()
        self.section.id = atts.get('id')
        self.data.append(self.section)

    def handle_endtag(self, tag: str) -> None:
        """Called at the end of every HTML tag."""
        # Check for permalinks
        if self.is_permalink and tag == 'a':
            self.is_permalink = False
            return

        # We only care about the opening tag for headings.
        if tag not in _HEADER_TAGS:
            return

        self.is_header_tag = False

    def handle_data(self, data: str) -> None:
        """Called for the text contents of each tag."""
        # Do not retain permalink text.
        if self.is_permalink:
            return

        self._stripped_html.append(data)

        if self.section is None:
            # This means we have some content at the start of the
            # HTML before we reach a heading tag. We don't actually
            # care about that content as it will be added to the
            # overall page entry in the search. So just skip it.
            return

        if self.is_header_tag:
            # Write text data to title, being sure not to overwrite
            # text from previous children of heading. Text data
            # retains its whitespace and so none is added here.
            self.section.title += data
        else:
            # Write text data for elements under a heading section.
            self.section.text.append(data.rstrip('\n'))

    @property
    def stripped_html(self) -> str:
        return '\n'.join(self._stripped_html)
