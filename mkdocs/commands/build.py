# coding: utf-8

from __future__ import unicode_literals
from datetime import datetime
from calendar import timegm
import io
import logging
import os

from jinja2.exceptions import TemplateNotFound
import jinja2

from mkdocs import nav, search, utils
from mkdocs.utils import filters
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


def get_context(nav, config, page=None):
    """
    Given the SiteNavigation and config, generate the context which is relevant
    to app pages.
    """

    if nav is None:
        return {'page', page}

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
        'page': page,
    }


def build_template(template_name, env, config, site_navigation=None):

    log.debug("Building template: %s", template_name)

    try:
        template = env.get_template(template_name)
    except TemplateNotFound:
        return False

    context = get_context(site_navigation, config)

    output_content = template.render(context)
    output_path = os.path.join(config['site_dir'], template_name)
    utils.write_file(output_content.encode('utf-8'), output_path)
    return True


def _build_page(page, config, site_navigation, env, dirty=False):

    # Process the markdown text
    page.load_markdown()
    page.render(config, site_navigation)

    context = get_context(site_navigation, config, page)

    # Allow 'template:' override in md source files.
    if 'template' in page.meta:
        template = env.get_template(page.meta['template'])
    else:
        template = env.get_template('main.html')

    # Render the template.
    output_content = template.render(context)

    # Write the output file.
    utils.write_file(output_content.encode('utf-8'), page.abs_output_path)


def build_extra_templates(extra_templates, config, site_navigation=None):

    log.debug("Building extra_templates page")

    for extra_template in extra_templates:

        input_path = os.path.join(config['docs_dir'], extra_template)

        with io.open(input_path, 'r', encoding='utf-8') as template_file:
            template = jinja2.Template(template_file.read())

        context = get_context(site_navigation, config)

        output_content = template.render(context)
        output_path = os.path.join(config['site_dir'], extra_template)
        utils.write_file(output_content.encode('utf-8'), output_path)


def build_pages(config, dirty=False):
    """
    Builds all the pages and writes them into the build directory.
    """
    site_navigation = nav.SiteNavigation(config)
    loader = jinja2.FileSystemLoader(config['theme_dir'] + [config['mkdocs_templates'], ])
    env = jinja2.Environment(loader=loader)

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
            if dirty and (utils.modified_time(page.abs_input_path) < utils.modified_time(page.abs_output_path)):
                continue

            log.debug("Building page %s", page.input_path)
            _build_page(page, config, site_navigation, env)
            search_index.add_entry_from_context(page)
        except Exception:
            log.error("Error building page %s", page.input_path)
            raise

    search_index = search_index.generate_search_index()
    json_output_path = os.path.join(config['site_dir'], 'mkdocs', 'search_index.json')
    utils.write_file(search_index.encode('utf-8'), json_output_path)


def build(config, live_server=False, dirty=False):
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
