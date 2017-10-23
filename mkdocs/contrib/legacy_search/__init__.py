# coding: utf-8

from __future__ import absolute_import, unicode_literals

import os
import logging
from mkdocs import utils
from mkdocs.plugins import BasePlugin
from mkdocs.contrib.legacy_search.search_index import SearchIndex


log = logging.getLogger(__name__)


class SearchPlugin(BasePlugin):
    """ Add a search feature to MkDocs. """

    def on_config(self, config, **kwargs):
        "Add plugin templates and scripts to config."
        if 'include_search_page' in config['theme'] and config['theme']['include_search_page']:
            config['theme'].static_templates.add('search.html')
        if not ('search_index_only' in config['theme'] and config['theme']['search_index_only']):
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
            config['theme'].dirs.append(path)
            config['extra_javascript'].append('search/require.js')
            config['extra_javascript'].append('search/search.js')
        return config

    def on_pre_build(self, config, **kwargs):
        "Create search index instance for later use."
        self.search_index = SearchIndex()

    def on_page_context(self, context, **kwargs):
        "Add page to search index."
        self.search_index.add_entry_from_context(context['page'])

    def on_post_build(self, config, **kwargs):
        "Build search index."
        search_index = self.search_index.generate_search_index()
        json_output_path = os.path.join(config['site_dir'], 'search', 'search_index.json')
        utils.write_file(search_index.encode('utf-8'), json_output_path)
