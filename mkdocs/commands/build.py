# coding: utf-8

from __future__ import unicode_literals
from datetime import datetime
from calendar import timegm
import io
import logging
import os

from jinja2.exceptions import TemplateNotFound
import jinja2
import json

from mkdocs import nav, search, utils
from mkdocs.utils import filters
from mkdocs.relative_path_ext import RelativePathExtension
import mkdocs


class DuplicateFilter(object):
    ''' Avoid logging duplicate messages. '''
    def __init__(self):
        self.msgs = set()

    def filter(self, record):
        rv = record.msg not in self.msgs
        self.msgs.add(record.msg)
        return rv


log = logging.getLogger(__name__)
log.addFilter(DuplicateFilter())


def get_complete_paths(config, page):
    """
    Return the complete input/output paths for the supplied page.
    """
    input_path = os.path.join(config['docs_dir'], page.input_path)
    output_path = os.path.join(config['site_dir'], page.output_path)
    return input_path, output_path


def convert_markdown(markdown_source, config, site_navigation=None):
    """
    Convert the Markdown source file to HTML as per the config and
    site_navigation. Return a tuple of the HTML as a string, the parsed table
    of contents, and a dictionary of any metadata that was specified in the
    Markdown file.
    """

    extensions = [
        RelativePathExtension(site_navigation, config['strict'])
    ] + config['markdown_extensions']

    return utils.convert_markdown(
        markdown_source=markdown_source,
        extensions=extensions,
        extension_configs=config['mdx_configs']
    )


def get_global_context(nav, config):
    """
    Given the SiteNavigation and config, generate the context which is relevant
    to app pages.
    """

    extra_javascript = utils.create_media_urls(nav, config['extra_javascript'])

    extra_css = utils.create_media_urls(nav, config['extra_css'])

    # Support SOURCE_DATE_EPOCH environment variable for "reproducible" builds.
    # See https://reproducible-builds.org/specs/source-date-epoch/
    timestamp = int(os.environ.get('SOURCE_DATE_EPOCH', timegm(datetime.utcnow().utctimetuple())))

    return {
        'nav': nav,
        # base_url should never end with a slash.
        'base_url': nav.url_context.make_relative('/').rstrip('/'),

        'extra_css': extra_css,
        'extra_javascript': extra_javascript,

        'mkdocs_version': mkdocs.__version__,
        'build_date_utc': datetime.utcfromtimestamp(timestamp),

        'config': config,

        # TODO: remove the rest in 1.0 as they are deprecated
        'site_name': config['site_name'],
        'site_url': config['site_url'],
        'site_author': config['site_author'],
        'homepage_url': nav.homepage.url,
        'page_description': config['site_description'],
        'favicon': config['site_favicon'],

        'repo_url': config['repo_url'],
        'repo_name': config['repo_name'],

        'include_nav': config['include_nav'],
        'include_next_prev': config['include_next_prev'],

        'copyright': config['copyright'],
        'google_analytics': config['google_analytics']
    }


def get_page_context(page, content, toc, meta, config):
    """
    Generate the page context by extending the global context and adding page
    specific variables.
    """
    if config['site_url']:
        page.set_canonical_url(config['site_url'])

    if config['repo_url']:
        page.set_edit_url(config['repo_url'], config['edit_uri'])

    page.content = content
    page.toc = toc
    page.meta = meta

    # TODO: remove the rest in version 1.0 as they are deprecated

    if page.is_homepage or page.title is None:
        page_title = None
    else:
        page_title = page.title

    if page.is_homepage:
        page_description = config['site_description']
    else:
        page_description = None

    return {
        'page': page,
        # TODO: remove the rest in version 1.0 as they are deprecated
        'page_title': page_title,
        'page_description': page_description,

        'content': content,
        'toc': toc,
        'meta': meta,

        'canonical_url': page.canonical_url,

        'current_page': page,
        'previous_page': page.previous_page,
        'next_page': page.next_page
    }


def build_template(template_name, env, config, site_navigation=None):

    log.debug("Building template: %s", template_name)

    try:
        template = env.get_template(template_name)
    except TemplateNotFound:
        return False

    context = {'page': None}
    if site_navigation is not None:
        context.update(get_global_context(site_navigation, config))

    output_content = template.render(context)
    output_path = os.path.join(config['site_dir'], template_name)
    utils.write_file(output_content.encode('utf-8'), output_path)
    return True


def _build_page(page, config, site_navigation, env, dump_json, dirty=False):

    # Get the input/output paths
    input_path, output_path = get_complete_paths(config, page)

    # Read the input file
    try:
        input_content = io.open(input_path, 'r', encoding='utf-8').read()
    except IOError:
        log.error('file not found: %s', input_path)
        raise

    # Process the markdown text
    html_content, table_of_contents, meta = convert_markdown(
        markdown_source=input_content,
        config=config,
        site_navigation=site_navigation
    )

    context = get_global_context(site_navigation, config)
    context.update(get_page_context(
        page, html_content, table_of_contents, meta, config
    ))

    # Allow 'template:' override in md source files.
    if 'template' in meta:
        template = env.get_template(meta['template'][0])
    else:
        try:
            template = env.get_template('main.html')
        except jinja2.TemplateNotFound:
            # TODO: Remove this in version 1.0
            template = env.get_template('base.html')
            log.warn(
                "Your theme does not appear to contain a 'main.html' template. "
                "The 'base.html' template was used instead, which is deprecated. "
                "Update your theme so that the primary entry point is 'main.html'."
            )

    # Render the template.
    output_content = template.render(context)

    # Write the output file.
    if dump_json:
        json_context = {
            'content': context['content'],
            'title': context['current_page'].title,
            'url': context['current_page'].abs_url,
            'language': 'en',
        }
        json_output = json.dumps(json_context, indent=4).encode('utf-8')
        utils.write_file(json_output, output_path.replace('.html', '.json'))
    else:
        utils.write_file(output_content.encode('utf-8'), output_path)

    return html_content, table_of_contents, meta


def build_extra_templates(extra_templates, config, site_navigation=None):

    log.debug("Building extra_templates page")

    for extra_template in extra_templates:

        input_path = os.path.join(config['docs_dir'], extra_template)

        with io.open(input_path, 'r', encoding='utf-8') as template_file:
            template = jinja2.Template(template_file.read())

        context = {'page': None}
        if site_navigation is not None:
            context.update(get_global_context(site_navigation, config))

        output_content = template.render(context)
        output_path = os.path.join(config['site_dir'], extra_template)
        utils.write_file(output_content.encode('utf-8'), output_path)


def build_pages(config, dump_json=False, dirty=False):
    """
    Builds all the pages and writes them into the build directory.
    """
    site_navigation = nav.SiteNavigation(config['pages'], config['use_directory_urls'])
    loader = jinja2.FileSystemLoader(config['theme_dir'] + [config['mkdocs_templates'], ])
    env = jinja2.Environment(loader=loader)

    # TODO: remove DeprecationContext in v1.0 when all deprecated vars have been removed
    from jinja2.runtime import Context
    deprecated_vars = {
        'page_title': 'page.title',
        'content': 'page.content',
        'toc': 'page.toc',
        'meta': 'page.meta',
        'canonical_url': 'page.canonical_url',
        'previous_page': 'page.previous_page',
        'next_page': 'page.next_page',
        'current_page': 'page',
        'include_nav': 'nav|length>1',
        'include_next_prev': '(page.next_page or page.previous_page)',
        'site_name': 'config.site_name',
        'site_author': 'config.site_author',
        'page_description': 'config.site_description',
        'repo_url': 'config.repo_url',
        'repo_name': 'config.repo_name',
        'site_url': 'config.site_url',
        'copyright': 'config.copyright',
        'google_analytics': 'config.google_analytics',
        'homepage_url': 'nav.homepage.url',
        'favicon': '{{ base_url }}/img/favicon.ico',
    }

    class DeprecationContext(Context):
        def resolve(self, key):
            """ Log a warning when accessing any deprecated variable name. """
            if key in deprecated_vars:
                log.warn(
                    "Template variable warning: '{0}' is being deprecated "
                    "and will not be available in a future version. Use "
                    "'{1}' instead.".format(key, deprecated_vars[key])
                )
            return super(DeprecationContext, self).resolve(key)

    env.context_class = DeprecationContext
    # TODO: end remove DeprecationContext

    env.filters['tojson'] = filters.tojson
    search_index = search.SearchIndex()

    # Force absolute URLs in the nav of error pages and account for the
    # possability that the docs root might be different than the server root.
    # See https://github.com/mkdocs/mkdocs/issues/77
    site_navigation.url_context.force_abs_urls = True
    default_base = site_navigation.url_context.base_path
    site_navigation.url_context.base_path = utils.urlparse(config['site_url']).path
    build_template('404.html', env, config, site_navigation)
    # Reset nav behavior to the default
    site_navigation.url_context.force_abs_urls = False
    site_navigation.url_context.base_path = default_base

    if not build_template('search.html', env, config, site_navigation):
        log.debug("Search is enabled but the theme doesn't contain a "
                  "search.html file. Assuming the theme implements search "
                  "within a modal.")

    build_template('sitemap.xml', env, config, site_navigation)

    build_extra_templates(config['extra_templates'], config, site_navigation)

    for page in site_navigation.walk_pages():

        try:

            # When --dirty is used, only build the page if the markdown has been modified since the
            # previous build of the output.
            input_path, output_path = get_complete_paths(config, page)
            if dirty and (utils.modified_time(input_path) < utils.modified_time(output_path)):
                continue

            log.debug("Building page %s", page.input_path)
            build_result = _build_page(page, config, site_navigation, env,
                                       dump_json)
            html_content, table_of_contents, _ = build_result
            search_index.add_entry_from_context(
                page, html_content, table_of_contents)
        except Exception:
            log.error("Error building page %s", page.input_path)
            raise

    search_index = search_index.generate_search_index()
    json_output_path = os.path.join(config['site_dir'], 'mkdocs', 'search_index.json')
    utils.write_file(search_index.encode('utf-8'), json_output_path)


def build(config, live_server=False, dump_json=False, dirty=False):
    """
    Perform a full site build.
    """
    if not dirty:
        log.info("Cleaning site directory")
        utils.clean_directory(config['site_dir'])
    else:
        # Warn user about problems that may occur with --dirty option
        log.warning("A 'dirty' build is being performed, this will likely lead to inaccurate navigation and other"
                    " links within your site. This option is designed for site development purposes only.")

    if not live_server:
        log.info("Building documentation to directory: %s", config['site_dir'])
        if dirty and site_directory_contains_stale_files(config['site_dir']):
            log.info("The directory contains stale files. Use --clean to remove them.")

    if dump_json:
        build_pages(config, dump_json=True, dirty=dirty)
        return

    # Reversed as we want to take the media files from the builtin theme
    # and then from the custom theme_dir so that the custom versions take
    # precedence.
    for theme_dir in reversed(config['theme_dir']):
        log.debug("Copying static assets from theme: %s", theme_dir)
        utils.copy_media_files(
            theme_dir, config['site_dir'], exclude=['*.py', '*.pyc', '*.html'], dirty=dirty
        )

    log.debug("Copying static assets from the docs dir.")
    utils.copy_media_files(config['docs_dir'], config['site_dir'], dirty=dirty)

    log.debug("Building markdown pages.")
    build_pages(config, dirty=dirty)


def site_directory_contains_stale_files(site_directory):
    """
    Check if the site directory contains stale files from a previous build.
    Right now the check returns true if the directory is not empty.
    A more sophisticated approach should be found to trigger only if there are
    files that won't be overwritten anyway.
    """
    if os.path.exists(site_directory):
        if os.listdir(site_directory):
            return True
    return False
