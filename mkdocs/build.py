# coding: utf-8

from mkdocs import nav, toc, utils
from urlparse import urljoin
from pprint import pprint as pp
import jinja2, markdown, os, re
import urlparse, json

os.environ['NLTK_DATA'] = os.path.expanduser("~") + '/nltk_data'
from nltk.corpus import stopwords
from nltk import PorterStemmer

badwords = stopwords.words("english")
stemmer = PorterStemmer()

class PathToURL(object):
    def __init__(self, nav=None):
        self.nav = nav

    def __call__(self, match):
        url = match.groups()[0]
        scheme, netloc, path, query, query, fragment = urlparse.urlparse(url)

        if (scheme or netloc or not utils.is_markdown_file(path)):
            # Ignore URLs unless they are a relative link to a markdown file.
            return 'a href="%s"' % url

        if self.nav:
            # If the site navigation has been provided, then validate
            # the internal hyperlink, making sure the target actually exists.
            target_file = self.nav.file_context.make_absolute(path)
            if target_file not in self.nav.source_files:
                source_file = self.nav.file_context.current_file
                msg = (
                    'The page "%s" contained a hyperlink to "%s" which '
                    'is not listed in the "pages" configuration.'
                )
                assert False, msg % (source_file, target_file)
            path = utils.get_url_path(target_file)
            path = self.nav.url_context.make_relative(path)
        else:
            path = utils.get_url_path(path).lstrip('/')

        # Convert the .md hyperlink to a relative hyperlink to the HTML page.
        url = urlparse.urlunparse((scheme, netloc, path, query, query, fragment))
        return 'a href="%s"' % url


def convert_markdown(markdown_source):
    """
    Convert the Markdown source file to HTML content, and additionally
    return the parsed table of contents, and a dictionary of any metadata
    that was specified in the Markdown file.
    """

    # Prepend a table of contents marker for the TOC extension
    markdown_source = toc.pre_process(markdown_source)

    # Generate the HTML from the markdown source
    md = markdown.Markdown(extensions=['meta', 'toc', 'tables', 'fenced_code'])
    html_content = md.convert(markdown_source)
    meta = md.Meta

    # Strip out the generated table of contents
    (html_content, toc_html) = toc.post_process(html_content)

    # Post process the generated table of contents into a data structure
    table_of_contents = toc.TableOfContents(toc_html)

    return (html_content, table_of_contents, meta)


def post_process_html(html_content, nav=None):
    html_content = re.sub(r'a href="([^"]*)"', PathToURL(nav), html_content)
    html_content = re.sub('<pre>', '<pre class="prettyprint well">', html_content)
    return html_content


def get_context(page, content, nav, toc, meta, config):
    site_name = config['site_name']

    if page.is_homepage or page.title is None:
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
        site_favicon = nav.url_context.make_relative('/' + config['site_favicon'])
    else:
        site_favicon = None

    return {
        'site_name': site_name,
        'site_author': config['site_author'],
        'site_favicon': site_favicon,

        'page_title': page_title,
        'page_description': page_description,

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

        'repo_url': config['repo_url'],
        'repo_name': config['repo_name'],

        'extra_css': config['extra_css'],
        'extra_javascript': config['extra_javascript'],

        'include_nav': config['include_nav'],
        'include_next_prev': config['include_next_prev'],
        'include_search': config['include_search'],
    }

def generate_search(config,index,env,site_nav):
    # output index file
    utils.write_file("Search.setIndex(" + json.dumps(index) + ")", os.path.join(config['site_dir'], 'searchindex.js'))

    template = env.get_template('search.html')
    base = env.get_template('base.html')
    ejs = config['extra_javascript']
    ejs.append('js/searchtools.js')
    content = base.render({
            'site_name': config['site_name'],
            'site_author': config['site_author'],
            'site_favicon': None,
            'page_title': 'Search',
            'page_description': 'Search',
            'content': template.render({}),
            'toc': None,
            'nav': site_nav,
            'meta': None,
            'config': config,
            'base_url': site_nav.url_context.make_relative('/'),
            'homepage_url': site_nav.homepage.url,
            'canonical_url': None,
            'current_page': None,
            'previous_page': None,
            'next_page': None,
            'repo_url': config['repo_url'],
            'repo_name': config['repo_name'],
            'extra_css': config['extra_css'],
            'extra_javascript': ejs,
            'include_nav': config['include_nav'],
            'include_next_prev': config['include_next_prev'],
            'include_search': config['include_search'],
        })
    utils.write_file(content, os.path.join(config['site_dir'], 'search.html'))

def generate_index(content):
    # remove html comments
    newcon = re.sub(r"<!--(.|\n|\r|\s)+?-->", "", content)
    # fix links
    newcon = re.sub(r"\([^\)]+\)", "", newcon)
    # remove any extra junk...
    newcon = re.sub(r"[^a-zA-Z0-9 \t\n]+", "", newcon)
    words = [word for word in newcon.split() if word not in badwords]
    output = set([])
    # stemmer does some weird things, so while this can cause "duplicates" it's not that bad
    for w in words:
        output.add(w)
        output.add(stemmer.stem_word(w))
    return (output,newcon)

def merge_index(index,title,url,page_index,title_index):
    cur_index = len(index['filenames'])
    index['filenames'].append(url)
    index['titles'].append(title)

    # build inverted index of page words
    for t in page_index:
        if t in index['terms']:
            if isinstance( index['terms'][t], ( int, long ) ):
                index['terms'][t] = [ index['terms'][t], cur_index ]
            elif isinstance( index['terms'][t], list ):
                index['terms'][t].append(cur_index)
            else:
                index['terms'][t] = cur_index
        else:
            index['terms'][t] = cur_index

    # same thing, but for titles
    for t in title_index:
        if t in index['titleterms']:
            if isinstance( index['titleterms'][t], ( int, long ) ):
                index['titleterms'][t] = [ index['titleterms'][t], cur_index ]
            elif isinstance( index['titleterms'][t], list ):
                index['titleterms'][t].append(cur_index)
            else:
                index['titleterms'][t] = cur_index
        else:
            index['titleterms'][t] = cur_index


def build_pages(config):
    """
    Builds all the pages and writes them into the build directory.
    """
    site_navigation = nav.SiteNavigation(config['pages'])
    loader = jinja2.FileSystemLoader(config['theme_dir'])
    env = jinja2.Environment(loader=loader)

    # mirrors sphinx so we can reuse their client side code
    index = {
        'envversion': 42,
        'terms': {},      # term => int/array of index
        'objtypes': {},
        'objnames': {},
        'filenames': [],  # pageUrl
        'titles': [],     # matching title
        'objects': {},
        'titleterms': {}  # term => int/array of index
    }
    # output =>  Searc.setIndex( ...  json dump ... )
    for page in site_navigation.walk_pages():
        if page.title is None:
            title = config['site_name']
        else:
            title = str(page.title)
        # Read the input file
        input_path = os.path.join(config['docs_dir'], page.input_path)
        input_content = open(input_path, 'r').read().decode('utf-8')

        # Process the markdown text
        title_index, source = generate_index(title)
        input_index, source = generate_index(input_content)
        html_content, table_of_contents, meta = convert_markdown(input_content)
        html_content = post_process_html(html_content, site_navigation)

        merge_index(index,title,str(page.abs_url).rstrip('/') + '/index',input_index,title_index)
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

        if config['include_search']:
            sources = os.path.join(config['site_dir'], '_sources/' + str(page.abs_url).rstrip('/') + '/index.txt')
            utils.write_file(source, sources)

    if config['include_search']:
        generate_search(config,index,env,site_navigation)


def build(config, live_server=False):
    """
    Perform a full site build.
    """
    if not live_server:
        print "Building documentation to directory: %s" % config['site_dir']
    utils.copy_media_files(config['theme_dir'], config['site_dir'])
    utils.copy_media_files(config['docs_dir'], config['site_dir'])
    build_pages(config)
