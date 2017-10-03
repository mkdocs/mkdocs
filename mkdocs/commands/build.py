# coding: utf-8

from __future__ import unicode_literals
from datetime import datetime
from calendar import timegm
import io
import logging
import os

from jinja2.exceptions import TemplateNotFound
import jinja2

from mkdocs import nav, utils
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
    """ Build a template using the theme environment. """

    log.debug("Building template: %s", template_name)

    try:
        template = env.get_template(template_name)
    except TemplateNotFound:
        log.info("Template skipped: '{}'. Not found in template directories.".format(template_name))
        return

    # Run `pre_template` plugin events.
    template = config['plugins'].run_event(
        'pre_template', template, template_name=template_name, config=config
    )

    context = get_context(site_navigation, config)

    # Run `template_context` plugin events.
    context = config['plugins'].run_event(
        'template_context', context, template_name=template_name, config=config
    )

    output_content = template.render(context)

    # Run `post_template` plugin events.
    output_content = config['plugins'].run_event(
        'post_template', output_content, template_name=template_name, config=config
    )

    if output_content.strip():
        output_path = os.path.join(config['site_dir'], template_name)
        utils.write_file(output_content.encode('utf-8'), output_path)
    else:
        log.info("Template skipped: '{}'. Generated empty output.".format(template_name))


def build_error_template(template, env, config, site_navigation):
    """
    Build error template.

    Force absolute URLs in the nav of error pages and account for the
    possability that the docs root might be different than the server root.
    See https://github.com/mkdocs/mkdocs/issues/77
    """

    site_navigation.url_context.force_abs_urls = True
    default_base = site_navigation.url_context.base_path
    site_navigation.url_context.base_path = utils.urlparse(config['site_url']).path

    build_template(template, env, config, site_navigation)

    # Reset nav behavior to the default
    site_navigation.url_context.force_abs_urls = False
    site_navigation.url_context.base_path = default_base


def _build_page(page, config, site_navigation, env, dirty=False):
    """ Build a Markdown page and pass to theme template. """

    # Run the `pre_page` plugin event
    page = config['plugins'].run_event(
        'pre_page', page, config=config, site_navigation=site_navigation
    )

    page.read_source(config=config)

    # Run `page_markdown` plugin events.
    page.markdown = config['plugins'].run_event(
        'page_markdown', page.markdown, page=page, config=config, site_navigation=site_navigation
    )

    page.render(config, site_navigation)

    # Run `page_content` plugin events.
    page.content = config['plugins'].run_event(
        'page_content', page.content, page=page, config=config, site_navigation=site_navigation
    )

    context = get_context(site_navigation, config, page)

    # Allow 'template:' override in md source files.
    if 'template' in page.meta:
        template = env.get_template(page.meta['template'])
    else:
        template = env.get_template('main.html')

    # Run `page_context` plugin events.
    context = config['plugins'].run_event(
        'page_context', context, page=page, config=config, site_navigation=site_navigation
    )

    # Render the template.
    output_content = template.render(context)

    # Run `post_page` plugin events.
    output_content = config['plugins'].run_event(
        'post_page', output_content, page=page, config=config
    )

    # Write the output file.
    if output_content.strip():
        utils.write_file(output_content.encode('utf-8'), page.abs_output_path)
    else:
        log.info("Page skipped: '{}'. Generated empty output.".format(page.title))


def build_extra_templates(extra_templates, config, site_navigation=None):
    """ Build user templates which are not part of the theme. """

    log.debug("Building extra_templates pages")

    for extra_template in extra_templates:

        input_path = os.path.join(config['docs_dir'], extra_template)

        with io.open(input_path, 'r', encoding='utf-8') as template_file:
            template = jinja2.Template(template_file.read())

        # Run `pre_template` plugin events.
        template = config['plugins'].run_event(
            'pre_template', template, template_name=extra_template, config=config
        )

        context = get_context(site_navigation, config)

        # Run `template_context` plugin events.
        context = config['plugins'].run_event(
            'template_context', context, template_name=extra_template, config=config
        )

        output_content = template.render(context)

        # Run `post_template` plugin events.
        output_content = config['plugins'].run_event(
            'post_template', output_content, template_name=extra_template, config=config
        )

        if output_content.strip():
            output_path = os.path.join(config['site_dir'], extra_template)
            utils.write_file(output_content.encode('utf-8'), output_path)
        else:
            log.info("Template skipped: '{}'. Generated empty output.".format(extra_template))


def build_pages(config, dirty=False):
    """ Build all pages and write them into the build directory. """

    site_navigation = nav.SiteNavigation(config)

    # Run `nav` plugin events.
    site_navigation = config['plugins'].run_event('nav', site_navigation, config=config)

    env = config['theme'].get_env()

    # Run `env` plugin events.
    env = config['plugins'].run_event(
        'env', env, config=config, site_navigation=site_navigation
    )

    for template in config['theme'].static_templates:
        if utils.is_error_template(template):
            build_error_template(template, env, config, site_navigation)
        else:
            build_template(template, env, config, site_navigation)

    build_extra_templates(config['extra_templates'], config, site_navigation)

    log.debug("Building markdown pages.")
    for page in site_navigation.walk_pages():
        try:
            # When --dirty is used, only build the page if the markdown has been modified since the
            # previous build of the output.
            if dirty and (utils.modified_time(page.abs_input_path) < utils.modified_time(page.abs_output_path)):
                continue

            log.debug("Building page %s", page.input_path)
            _build_page(page, config, site_navigation, env)
        except Exception:
            log.error("Error building page %s", page.input_path)
            raise


def build(config, live_server=False, dirty=False):
    """ Perform a full site build. """

    # Run `config` plugin events.
    config = config['plugins'].run_event('config', config)

    # Run `pre_build` plugin events.
    config['plugins'].run_event('pre_build', config)

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
    for theme_dir in reversed(config['theme'].dirs):
        log.debug("Copying static assets from %s", theme_dir)
        utils.copy_media_files(
            theme_dir, config['site_dir'], exclude=['*.py', '*.pyc', '*.html', 'mkdocs_theme.yml'], dirty=dirty
        )

    log.debug("Copying static assets from the docs dir.")
    utils.copy_media_files(config['docs_dir'], config['site_dir'], dirty=dirty)

    build_pages(config, dirty=dirty)

    # Run `post_build` plugin events.
    config['plugins'].run_event('post_build', config)


def site_directory_contains_stale_files(site_directory):
    """ Check if the site directory contains stale files from a previous build. """

    return True if os.path.exists(site_directory) and os.listdir(site_directory) else False
