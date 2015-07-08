from mkdocs.structure.files import get_files
from mkdocs.structure.nav import get_navigation
from mkdocs.structure.pages import build_pages
import yaml


pages_config = yaml.load("""
- Home: index.md
- User Guide:
    - Writing Your Docs: user-guide/writing-your-docs.md
    - Styling Your Docs: user-guide/styling-your-docs.md
    - Configuration: user-guide/configuration.md
    - Deploying Your Docs: user-guide/deploying-your-docs.md
    - Custom Themes: user-guide/custom-themes.md
- About:
    - Release Notes: about/release-notes.md
    - Contributing: about/contributing.md
    - License: about/license.md
""")


config = {
    'docs_dir': 'docs',
    'pages': pages_config
}
files = get_files(config['docs_dir'])
nav = get_navigation(config['pages'], files)
build_pages(files)
