# Developing Themes

A guide to creating and distributing custom themes.

---

!!! Note

    If you are looking for existing third party themes, they are listed in the
    MkDocs [community wiki]. If you want to share a theme you create, you
    should list it on the Wiki.

When creating a new theme, you can either follow the steps in this guide to
create one from scratch or you can download the `mkdocs-basic-theme` as a
basic, yet complete, theme with all the boilerplate required. **You can find
this base theme on [GitHub][basic theme]**. It contains detailed comments in
the code to describe the different features and their usage.

[community wiki]: https://github.com/mkdocs/mkdocs/wiki/MkDocs-Themes
[basic theme]: https://github.com/mkdocs/mkdocs-basic-theme

## Creating a custom theme

The bare minimum required for a custom theme is a `main.html` [Jinja2
template] file which is placed in a directory that is *not* a child of the
[docs_dir]. Within `mkdocs.yml`, set the [`theme.custom_dir`][custom_dir]
option to the path of the directory containing `main.html`. The path should be
relative to the configuration file. For example, given this example project
layout:

```no-highlight
mkdocs.yml
docs/
    index.md
    about.md
custom_theme/
    main.html
    ...
```

... you would include the following settings in `mkdocs.yml` to use the custom theme
directory:

```yaml
theme:
    name: null
    custom_dir: 'custom_theme/'
```

!!! Note

    Generally, when building your own custom theme, the theme.[name]
    configuration setting would be set to `null`. However, if the
    theme.[custom_dir] configuration value is used in combination with an
    existing theme, the theme.[custom_dir] can be used to replace only specific
    parts of a built-in theme. For example, with the above layout and if you set
    `name: "mkdocs"` then the `main.html` file in the theme.[custom_dir] would
    replace the file of the same name in the `mkdocs` theme but otherwise the
    `mkdocs` theme would remain unchanged. This is useful if you want to make
    small adjustments to an existing theme.

    For more specific information, see [Customizing Your Theme].

!!! Warning

    A theme's [configuration] defined in a `mkdocs_theme.yml` file is not loaded
    from `theme.custom_dir`. When an entire theme exists in `theme.custom_dir`
    and `theme.name` is set to `null`, then the entire theme configuration must
    be defined in the [theme] configuration option in the `mkdocs.yml` file.

    However, when a theme is [packaged] up for distribution, and loaded using
    the `theme.name` configuration option, then a `mkdocs_theme.yml` file
    is required for the theme.

[Customizing Your Theme]: ../user-guide/customizing-your-theme.md#using-the-theme-custom_dir
[custom_dir]: ../user-guide/configuration.md#custom_dir
[name]: ../user-guide/configuration.md#name
[docs_dir]: ../user-guide/configuration.md#docs_dir
[configuration]: #theme-configuration
[packaged]: #packaging-themes
[theme]: ../user-guide/configuration.md#theme

## Basic theme

The simplest `main.html` file is the following:

```django
<!DOCTYPE html>
<html>
  <head>
    <title>{% if page.title %}{{ page.title }} - {% endif %}{{ config.site_name }}</title>
  </head>
  <body>
    {{ page.content }}
  </body>
</html>
```

The body content from each page specified in `mkdocs.yml` is inserted using the
`{{ page.content }}` tag. Style-sheets and scripts can be brought into this
theme as with a normal HTML file. Navbars and tables of contents can also be
generated and included automatically, through the `nav` and `toc` objects,
respectively. If you wish to write your own theme, it is recommended to start
with one of the [built-in themes] and modify it accordingly.

!!! Note

    As MkDocs uses [Jinja] as its template engine, you have access to all the
    power of Jinja, including [template inheritance]. You may notice that the
    themes included with MkDocs make extensive use of template inheritance and
    blocks, allowing users to easily override small bits and pieces of the
    templates from the theme [custom_dir]. Therefore, the built-in themes are
    implemented in a `base.html` file, which `main.html` extends. Although not
    required, third party template authors are encouraged to follow a similar
    pattern and may want to define the same [blocks] as are used in the built-in
    themes for consistency.

[Jinja]: http://jinja.pocoo.org/
[template inheritance]: http://jinja.pocoo.org/docs/dev/templates/#template-inheritance
[theme_dir]: ../user-guide/customizing-your-theme.md#using-the-theme_dir
[blocks]: ../user-guide/customizing-your-theme.md#overriding-template-blocks

## Theme Files

There are various files which a theme treats special in some way. Any other
files are simply copied from the theme directory to the same path in the
`site_dir` when the site it built. For example image and CSS files have no
special significance and are copied as-is. Note, however, that if the user
provides a file with the same path in their `docs_dir`, then the user's file
will replace the theme file.

### Template Files

Any files with the `.html` extension are considered to be template files and are
not copied from the theme directory or any subdirectories. Also, any files
listed in [static_templates] are treated as templates regardless of their file
extension.

[static_templates]: #static_templates

### Theme Meta Files

The various files required for packaging a theme are also ignored. Specifically,
the `mkdocs_theme.yml` configuration file and any Python files.

### Dot Files

Theme authors can explicitly force MkDocs to ignore files by starting a file or
directory name with a dot. Any of the following files would be ignored:

```text
.ignored.txt
.ignored/file.txt
foo/.ignored.txt
foo/.ignored/file.txt
```

### Documentation Files

All documentation files are ignored. Specifically, any Markdown files (using any
of the file extensions supported by MKDocs). Additionally, any README files
which may exist in the theme directories are ignored.

## Template Variables

Each template in a theme is built with a template context. These are the
variables that are available to themes. The context varies depending on the
template that is being built. At the moment templates are either built with
the global context or with a page specific context. The global context is used
for HTML pages that don't represent an individual Markdown document, for
example a 404.html page or search.html.

### Global Context

The following variables are available globally on any template.

#### config

The `config` variable is an instance of MkDocs' config object generated from the
`mkdocs.yml` config file. While you can use any config option, some commonly
used options include:

* [config.site_name](../user-guide/configuration.md#site_name)
* [config.site_url](../user-guide/configuration.md#site_url)
* [config.site_author](../user-guide/configuration.md#site_author)
* [config.site_description](../user-guide/configuration.md#site_description)
* [config.theme.locale](../user-guide/configuration.md#locale) (See also
  [Theme Configuration](#locale) below)
* [config.extra_javascript](../user-guide/configuration.md#extra_javascript)
* [config.extra_css](../user-guide/configuration.md#extra_css)
* [config.repo_url](../user-guide/configuration.md#repo_url)
* [config.repo_name](../user-guide/configuration.md#repo_name)
* [config.copyright](../user-guide/configuration.md#copyright)
* [config.google_analytics](../user-guide/configuration.md#google_analytics)

#### nav

The `nav` variable is used to create the navigation for the documentation. The
`nav` object is an iterable of [navigation objects](#navigation-objects) as
defined by the [nav] configuration setting.

[nav]: ../user-guide/configuration.md#nav

In addition to the iterable of [navigation objects](#navigation-objects), the
`nav` object contains the following attributes:

##### nav.homepage

The [page](#page) object for the homepage of the site.

##### nav.pages

A flat list of all [page](#page) objects contained in the navigation. This list
is not necessarily a complete list of all site pages as it does not contain
pages which are not included in the navigation. This list does match the list
and order of pages used for all "next page" and "previous page" links. For a
list of all pages, use the [pages](#pages) template variable.

##### Nav Example

Following is a basic usage example which outputs the first and second level
navigation as a nested list.

```django
{% if nav|length>1 %}
    <ul>
    {% for nav_item in nav %}
        {% if nav_item.children %}
            <li>{{ nav_item.title }}
                <ul>
                {% for nav_item in nav_item.children %}
                    <li class="{% if nav_item.active%}current{% endif %}">
                        <a href="{{ nav_item.url|url }}">{{ nav_item.title }}</a>
                    </li>
                {% endfor %}
                </ul>
            </li>
        {% else %}
            <li class="{% if nav_item.active%}current{% endif %}">
                <a href="{{ nav_item.url|url }}">{{ nav_item.title }}</a>
            </li>
        {% endif %}
    {% endfor %}
    </ul>
{% endif %}
```

#### base_url

The `base_url` provides a relative path to the root of the MkDocs project. While
this can be used directly by prepending it to a local relative URL, it is best
to use the [url](#url) template filter, which is smarter about how it applies
`base_url`.

#### mkdocs_version

Contains the current MkDocs version.

#### build_date_utc

A Python datetime object that represents the date and time the documentation
was built in UTC. This is useful for showing how recently the documentation
was updated.

#### pages

A flat list of `File` objects for *all* pages in the project. This list can
contain pages not included in the global [navigation](#nav) and may not match
the order of pages within that navigation. The [page](#page) object for each
`File` can be accessed from `file.page`.

#### page

In templates which are not rendered from a Markdown source file, the `page`
variable is `None`. In templates which are rendered from a Markdown source file,
the `page` variable contains a `page` object. The same `page` objects are used
as `page` [navigation objects](#navigation-objects) in the global
[navigation](#nav) and in the [pages](#pages) template variable.

All `page` objects contain the following attributes:

##### page.title

Contains the Title for the current page.

##### page.content

The rendered Markdown as HTML, this is the contents of the documentation.

##### page.toc

An iterable object representing the Table of contents for a page. Each item in
the `toc` is an `AnchorLink` which contains the following attributes:

* `AnchorLink.title`: The text of the item.
* `AnchorLink.url`: The hash fragment of a URL pointing to the item.
* `AnchorLink.level`: The zero-based level of the item.
* `AnchorLink.children`: An iterable of any child items.

The following example would display the top two levels of the Table of Contents
for a page.

```django
<ul>
{% for toc_item in page.toc %}
    <li><a href="{{ toc_item.url }}">{{ toc_item.title }}</a></li>
    {% for toc_item in toc_item.children %}
        <li><a href="{{ toc_item.url }}">{{ toc_item.title }}</a></li>
    {% endfor %}
{% endfor %}
</ul>
```

##### page.meta

A mapping of the metadata included at the top of the markdown page. In this
example we define a `source` property above the page title.

```no-highlight
source: generics.py
        mixins.py

# Page title

Content...
```

A template can access this metadata for the page with the `meta.source`
variable. This could then be used to link to source files related to the
documentation page.

```django
{% for filename in page.meta.source %}
  <a class="github" href="https://github.com/.../{{ filename }}">
    <span class="label label-info">{{ filename }}</span>
  </a>
{% endfor %}
```

##### page.url

The URL of the page relative to the MkDocs `site_dir`. It is expected that this
be used with the [url](#url) filter to ensure the URL is relative to the current
page.

```django
<a href="{{ page.url|url }}">{{ page.title }}</a>
```

[base_url]: #base_url

##### page.abs_url

The absolute URL of the page from the server root as determined by the value
assigned to the [site_url] configuration setting. The value includes any
subdirectory included in the `site_url`, but not the domain. [base_url] should
not be used with this variable.

For example, if `site_url: https://example.com/`, then the value of
`page.abs_url` for the page `foo.md` would be `/foo/`. However, if
`site_url: https://example.com/bar/`, then the value of `page.abs_url` for the
page `foo.md` would be `/bar/foo/`.

[site_url]: ../user-guide/configuration.md#site_url

##### page.canonical_url

The full, canonical URL to the current page as determined by the value assigned
to the [site_url] configuration setting. The value includes the domain and any
subdirectory included in the `site_url`. [base_url] should not be used with this
variable.

##### page.edit_url

The full URL to the source page in the source repository. Typically used to
provide a link to edit the source page. [base_url] should not be used with this
variable.

##### page.is_homepage

Evaluates to `True` for the homepage of the site and `False` for all other
pages. This can be used in conjunction with other attributes of the `page`
object to alter the behavior. For example, to display a different title
on the homepage:

```django
{% if not page.is_homepage %}{{ page.title }} - {% endif %}{{ site_name }}
```

##### page.previous_page

The page object for the previous page or `None`. The value will be `None` if the
current page is the first item in the site navigation or if the current page is
not included in the navigation at all. When the value is a page object, the
usage is the same as for `page`.

##### page.next_page

The page object for the next page or `None`. The value will be `None` if the
current page is the last item in the site navigation or if the current page is
not included in the navigation at all. When the value is a page object, the
usage is the same as for `page`.

##### page.parent

The immediate parent of the page in the [site navigation](#nav). `None` if the
page is at the top level.

##### page.children

Pages do not contain children and the attribute is always `None`.

##### page.active

When `True`, indicates that this page is the currently viewed page. Defaults
to `False`.

##### page.is_section

Indicates that the navigation object is a "section" object. Always `False` for
page objects.

##### page.is_page

Indicates that the navigation object is a "page" object. Always `True` for
page objects.

##### page.is_link

Indicates that the navigation object is a "link" object. Always `False` for
page objects.

### Navigation Objects

Navigation objects contained in the [nav](#nav) template variable may be one of
[section](#section) objects, [page](#page) objects, and [link](#link) objects.
While section objects may contain nested navigation objects, pages and links do
not.

Page objects are the full page object as used for the current [page](#page) with
all of the same attributes available. Section and Link objects contain a subset
of those attributes as defined below:

#### Section

A `section` navigation object defines a named section in the navigation and
contains a list of child navigation objects. Note that sections do not contain
URLs and are not links of any kind. However, by default, MkDocs sorts index
pages to the top and the first child might be used as the URL for a section if a
theme chooses to do so.

 The following attributes are available on `section` objects:

##### section.title

The title of the section.

##### section.parent

The immediate parent of the section or `None` if the section is at the top
level.

##### section.children

An iterable of all child navigation objects. Children may include nested
sections, pages and links.

##### section.active

When `True`, indicates that a child page of this section is the current page and
can be used to highlight the section as the currently viewed section. Defaults
to `False`.

##### section.is_section

Indicates that the navigation object is a "section" object. Always `True` for
section objects.

##### section.is_page

Indicates that the navigation object is a "page" object. Always `False` for
section objects.

##### section.is_link

Indicates that the navigation object is a "link" object. Always `False` for
section objects.

#### Link

A `link` navigation object contains a link which does not point to an internal
MkDocs page. The following attributes are available on `link` objects:

##### link.title

The title of the link. This would generally be used as the label of the link.

##### link.url

The URL that the link points to. The URL should always be an absolute URLs and
should not need to have `base_url` prepended.

##### link.parent

The immediate parent of the link. `None` if the link is at the top level.

##### link.children

Links do not contain children and the attribute is always `None`.

##### link.active

External links cannot be "active" and the attribute is always `False`.

##### link.is_section

Indicates that the navigation object is a "section" object. Always `False` for
link objects.

##### link.is_page

Indicates that the navigation object is a "page" object. Always `False` for
link objects.

##### link.is_link

Indicates that the navigation object is a "link" object. Always `True` for
link objects.

### Extra Context

Additional variables can be passed to the template with the
[`extra`](../user-guide/configuration.md#extra) configuration option. This is a
set of key value pairs that can make custom templates far more flexible.

For example, this could be used to include the project version of all pages
and a list of links related to the project. This can be achieved with the
following `extra` configuration:

```yaml
extra:
    version: 0.13.0
    links:
        - https://github.com/mkdocs
        - https://docs.readthedocs.org/en/latest/builds.html#mkdocs
        - https://www.mkdocs.org/
```

And then displayed with this HTML in the custom theme.

```django
{{ config.extra.version }}

{% if config.extra.links %}
  <ul>
  {% for link in config.extra.links %}
      <li>{{ link }}</li>
  {% endfor %}
  </ul>
{% endif %}
```

## Template Filters

In addition to [Jinja's default filters], the following custom filters are
available to use in MkDocs templates:

### url

Normalizes a URL. Absolute URLs are passed through unaltered. If the URL is
relative and the template context includes a page object, then the URL is
returned relative to the page object. Otherwise, the URL is returned with
[base_url](#base_url) prepended.

```django
<a href="{{ page.url|url }}">{{ page.title }}</a>
```

### tojson

Safety convert a Python object to a value in a JavaScript script.

```django
<script>
    var mkdocs_page_name = {{ page.title|tojson|safe }};
</script>
```

## Search and themes

As of MkDocs version *0.17* client side search support has been added to MkDocs
via the `search` plugin. A theme needs to provide a few things for the plugin to
work with the theme.

While the `search` plugin is activated by default, users can disable the plugin
and themes should account for this. It is recommended that theme templates wrap
search specific markup with a check for the plugin:

```django
{% if 'search' in config['plugins'] %}
    search stuff here...
{% endif %}
```

At its most basic functionality, the search plugin will simply provide an index
file which is no more than a JSON file containing the content of all pages.
The theme would need to implement its own search functionality client-side.
However, with a few settings and the necessary templates, the plugin can provide
a complete functioning client-side search tool based on [lunr.js].

The following HTML needs to be added to the theme so that the provided
JavaScript is able to properly load the search scripts and make relative links
to the search results from the current page.

```django
<script>var base_url = '{{ base_url }}';</script>
```

With properly configured settings, the following HTML in a template  will add a
full search implementation to your theme.

```django
<h1 id="search">Search Results</h1>

<form action="search.html">
  <input name="q" id="mkdocs-search-query" type="text" >
</form>

<div id="mkdocs-search-results">
  Sorry, page not found.
</div>
```

The JavaScript in the plugin works by looking for the specific ID's used in the
above HTML. The form input for the user to type the search query must be
identified with `id="mkdocs-search-query"` and the div where the results will be
placed must be identified with `id="mkdocs-search-results"`.

The plugin supports the following options being set in the [theme's
configuration file], `mkdocs_theme.yml`:

### include_search_page

Determines whether the search plugin expects the theme to provide a dedicated
search page via a template located at `search/search.html`.

When `include_search_page` is set to `true`, the search template will be built
and available at `search/search.html`. This method is used by the `readthedocs`
theme.

When `include_search_page` is set to `false` or not defined, it is expected that
the theme provide some other mechanisms for displaying search results. For
example, the `mkdocs` theme displays results on any page via a modal.

### search_index_only

Determines whether the search plugin should only generate a search index or a
complete search solution.

When `search_index_only` is set to `false`, then the search plugin modifies the
Jinja environment by adding its own `templates` directory (with a lower
precedence than the theme) and adds its scripts to the `extra_javascript` config
setting.

When `search_index_only` is set to `true` or not defined, the search plugin
makes no modifications to the Jinja environment. A complete solution using the
provided index file is the responsibility of the theme.

The search index is written to a JSON file at `search/search_index.json` in the
[site_dir]. The JSON object contained within the file may contain up to three
objects.

```json
{
    config: {...},
    docs: [...],
    index: {...}
}
```

If present, the `config` object contains the key/value pairs of config options
defined for the plugin in the user's `mkdocs.yml` config file under
`plugings.search`. The `config` object was new in MkDocs version *1.0*.

The `docs` object contains a list of document objects. Each document object is
made up of a `location` (URL), a `title`, and `text` which can be used to create
a search index and/or display search results.

If present, the `index` object contains a pre-built index which offers
performance improvements for larger sites. Note that the pre-built index is only
created if the user explicitly enables the [prebuild_index] config option.
Themes should expect the index to not be present, but can choose to use the
index when it is available. The `index` object was new in MkDocs version *1.0*.

[Jinja2 template]: http://jinja.pocoo.org/docs/dev/
[built-in themes]: https://github.com/mkdocs/mkdocs/tree/master/mkdocs/themes
[theme's configuration file]: #theme-configuration
[lunr.js]: https://lunrjs.com/
[site_dir]: ../user-guide/configuration.md#site_dir
[prebuild_index]: ../user-guide/configuration.md#prebuild_index
[Jinja's default filters]: https://jinja.palletsprojects.com/en/latest/templates/#builtin-filters

## Packaging Themes

MkDocs makes use of [Python packaging] to distribute themes. This comes with a
few requirements.

To see an example of a package containing one theme, see the [MkDocs Bootstrap
theme] and to see a package that contains many themes, see the [MkDocs
Bootswatch theme].

!!! Note

    It is not strictly necessary to package a theme, as the entire theme
    can be contained in the `custom_dir`. If you have created a "one-off theme,"
    that should be sufficient. However, if you intend to distribute your theme
    for others to use, packaging the theme has some advantages. By packaging
    your theme, your users can more easily install it, they can rely on a default
    [configuration] being defined, and they can then take advantage of the
    [custom_dir] to make tweaks to your theme to better suit their needs.

[Python packaging]: https://packaging.python.org/en/latest/
[MkDocs Bootstrap theme]: https://mkdocs.github.io/mkdocs-bootstrap/
[MkDocs Bootswatch theme]: https://mkdocs.github.io/mkdocs-bootswatch/

### Package Layout

The following layout is recommended for themes. Two files at the top level
directory called `MANIFEST.in` and `setup.py` beside the theme directory which
contains an empty `__init__.py` file, a theme configuration file
(`mkdocs_theme.yml`), and your template and media files.

```no-highlight
.
|-- MANIFEST.in
|-- theme_name
|   |-- __init__.py
|   |-- mkdocs_theme.yml
|   |-- main.html
|   |-- styles.css
`-- setup.py
```

The `MANIFEST.in` file should contain the following contents but with
theme_name updated and any extra file extensions added to the include.

```no-highlight
recursive-include theme_name *.ico *.js *.css *.png *.html *.eot *.svg *.ttf *.woff
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
```

The `setup.py` should include the following text with the modifications
described below.

```python
from setuptools import setup, find_packages

VERSION = '0.0.1'

setup(
    name="mkdocs-themename",
    version=VERSION,
    url='',
    license='',
    description='',
    author='',
    author_email='',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'mkdocs.themes': [
            'themename = theme_name',
        ]
    },
    zip_safe=False
)
```

Fill in the URL, license, description, author and author email address.

The name should follow the convention `mkdocs-themename` (like
`mkdocs-bootstrap` and `mkdocs-bootswatch`), starting with MkDocs, using
hyphens to separate words and including the name of your theme.

Most of the rest of the file can be left unedited. The last section we need to
change is the entry_points. This is how MkDocs finds the theme(s) you are
including in the package. The name on the left is the one that users will use
in their mkdocs.yml and the one on the right is the directory containing your
theme files.

The directory you created at the start of this section with the main.html file
should contain all of the other theme files. The minimum requirement is that
it includes a `main.html` for the theme. It **must** also include a
`__init__.py` file which should be empty, this file tells Python that the
directory is a package.

### Theme Configuration

A packaged theme is required to include a configuration file named
`mkdocs_theme.yml` which is placed in the root of your template files. The file
should contain default configuration options for the theme. However, if the
theme offers no configuration options, the file is still required and can be
left blank. A theme which is not packaged does not need a `mkdocs_theme.yml`
file as that file is not loaded from `theme.custom_dir`.

The theme author is free to define any arbitrary options deemed necessary and
those options will be made available in the templates to control behavior.
For example, a theme might want to make a sidebar optional and include the
following in the `mkdocs_theme.yml` file:

```yaml
show_sidebar: true
```

Then in a template, that config option could be referenced:

```django
{% if config.theme.show_sidebar %}
<div id="sidebar">...</div>
{% endif %}
```

And the user could override the default in their project's `mkdocs.yml` config
file:

```yaml
theme:
    name: themename
    show_sidebar: false
```

In addition to arbitrary options defined by the theme, MkDocs defines a few
special options which alters its behavior:

!!! block ""

    #### locale

    This option mirrors the [theme] config option of the same name. If this
    value is not defined in the `mkdocs_theme.yml` file and the user does not
    set it in `mkdocs.yml` then it will default to `en` (English). The value
    is expected to match the language used in the text provided by the theme
    (such a "next" and "previous" links) and should be used as the value of
    the `<html>` tag's `lang` attribute. See [Supporting theme localization/
    translation](#supporting-theme-localizationtranslation) for more
    information.

    Note that during configuration validation, the provided string is converted
    to a `Locale` object. The object contains `Locale.language` and
    `Locale.territory` attributes and will resolve as a string from within a
    template. Therefore, the following will work fine:

        <html lang="{ config.theme.locale }">

    If the locale was set to `fr_CA` (Canadian French), then the above template
    would render as:

        <html lang="fr_CA">

    If you did not want the territory attribute to be included, then reference
    the `language` attribute directly:

        <html lang="{ config.theme.locale.language }">

    That would render as:

        <html lang="fr">

    #### static_templates

    This option mirrors the [theme] config option of the same name and allows
    some defaults to be set by the theme. Note that while the user can add
    templates to this list, the user cannot remove templates included in the
    theme's config.

    #### extends

    Defines a parent theme that this theme inherits from. The value should be
    the string name of the parent theme. Normal [Jinja inheritance rules]
    apply.

Plugins may also define some options which allow the theme to inform a plugin
about which set of plugin options it expects. See the documentation for any
plugins you may wish to support in your theme.

### Distributing Themes

With the above changes, your theme should now be ready to install. This can be
done with pip, using `pip install .` if you are still in the same directory as
the setup.py.

Most Python packages, including MkDocs, are distributed on PyPI. To do this,
you should run the following command.

```no-highlight
python setup.py register
```

If you don't have an account setup, you should be prompted to create one.

For a much more detailed guide, see the official Python packaging
documentation for [Packaging and Distributing Projects].

[Packaging and Distributing Projects]: https://packaging.python.org/en/latest/distributing/
[theme]: ../user-guide/configuration.md#theme
[Jinja inheritance rules]: https://jinja.palletsprojects.com/en/latest/templates/#template-inheritance

## Supporting theme Localization/Translation

While the built-in themes provide support for [localization/translation] of
templates, custom themes and third-party themes may choose not to. Regardless,
the [`locale`](#locale) setting of the `theme` configuration option is always
present and is relied upon by other parts of the system. Therefore, it is
recommended that all third-party themes use the same setting for designating a
language regardless of the system they use for translation. In that way, users
will experience consistent behavior regardless of the theme they may choose.

The method for managing translations is up to the developers of a theme.
However, if a theme developer chooses to use the same mechanisms used by the
built-in themes, the sections below outline how to enable and make use of the
same commands utilized by MkDocs.

[localization/translation]: ../user-guide/localizing-your-theme.md
[Theme Configuration]: #theme-configuration

### Enabling the Localization/Translation commands

MkDocs includes some helper commands which are light wrappers around [pybabel's
commands][pybabel]. To use the commands on your own theme, add the following to
your theme's `setup.py` script:

```python
from mkdocs.commands.setup import babel_cmdclass

setup(
    ...
    cmdclass=babel_cmdclass
)
```

Note that `cmdclass=babel_cmdclass` was added an a parameter passed to
the `setup` function.

!!! warning
    As **pybabel is not installed by default** and most users will not have
    pybabel installed, theme developers and/or translators should make sure to
    have installed the necessary dependencies
    (using `pip install mkdocs[i18n]`) in order for the commands to be
    available for use.

[pybabel]: https://babel.pocoo.org/en/latest/setup.html

### Using the Localization/Translation commands

Since the translation commands are embedded in the `setup.py` script of your
custom theme they should be called from the root of your theme's working
tree as follows:

```bash
python setup.py <command_name> [OPTIONS]
```

Each command provides a detailed list of options available with the `-h/--help`
option.

For an overview of the workflow used by MkDocs to translate the built-in
themes, see the appropriate [section] of the Contributing Guide and the
[Translation Guide].

Default values for many of the options to the commands can be defined in a
`setup.cfg` file. Create a section using the command name as the section name,
and the long option name as the key. See MkDocs' own [setup.cfg] file for an
example.

A summary of changes/additions to the behavior and options of the upstream
[pybabel commands][pybabel] are summarized below.

[section]: ../about/contributing.md#submitting-changes-to-the-builtin-themes
[Translation Guide]: translations.md
[setup.cfg]: https://github.com/mkdocs/mkdocs/blob/master/setup.cfg

#### compile_catalog

The `-t/--theme` option has been added to this command. The `theme` specified
must be a `theme` defined as a entry point in the same `setup.py` script. Other
themes will not be recognized. If only one `theme` has been defined as an entry
point, then that `theme` will be used as the default if none is specified by
this option. If more than one `theme` is defined as entry points, then no
default is set and a `theme` must be specified by this option. The command only
operates on one theme at a time. Therefore, the command needs to be run once
for each theme included in a package.

When a `theme` is specified, the directory of that `theme` as defined in the
entry point is used to define a default value of the `-d/--directory` option.
The `--directory` option is set to `{theme_dir}/locales`. If a `directory` is
passed to the `--directory` option, then the `theme` option is ignored.

#### extract_messages

The `-t/--theme` option has been added to this command. The `theme` specified
must be a `theme` defined as a entry point in the same `setup.py` script. Other
themes will not be recognized. If only one `theme` has been defined as an entry
point, then that `theme` will be used as the default if none is specified by
this option. If more than one `theme` is defined as entry points, then no
default is set and a `theme` must be specified by this option. The command only
operates on one theme at a time. Therefore, the command needs to be run once
for each theme included in a package.

When a `theme` is specified, the directory of that `theme` as defined in the
entry point is used to define a default value for the `--input-dirs` and
`--output-file` options. The `--input-dirs` option is set to the `theme`
directory and `--output-file` is set to `{theme_dir}/{domain}.pot`. If a path
is provided to either option, then the `theme` option is ignored for that
option.

The `--domain` option has been added to this command and can be used to
override the `domain` used for the `output-file` based on the `theme`.
Defaults to `messages`.

The `-F/--mapping-file` option defaults to the [mapping file] used by MkDocs'
built-in themes. However, if that mapping file does not meet your theme's needs
to can override it by providing your own and passing the path of that file into
the option.

[mapping file]: https://github.com/mkdocs/mkdocs/tree/master/mkdocs/themes/babel.cfg

#### init_catalog

The `-t/--theme` option has been added to this command. The `theme` specified
must be a `theme` defined as a entry point in the same `setup.py` script. Other
themes will not be recognized. If only one `theme` has been defined as an entry
point, then that `theme` will be used as the default if none is specified by
this option. If more than one `theme` is defined as entry points, then no
default is set and a `theme` must be specified by this option. The command only
operates on one theme at a time. Therefore, the command needs to be run once
for each theme included in a package.

When a `theme` is specified, the directory of that `theme` as defined in the
entry point is used to define a default value for the `-i/--input-file` and
`-d/--output-dir` options. The `--input-file` option is set to
`{theme_dir}/{domain}.pot` (`domain` defaults to `messages`) and `--output-dir`
is set to `{theme_dir}/locales`. If a path is provided to either option, then
the `theme` option is ignored for that option.

#### update_catalog

The `-t/--theme` option has been added to this command. The `theme` specified
must be a `theme` defined as a entry point in the same `setup.py` script. Other
themes will not be recognized. If only one `theme` has been defined as an entry
point, then that `theme` will be used as the default if none is specified by
this option. If more than one `theme` is defined as entry points, then no
default is set and a `theme` must be specified by this option. The command only
operates on one theme at a time. Therefore, the command needs to be run once
for each theme included in a package.

When a `theme` is specified, the directory of that `theme` as defined in the
entry point is used to define a default value for the `-i/--input-file` and
`-d/--output-dir` options. The `--input-file` option is set to
`{theme_dir}/{domain}.pot` (`domain` defaults to `messages`) and `--output-dir`
is set to `{theme_dir}/locales`. If a path is provided to either option, then
the `theme` option is ignored for that option.

### Example custom theme Localization/Translation workflow

!!! note

    If your theme inherits from an existing theme which already provides
    translation catalogs, your theme's translations will be merged with the
    parent theme's translations during a MkDocs build.

    This means that you only need to concentrate on the added translations.
    Yet, you will still benefit from the translations of the parent theme. At
    the same time, you may override any of parent theme's translations!

Let's suppose that you're working on your own fork of the
[mkdocs-basic-theme][basic theme] and want to add translations to it.

You would first modify the `setup.py` like this:

```diff
--- a/setup.py
+++ b/setup.py
@@ -1,4 +1,5 @@
 from setuptools import setup, find_packages
+from mkdocs.commands.setup import babel_cmdclass

 VERSION = '1.1'

@@ -18,5 +19,6 @@ setup(
             'basictheme = basic_theme',
         ]
     },
-    zip_safe=False
+    zip_safe=False,
+    cmdclass=babel_cmdclass
 )
```

Next, you would edit the templates by wrapping text in your HTML sources with
`{% trans %}` and `{% endtrans %}` as follows:

```diff
--- a/basic_theme/base.html
+++ b/basic_theme/base.html
@@ -88,7 +88,7 @@

 <body>

-  <h1>This is an example theme for MkDocs.</h1>
+  <h1>{% trans %}This is an example theme for MkDocs.{% endtrans %}</h1>

   <p>
     It is designed to be read by looking at the theme HTML which is heavily
```

Then you would follow the [Translation Guide] as usual to get your translations
running.

### Packaging Translations with your theme

While the Portable Object Template (`pot`) file created by the
`extract_messages` command and the Portable Object (`po`) files created by the
`init_catalog` and `update_catalog` commands are useful for creating and
editing translations, they are not used by MkDocs directly and do not need to
be included in a packaged release of a theme. When MkDocs builds a site with
translations, it only makes use of the binary `mo` files(s) for the specified
locale. Therefore, when [packaging a theme], you would need to make the
following addition to your `MANIFEST.in` file:

``` no-highlight
recursive-include theme_name *.mo
```

Then, before building your Python package, you will want to ensure that the
binary `mo` file for each locale is up-to-date by running the `compile_catalog`
command for each locale. MkDocs expects the binary `mo` files to be located at
`locales/<locale>/LC_MESSAGES/messages.mo`, which the `compile_catalog`
command automatically does for you. See [Testing theme translations] for
details.

!!! note

    As outlined in our [Translation Guide], the MkDocs project has chosen to
    include the `pot` and `po` files in our code repository, but not the
    `mo` files. This requires us to always run `compile_catalog` before
    packaging a new release regardless of whether any changes were made to a
    translation or not. However, you may chose an alternate workflow for your
    theme. At a minimum, you need to ensure that up-to-date `mo` files are
    included at the correct location in each release. However, you may use a
    different process for generating those `mo` files if you chose to do so.

[packaging a theme]: #packaging-themes
[Testing theme translations]: translations.md#testing-theme-translations
