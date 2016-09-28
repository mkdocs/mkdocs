# Custom themes

A guide to creating and distributing custom themes.

---

!!! Note

    If you are looking for third party themes, they are listed in the MkDocs
    [community wiki](https://github.com/mkdocs/mkdocs/wiki/MkDocs-Themes). If
    you want to share a theme you create, you should list it on the Wiki.

When creating a new theme, you can either follow the steps in this guide to
create one from scratch or you can download the `mkdocs-basic-theme` as a
basic, yet complete, theme with all the boilerplate required. **You can find
this base theme on [GitHub](https://github.com/mkdocs/mkdocs-basic-theme)**.
It contains detailed comments in the code to describe the different features
and their usage.

## Creating a custom theme

The bare minimum required for a custom theme is a `main.html` [Jinja2
template] file. This should be placed in a directory which will be the
`theme_dir` and it should be created next to the `mkdocs.yml` configuration
file. Within `mkdocs.yml`, specify the `theme_dir` option and set it to the
name of the directory containing `main.html`. For example, given this example
project layout:

    mkdocs.yml
    docs/
        index.md
        about.md
    custom_theme/
        main.html
        ...

You would include the following settings in `mkdocs.yml` to use the custom theme
directory:

    theme: null
    theme_dir: 'custom_theme'

!!! Note

    Generally, when building your own custom theme, the `theme` configuration
    setting would be set to `null`. However, if used in combination with the
    `theme_dir` configuration value a custom theme can be used to replace only
    specific parts of a built-in theme. For example, with the above layout and
    if you set `theme: "mkdocs"` then the `main.html` file in the `theme_dir`
    would replace that in the theme but otherwise the `mkdocs` theme would
    remain the same. This is useful if you want to make small adjustments to an
    existing theme.

    For more specific information, see [styling your docs].

[styling your docs]: ./styling-your-docs.md#using-the-theme_dir

## Basic theme

The simplest `main.html` file is the following:

```django
<!DOCTYPE html>
<html>
  <head>
    <title>{% if page_title %}{{ page_title }} - {% endif %}{{ site_name }}</title>
  </head>
  <body>
    {{ content }}
  </body>
</html>
```

Article content from each page specified in `mkdocs.yml` is inserted using the
`{{ content }}` tag. Style-sheets and scripts can be brought into this theme as
with a normal HTML file. Navbars and tables of contents can also be generated
and included automatically, through the `nav` and `toc` objects, respectively.
If you wish to write your own theme, it is recommended to start with one of
the [built-in themes] and modify it accordingly.

!!! Note

    As MkDocs uses [Jinja] as its template engine, you have access to all the
    power of Jinja, including [template inheritance]. You may notice that the
    themes included with MkDocs make extensive use of template inheritance and
    blocks, allowing users to easily override small bits and pieces of the
    templates from the [theme_dir]. Therefore, the built-in themes are
    implemented in a `base.html` file, which `main.html` extends. Although not
    required, third party template authors are encouraged to follow a similar
    pattern and may want to define the same [blocks] as are used in the built-in
    themes for consistency.

[Jinja]: http://jinja.pocoo.org/
[template inheritance]: http://jinja.pocoo.org/docs/dev/templates/#template-inheritance
[theme_dir]: ./styling-your-docs.md#using-the-theme_dir
[blocks]: ./styling-your-docs.md#overriding-template-blocks

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

* [config.site_name](./configuration.md#site_name)
* [config.site_url](./configuration.md#site_url)
* [config.site_author](./configuration.md#site_author)
* [config.site_description](./configuration.md#site_description)
* [config.repo_url](./configuration.md#repo_url)
* [config.repo_name](./configuration.md#repo_name)
* [config.copyright](./configuration.md#copyright)
* [config.google_analytics](./configuration.md#google_analytics)

#### nav

The `nav` variable is used to create the navigation for the documentation.
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
                    <li class="{% if nav_item.active%}current{%endif%}">
                        <a href="{{ nav_item.url }}">{{ nav_item.title }}</a>
                    </li>
                {% endfor %}
                </ul>
            </li>
        {% else %}
            <li class="{% if nav_item.active%}current{%endif%}">
                <a href="{{ nav_item.url }}">{{ nav_item.title }}</a>
            </li>
        {% endif %}
    {% endfor %}
    </ul>
{% endif %}
```

The `nav` object also contains a `hompage` object, which points to the `page`
object of the homepage. For example, you may want to access `nav.homepage.url`.

#### base_url

The `base_url` provides a relative path to the root of the MkDocs project.
This makes it easy to include links to static assets in your theme. For
example, if your theme includes a `js` folder, to include `theme.js` from that
folder on all pages you would do this:

```django
<script src="{{ base_url }}/js/theme.js"></script>
```

#### extra_css

Contains a list of URLs to the style-sheets listed in the [extra_css]
config setting. Unlike the config setting, which contains local paths, this
variable contains absolute paths from the homepage.

[extra_css]: configuration.md#extra_css

#### extra_javascript

Contains a list of URLs to the scripts listed in the [extra_javascript] config
setting. Unlike the config setting, which contains local paths, this variable
contains absolute paths from the homepage.

[extra_javascript]: configuration.md#extra_javascript

#### mkdocs_version

Contains the current MkDocs version.

#### build_date_utc

A Python datetime object that represents the date and time the documentation
was built in UTC. This is useful for showing how recently the documentation
was updated.

#### page

In templates which are not rendered from a Markdown source file, the `page`
variable is `None`. In templates which are rendered from a Markdown source file,
the `page` variable contains a page object with the following attributes:

##### page.title

Contains the Title for the current page.

##### page.content

The rendered Markdown as HTML, this is the contents of the documentation.

##### page.toc

An object representing the Table of contents for a page. Displaying the table
of contents as a simple list can be achieved like this.

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

##### page.canonical_url

The full, canonical URL to the current page. This includes the `site_url` from
the configuration.

##### page.edit_url

The full URL to the input page in the source repository. Typically used to
provide a link to edit the source page.

##### page.url

The URL to the current page not including the `site_url` from the configuration.

##### page.is_homepage

Evaluates to `True` for the homepage of the site and `False` for all other
pages. This can be used in conjunction with other attributes of the `page`
object to alter the behavior. For example, to display a different title
on the homepage:

```django
{% if not page.is_homepage %}{{ page.title }} - {% endif %}{{ site_name }}
```

##### page.previous_page

The page object for the previous  page. The usage is the same as for
`page`.

##### page.next_page

The page object for the next page.The usage is the same as for `page`.

### Extra Context

Additional variables can be passed to the template with the
[`extra`](/user-guide/configuration.md#extra) configuration option. This is a
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
        - http://www.mkdocs.org/
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

## Search and themes

As of MkDocs `0.13` client side search support has been added to MkDocs with
[Lunr.js].

Search can either be added to every page in the theme or to a dedicated
template which must be named `search.html`. The search template will be build
with the same name and can be viewable with `mkdocs serve` at
`http://localhost:8000/search.html`. An example of the two different
approaches can be seen by comparing the `mkdocs` and `readthedocs` themes.

The following HTML needs to be added to the theme so the JavaScript is loaded
for Lunr.js.

```django
<script>var base_url = '{{ base_url }}';</script>
<script data-main="{{ base_url }}/mkdocs/js/search.js" src="{{ base_url }}/mkdocs/js/require.js"></script>
```

!!! note

    The above JavaScript will download the search index, for larger
    documentation projects this can be a heavy operation. In those cases, it
    is suggested that you either use the `search.html` approach to only
    include search on one page or load the JavaScript on an event like a form
    submit.

This loads the JavaScript and sets a global variable `base_url` which allows
the JavaScript to make the links relative to the current page. The above
JavaScript, with the following HTML in a `search.html` template will add a
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

This works by looking for the specific ID's used in the above HTML. The input
for the user to type the search query must have the ID `mkdocs-search-query`
and `mkdocs-search-results` is the directory where the results will be placed.

[Jinja2 template]: http://jinja.pocoo.org/docs/dev/
[built-in themes]: https://github.com/mkdocs/mkdocs/tree/master/mkdocs/themes
[lunr.js]: http://lunrjs.com/

## Packaging Themes

MkDocs makes use of [Python packaging] to distribute themes. This comes with a
few requirements.

To see an example of a package containing one theme, see the [MkDocs Bootstrap
theme] and to see a package that contains many themes, see the [MkDocs
Bootswatch theme].

!!! Note

    It is not strictly necessary to package a theme, as the entire theme
    can be contained in the `theme_dir`. If you have created a "one-off theme,"
    that should be sufficent. However, if you intend to distribute your theme
    for others to use, packaging the theme has some advantages. By packaging
    your theme, your users can more easily install it and they can them take
    advantage of the [theme_dir] to make tweaks to your theme to better suit
    their needs.

[Python packaging]: https://packaging.python.org/en/latest/
[MkDocs Bootstrap theme]: http://mkdocs.github.io/mkdocs-bootstrap/
[MkDocs Bootswatch theme]: http://mkdocs.github.io/mkdocs-bootswatch/

### Package Layout

The following layout is recommended for themes. Two files at the top level
directory called `MANIFEST.in` amd `setup.py` beside the theme directory which
contains an empty `__init__.py` file and your template and media files.

```no-highlight
.
|-- MANIFEST.in
|-- theme_name
|   |-- __init__.py
|   |-- main.py
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

The name should follow the convention `mkdocs-themename` (like `mkdocs-
bootstrap` and `mkdocs-bootswatch`), starting with MkDocs, using hyphens to
separate words and including the name of your theme.

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
