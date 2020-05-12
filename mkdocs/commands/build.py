import logging
import os
import gzip
from urllib.parse import urlparse

from jinja2.exceptions import TemplateNotFound
import jinja2

from mkdocs import utils
from mkdocs.structure.files import get_files
from mkdocs.structure.nav import get_navigation
import mkdocs


class DuplicateFilter:
    ''' Avoid logging duplicate messages. '''
    def __init__(self):
        self.msgs = set()

    def filter(self, record):
        rv = record.msg not in self.msgs
        self.msgs.add(record.msg)
        return rv


log = logging.getLogger(__name__)
log.addFilter(DuplicateFilter())
log.addFilter(utils.warning_filter)


def get_context(nav, files, config, page=None, base_url=''):
    """
    Return the template context for a given page or template.
    """

    if page is not None:
        base_url = utils.get_relative_url('.', page.url)

    extra_javascript = utils.create_media_urls(config['extra_javascript'], page, base_url)

    extra_css = utils.create_media_urls(config['extra_css'], page, base_url)

    return {
        'nav': nav,
        'pages': files.documentation_pages(),

        'base_url': base_url,

        'extra_css': extra_css,
        'extra_javascript': extra_javascript,

        'mkdocs_version': mkdocs.__version__,
        'build_date_utc': utils.get_build_datetime(),

        'config': config,
        'page': page,
    }


def _build_template(name, template, files, config, nav):
    """
    Return rendered output for given template as a string.
    """

    # Run `pre_template` plugin events.
    template = config['plugins'].run_event(
        'pre_template', template, template_name=name, config=config
    )

    if utils.is_error_template(name):
        # Force absolute URLs in the nav of error pages and account for the
        # possability that the docs root might be different than the server root.
        # See https://github.com/mkdocs/mkdocs/issues/77.
        # However, if site_url is not set, assume the docs root and server root
        # are the same. See https://github.com/mkdocs/mkdocs/issues/1598.
        base_url = urlparse(config['site_url'] or '/').path
    else:
        base_url = utils.get_relative_url('.', name)

    context = get_context(nav, files, config, base_url=base_url)

    # Run `template_context` plugin events.
    context = config['plugins'].run_event(
        'template_context', context, template_name=name, config=config
    )

    output = template.render(context)

    # Run `post_template` plugin events.
    output = config['plugins'].run_event(
        'post_template', output, template_name=name, config=config
    )

    return output


def _build_theme_template(template_name, env, files, config, nav):
    """ Build a template using the theme environment. """

    log.debug("Building theme template: {}".format(template_name))

    try:
        template = env.get_template(template_name)
    except TemplateNotFound:
        log.warning("Template skipped: '{}' not found in theme directories.".format(template_name))
        return

    output = _build_template(template_name, template, files, config, nav)

    if output.strip():
        output_path = os.path.join(config['site_dir'], template_name)
        utils.write_file(output.encode('utf-8'), output_path)

        if template_name == 'sitemap.xml':
            log.debug("Gzipping template: %s", template_name)
            gz_filename = '{}.gz'.format(output_path)
            with open(gz_filename, 'wb') as f:
                timestamp = utils.get_build_timestamp()
                with gzip.GzipFile(fileobj=f, filename=gz_filename, mode='wb', mtime=timestamp) as gz_buf:
                    gz_buf.write(output.encode('utf-8'))
    else:
        log.info("Template skipped: '{}' generated empty output.".format(template_name))


def _build_extra_template(template_name, files, config, nav):
    """ Build user templates which are not part of the theme. """

    log.debug("Building extra template: {}".format(template_name))

    file = files.get_file_from_path(template_name)
    if file is None:
        log.warning("Template skipped: '{}' not found in docs_dir.".format(template_name))
        return

    try:
        with open(file.abs_src_path, 'r', encoding='utf-8', errors='strict') as f:
            template = jinja2.Template(f.read())
    except Exception as e:
        log.warning("Error reading template '{}': {}".format(template_name, e))
        return

    output = _build_template(template_name, template, files, config, nav)

    if output.strip():
        utils.write_file(output.encode('utf-8'), file.abs_dest_path)
    else:
        log.info("Template skipped: '{}' generated empty output.".format(template_name))


def _populate_page(page, config, files, dirty=False):
    """ Read page content from docs_dir and render Markdown. """

    try:
        # When --dirty is used, only read the page if the file has been modified since the
        # previous build of the output.
        if dirty and not page.file.is_modified():
            return

        # Run the `pre_page` plugin event
        page = config['plugins'].run_event(
            'pre_page', page, config=config, files=files
        )

        page.read_source(config)

        # Run `page_markdown` plugin events.
        page.markdown = config['plugins'].run_event(
            'page_markdown', page.markdown, page=page, config=config, files=files
        )

        page.render(config, files)

        # Run `page_content` plugin events.
        page.content = config['plugins'].run_event(
            'page_content', page.content, page=page, config=config, files=files
        )
    except Exception as e:
        log.error("Error reading page '{}': {}".format(page.file.src_path, e))
        raise


def _build_page(page, config, files, nav, env, dirty=False):
    """ Pass a Page to theme template and write output to site_dir. """

    try:
        # When --dirty is used, only build the page if the file has been modified since the
        # previous build of the output.
        if dirty and not page.file.is_modified():
            return

        log.debug("Building page {}".format(page.file.src_path))

        # Activate page. Signals to theme that this is the current page.
        page.active = True

        context = get_context(nav, files, config, page)

        # Allow 'template:' override in md source files.
        if 'template' in page.meta:
            template = env.get_template(page.meta['template'])
        else:
            template = env.get_template('main.html')

        # Run `page_context` plugin events.
        context = config['plugins'].run_event(
            'page_context', context, page=page, config=config, nav=nav
        )

        # Render the template.
        output = template.render(context)

        # Run `post_page` plugin events.
        output = config['plugins'].run_event(
            'post_page', output, page=page, config=config
        )

        # Write the output file.
        if output.strip():
            utils.write_file(output.encode('utf-8', errors='xmlcharrefreplace'), page.file.abs_dest_path)
        else:
            log.info("Page skipped: '{}'. Generated empty output.".format(page.file.src_path))

        # Deactivate page
        page.active = False
    except Exception as e:
        log.error("Error building page '{}': {}".format(page.file.src_path, e))
        raise


def build(config, live_server=False, dirty=False):
    """ Perform a full site build. """
    from time import time
    start = time()

    # Run `config` plugin events.
    config = config['plugins'].run_event('config', config)

    # Run `pre_build` plugin events.
    config['plugins'].run_event('pre_build', config=config)

    if not dirty:
        log.info("Cleaning site directory")
        utils.clean_directory(config['site_dir'])
    else:  # pragma: no cover
        # Warn user about problems that may occur with --dirty option
        log.warning("A 'dirty' build is being performed, this will likely lead to inaccurate navigation and other"
                    " links within your site. This option is designed for site development purposes only.")

    if not live_server:  # pragma: no cover
        log.info("Building documentation to directory: %s", config['site_dir'])
        if dirty and site_directory_contains_stale_files(config['site_dir']):
            log.info("The directory contains stale files. Use --clean to remove them.")

    # First gather all data from all files/pages to ensure all data is consistent across all pages.

    files = get_files(config)
    env = config['theme'].get_env()
    files.add_files_from_theme(env, config)

    # Run `files` plugin events.
    files = config['plugins'].run_event('files', files, config=config)

    nav = get_navigation(files, config)

    # Run `nav` plugin events.
    nav = config['plugins'].run_event('nav', nav, config=config, files=files)

    log.debug("Reading markdown pages.")
    for file in files.documentation_pages():
        log.debug("Reading: " + file.src_path)
        _populate_page(file.page, config, files, dirty)

    # Run `env` plugin events.
    env = config['plugins'].run_event(
        'env', env, config=config, files=files
    )

    # Start writing files to site_dir now that all data is gathered. Note that order matters. Files
    # with lower precedence get written first so that files with higher precedence can overwrite them.

    log.debug("Copying static assets.")
    files.copy_static_files(dirty=dirty)

    for template in config['theme'].static_templates:
        _build_theme_template(template, env, files, config, nav)

    for template in config['extra_templates']:
        _build_extra_template(template, files, config, nav)

    log.debug("Building markdown pages.")
    for file in files.documentation_pages():
        _build_page(file.page, config, files, nav, env, dirty)

    # Run `post_build` plugin events.
    config['plugins'].run_event('post_build', config=config)

    if config['strict'] and utils.warning_filter.count:
        raise SystemExit('\nExited with {} warnings in strict mode.'.format(utils.warning_filter.count))

    log.info('Documentation built in %.2f seconds', time() - start)


def site_directory_contains_stale_files(site_directory):
    """ Check if the site directory contains stale files from a previous build. """

    return True if os.path.exists(site_directory) and os.listdir(site_directory) else False
