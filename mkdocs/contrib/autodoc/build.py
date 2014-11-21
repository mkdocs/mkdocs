import os
import re
import jinja2

from mkdocs import toc
from . import nav

def create_api_page(event):
    """
    Processes all the auto-generated API pages for the documentation.

    ### Parameters
        event | <mkdocs.events.PreBuild>

    ### Returns
        <bool> | consumed
    """
    # generate a set of autodoc pages
    match = re.match('^(.*)autodoc:([\w\.]+)$', event.path)
    if match:
        base_path, module_name = match.groups()
        page = nav.load_module(base_path, module_name, title=event.title, url_context=event.url_context)
        event.pages = [page] + page.collect_pages()
        return True
    else:
        return False

def create_api_content(event):
    """
    Callback for the GenerateContent event.  If the page stored within the event is an ApiPage, it will
    will create HTML content based on the page's object.  Otherwise, it will pass along to the base instruction.

    ### Parameters
        event | <mkdocs.events.BuildPage>

    ### Returns
        <bool> | consumed
    """
    if isinstance(event.page, nav.ApiPage):
        theme = os.path.basename(event.config['theme_dir'][0])
        theme_path = os.path.join(os.path.dirname(__file__), 'themes', theme)
        loader = jinja2.FileSystemLoader(theme_path)
        env = jinja2.Environment(loader=loader)

        template = env.get_template(event.page.template_name)

        html_content = template.render(event.page.render_context)
        html_content, toc_html = toc.post_process(html_content)

        event.html_content = html_content
        event.table_of_contents = toc.TableOfContents(toc_html)
        return True
    else:
        return False

def generate_markdown(event):
    pass
