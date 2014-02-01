#coding: utf-8

from mkdocs import nav, toc, utils
from urlparse import urljoin
import jinja2
import markdown
import os
import re


class PathToURL(object):
    def __init__(self, config):
        self.config = config

    def __call__(self, match):
        path = match.groups()[0]
        return 'a href="%s"' % utils.path_to_url(path)


def convert_markdown(markdown_source):
    """
    Convert the Markdown source file to HTML content, and additionally
    return the parsed table of contents, and a dictionary of any metadata
    that was specified in the Markdown file.
    """

    # Prepend a table of contents marker for the TOC extension
    markdown_source = toc.pre_process(markdown_source)

    # Generate the HTML from the markdown source
    md = markdown.Markdown(extensions=['meta', 'toc'])
    html_content = md.convert(markdown_source)
    meta = md.Meta

    # Strip out the generated table of contents
    (html_content, toc_html) = toc.post_process(html_content)

    # Post process the generated table of contents into a data structure
    table_of_contents = toc.TableOfContents(toc_html)

    return (html_content, table_of_contents, meta)


def get_context(page, content, nav, toc, meta, config):
    site_name = config['site_name']

    if page.is_homepage:
        page_title = site_name
    else:
        page_title = page.title + ' - ' + site_name 

    if page.is_homepage:
        page_description = config['site_description']
    else:
        page_description = None

    if config['site_url']:
        base = config['site_url']
        if not base.endswith('/'):
            base += '/'
        canonical_url = urljoin(base, page.abs_url.lstrip('/'))
    else:
        canonical_url = None

    if config['site_favicon']:
        favicon = nav.url_context.make_relative('/' + config['site_favicon'])
    else:
        favicon = None

    return {
        'site_name': site_name,
        'site_author': config['site_author'],
        'page_title': page_title,
        'page_description': page_description,
        'favicon': favicon,

        'content': content,
        'toc': toc,
        'nav': nav,
        'meta': meta,
        'config': config,

        'base_url': nav.url_context.make_relative('/'),
        'homepage_url': nav.homepage.url,
        'canonical_url': canonical_url,

        'current_page': page,
        'previous_page': page.previous_page,
        'next_page': page.next_page,
    }


def build_pages(config):
    """
    Builds all the pages and writes them into the build directory.
    """
    site_navigation = nav.SiteNavigation(config['pages'])
    loader = jinja2.FileSystemLoader(config['theme_dir'])
    env = jinja2.Environment(loader=loader)

    for page in site_navigation.walk_pages():
        # Read the input file
        input_path = os.path.join(config['docs_dir'], page.input_path)
        input_content = open(input_path, 'r').read().decode('utf-8')

        # Process the markdown text
        html_content, table_of_contents, meta = convert_markdown(input_content)

        # Replace links ending in .md with links to the generated HTML instead
        html_content = re.sub(r'a href="([^"]*\.md)"', PathToURL(config), html_content)
        html_content = re.sub('<pre>', '<pre class="prettyprint well">', html_content)

        context = get_context(
            page, html_content, site_navigation,
            table_of_contents, meta, config
        )

        # Allow 'template:' override in md source files.
        if 'template' in meta:
            template = env.get_template(meta['template'][0])
        else:
            template = env.get_template('base.html')

        # Render the template.
        output_content = template.render(context)

        # Write the output file.
        output_path = os.path.join(config['site_dir'], page.output_path)
        utils.write_file(output_content.encode('utf-8'), output_path)


def build(config):
    """
    Perform a full site build.
    """
    utils.copy_media_files(config['theme_dir'], config['site_dir'])
    utils.copy_media_files(config['docs_dir'], config['site_dir'])
    build_pages(config)
