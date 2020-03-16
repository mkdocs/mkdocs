import os
import logging
from mkdocs import utils
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from mkdocs.contrib.search.search_index import SearchIndex


log = logging.getLogger(__name__)
base_path = os.path.dirname(os.path.abspath(__file__))


class LangOption(config_options.OptionallyRequired):
    """ Validate Language(s) provided in config are known languages. """

    def lang_file_exists(self, lang):
        path = os.path.join(base_path, 'lunr-language', 'lunr.{}.js'.format(lang))
        return os.path.isfile(path)

    def run_validation(self, value):
        if isinstance(value, str):
            value = [value]
        elif not isinstance(value, (list, tuple)):
            raise config_options.ValidationError('Expected a list of language codes.')
        for lang in value:
            if lang != 'en' and not self.lang_file_exists(lang):
                raise config_options.ValidationError(
                    '"{}" is not a supported language code.'.format(lang)
                )
        return value


class SearchPlugin(BasePlugin):
    """ Add a search feature to MkDocs. """

    config_scheme = (
        ('lang', LangOption(default=['en'])),
        ('separator', config_options.Type(str, default=r'[\s\-]+')),
        ('min_search_length', config_options.Type(int, default=3)),
        ('prebuild_index', config_options.Choice((False, True, 'node', 'python'), default=False)),
    )

    def on_config(self, config, **kwargs):
        "Add plugin templates and scripts to config."
        if 'include_search_page' in config['theme'] and config['theme']['include_search_page']:
            config['theme'].static_templates.add('search.html')
        if not ('search_index_only' in config['theme'] and config['theme']['search_index_only']):
            path = os.path.join(base_path, 'templates')
            config['theme'].dirs.append(path)
            if 'search/main.js' not in config['extra_javascript']:
                config['extra_javascript'].append('search/main.js')
        return config

    def on_pre_build(self, config, **kwargs):
        "Create search index instance for later use."
        self.search_index = SearchIndex(**self.config)

    def on_page_context(self, context, **kwargs):
        "Add page to search index."
        self.search_index.add_entry_from_context(context['page'])

    def on_post_build(self, config, **kwargs):
        "Build search index."
        output_base_path = os.path.join(config['site_dir'], 'search')
        search_index = self.search_index.generate_search_index()
        json_output_path = os.path.join(output_base_path, 'search_index.json')
        utils.write_file(search_index.encode('utf-8'), json_output_path)

        if not ('search_index_only' in config['theme'] and config['theme']['search_index_only']):
            # Include language support files in output. Copy them directly
            # so that only the needed files are included.
            files = []
            if len(self.config['lang']) > 1 or 'en' not in self.config['lang']:
                files.append('lunr.stemmer.support.js')
            if len(self.config['lang']) > 1:
                files.append('lunr.multi.js')
            for lang in self.config['lang']:
                if (lang != 'en'):
                    files.append('lunr.{}.js'.format(lang))

            for filename in files:
                from_path = os.path.join(base_path, 'lunr-language', filename)
                to_path = os.path.join(output_base_path, filename)
                utils.copy_file(from_path, to_path)
