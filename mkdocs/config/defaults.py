from __future__ import annotations

from mkdocs.config import base, config_options


def get_schema() -> base.PlainConfigSchema:
    return base.get_schema(_MkDocsConfig)


# NOTE: The order here is important. During validation some config options
# depend on others. So, if config option A depends on B, then A should be
# listed higher in the schema.
class _MkDocsConfig:
    config_file_path = config_options.Type(str)
    """Reserved for internal use, stores the mkdocs.yml config file."""

    site_name = config_options.Type(str, required=True)
    """The title to use for the documentation."""

    nav = config_options.Nav()
    """Defines the structure of the navigation."""
    pages = config_options.Deprecated(removed=True, moved_to='nav')

    site_url = config_options.URL(is_dir=True)
    """The full URL to where the documentation will be hosted."""

    site_description = config_options.Type(str)
    """A description for the documentation project that will be added to the
    HTML meta tags."""
    site_author = config_options.Type(str)
    """The name of the author to add to the HTML meta tags."""

    theme = config_options.Theme(default='mkdocs')
    """The MkDocs theme for the documentation."""

    docs_dir = config_options.DocsDir(default='docs', exists=True)
    """The directory containing the documentation markdown."""

    site_dir = config_options.SiteDir(default='site')
    """The directory where the site will be built to"""

    copyright = config_options.Type(str)
    """A copyright notice to add to the footer of documentation."""

    google_analytics = config_options.Deprecated(
        message=(
            'The configuration option {} has been deprecated and '
            'will be removed in a future release of MkDocs. See the '
            'options available on your theme for an alternative.'
        ),
        option_type=config_options.Type(list, length=2),
    )
    """set of values for Google analytics containing the account IO and domain
    this should look like, ['UA-27795084-5', 'mkdocs.org']"""

    dev_addr = config_options.IpAddress(default='127.0.0.1:8000')
    """The address on which to serve the live reloading docs server."""

    use_directory_urls = config_options.Type(bool, default=True)
    """If `True`, use `<page_name>/index.hmtl` style files with hyperlinks to
    the directory.If `False`, use `<page_name>.html style file with
    hyperlinks to the file.
    True generates nicer URLs, but False is useful if browsing the output on
    a filesystem."""

    repo_url = config_options.URL()
    """Specify a link to the project source repo to be included
    in the documentation pages."""

    repo_name = config_options.RepoName('repo_url')
    """A name to use for the link to the project source repo.
    Default, If repo_url is unset then None, otherwise
    "GitHub", "Bitbucket" or "GitLab" for known url or Hostname
    for unknown urls."""

    edit_uri_template = config_options.EditURITemplate('edit_uri')
    edit_uri = config_options.EditURI('repo_url')
    """Specify a URI to the docs dir in the project source repo, relative to the
    repo_url. When set, a link directly to the page in the source repo will
    be added to the generated HTML. If repo_url is not set also, this option
    is ignored."""

    extra_css = config_options.Type(list, default=[])
    extra_javascript = config_options.Type(list, default=[])
    """Specify which css or javascript files from the docs directory should be
    additionally included in the site."""

    extra_templates = config_options.Type(list, default=[])
    """Similar to the above, but each template (HTML or XML) will be build with
    Jinja2 and the global context."""

    markdown_extensions = config_options.MarkdownExtensions(
        builtins=['toc', 'tables', 'fenced_code'], configkey='mdx_configs'
    )
    """PyMarkdown extension names."""

    mdx_configs = config_options.Private()
    """PyMarkdown Extension Configs. For internal use only."""

    strict = config_options.Type(bool, default=False)
    """Enabling strict mode causes MkDocs to stop the build when a problem is
    encountered rather than display an error."""

    remote_branch = config_options.Type(str, default='gh-pages')
    """The remote branch to commit to when using gh-deploy."""

    remote_name = config_options.Type(str, default='origin')
    """The remote name to push to when using gh-deploy."""

    extra = config_options.SubConfig()
    """extra is a mapping/dictionary of data that is passed to the template.
    This allows template authors to require extra configuration that not
    relevant to all themes and doesn't need to be explicitly supported by
    MkDocs itself. A good example here would be including the current
    project version."""

    plugins = config_options.Plugins(default=['search'])
    """A list of plugins. Each item may contain a string name or a key value pair.
    A key value pair should be the string name (as the key) and a dict of config
    options (as the value)."""

    watch = config_options.ListOfPaths(default=[])
    """A list of extra paths to watch while running `mkdocs serve`."""
