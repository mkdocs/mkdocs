# Styling your docs

How to style and theme your documentation.

---

MkDocs includes a number of [different themes](#built-in-themes) which can easily be customised with extra CSS or JavaScript or you can create a [custom theme](#custom-themes) for your documentation.

To use a theme that is included in MkDocs, simply add this to your `mkdocs.yml` config file.

    theme: amelia

Replace [`amelia`](#amelia) with any of the [builtin themes](#built-in-themes) listed below.

To customise a theme, simply place additional CSS and JavaScript files in the documentation directory next to the Markdown files and these will be automatically detected and added. Additionally, the [`extra_css`](/user-guide/configuration/#extra_css) and [`extra_javascript`](/user-guide/configuration/#extra_javascript) configuration options can be used to specifically include certain CSS or JavaScript files.

See the [configuration documentation](/user-guide/configuration/#theme) for more specific details about these options.

To create a new custom theme or more heavily customise an existing theme, see the [custom themes](#custom-themes) section below.


## Built-in themes

### MkDocs

![mkdocs](/img/mkdocs.png)

### Read the Docs

![ReadTheDocs](https://docs.readthedocs.org/en/latest/_images/screen_mobile.png)

### Bootstrap

![Bootstrap](http://bootstrapdocs.com/v2.3.1/docs/assets/img/examples/bootstrap-example-fluid.png)


### The bootswatch themes

#### Amelia

![Amelia](http://bootswatch.com/2/amelia/thumbnail.png)

#### Cerulean

![Cerulean](http://bootswatch.com/cerulean/thumbnail.png)

#### Cosmo

![Cosmo](http://bootswatch.com/cosmo/thumbnail.png)

#### Cyborg

![Cyborg](http://bootswatch.com/cyborg/thumbnail.png)

#### Flatly

![Flatly](http://bootswatch.com/flatly/thumbnail.png)

#### Journal

![Journal](http://bootswatch.com/journal/thumbnail.png)

#### Readable

![Readable](http://bootswatch.com/readable/thumbnail.png)

#### Simplex

![Simplex](http://bootswatch.com/simplex/thumbnail.png)

#### Slate

![Slate](http://bootswatch.com/slate/thumbnail.png)

#### Spacelab

![Spacelab](http://bootswatch.com/spacelab/thumbnail.png)

#### United

![United](http://bootswatch.com/united/thumbnail.png)

#### Yeti

![Yeti](http://bootswatch.com/yeti/thumbnail.png)

## Custom themes

The bare minimum required for a custom theme is a `base.html` [Jinja2 template] file. This should be placed in a directory at the same level as the `mkdocs.yml` configuration file. Within `mkdocs.yml`, specify the `theme_dir` option and set it to the name of the directory containing `base.html`. For example, given this example project layout:

    mkdocs.yml
    docs/
        index.md
        about.md
    custom_theme/
        base.html
        ...

You would include the following setting to use the custom theme directory:

    theme_dir: 'custom_theme'

If used in combination with the `theme` configuration value a custom theme can be used to replace only specific parts of a built-in theme. For example, with the above layout and if you set `theme: mkdocs` then the `base.html` file would replace that in the theme but otherwise it would remain the same. This is useful if you want to make small adjustments to an existing theme.

### Basic theme

The simplest `base.html` file is the following:

    <!DOCTYPE html>
    <html>
      <head>
      </head>
      <body>
        {{ content }}
      </body>
    </html>

Article content from each page specified in `mkdocs.yml` is inserted using the `{{ content }}` tag. Stylesheets and scripts can be brought into this theme as with a normal HTML file. Navbars and tables of contents can also be generated and included automatically, through the `nav` and `toc` objects, respectively. If you wish to write your own theme, it is recommended to start with one of the [built-in themes] and modify it accordingly.

### Template Variables

Each template in a theme is built with a template context. These are the variables that are available to themes. The context varies depending on the template that is being built. At the moment templates are either built with the global context or with a page specific context. The global context is used for HTML pages that don't represent an individual Markdown document, for example a 404.html page or search.html.

#### Global Context

The following variables in the context map directly the the [configuration options](/user-guide/configuration/).

Variable Name     | Configuration name
----------------- | ------------------- |
site_name         | site_name           |
site_author       | site_author         |
favicon           | site_favicon        |
page_description  | site_description    |
repo_url          | repo_url            |
repo_name         | repo_name           |
site_url          | site_url            |
extra_css         | extra_css           |
extra_javascript  | extra_javascript    |
extra             | extra               |
include_nav       | include_nav         |
include_next_prev | include_next_prev   |
copyright         | copyright           |
google_analytics  | google_analytics    |

The following variables provide information about the navigation and location.

##### nav
The `nav` variable is used to create the navigation for for the documentation. Following is a basic usage example which outputs the first and second level navigation as a nested list.

```
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
```

##### base_url
The `base_url` provides a relative path to the root of the MkDocs project. This makes it easy to include links to static assets in your theme. For example, if your theme includes a `js` folder, to include `theme.js` from that folder on all pages you would do this:

```
<script src="{{ base_url }}/js/theme.js"></script>
```

##### homepage_url
Provides a relative path to the documentation homepage.

##### mkdocs_version
Contains the current MkDocs version.

##### build_date_utc
A Python datetime object that includes represents the time the documentation was built in UTC. This is useful for showing how recently the documentation was updated.


#### Page Context
The page context includes all of the above Global context and the following additional variables.

##### page_title
Contains the Title for the current page.

##### page_description
Contains the description for the current page on the homepage, it is blank on other pages.

##### content
The rendered Markdown as HTML, this is the contents of the documentation.

##### toc
An object representing the Table of contents for a page. Displaying the table of contents as a simple list can be achieved like this.

```
  <ul>
  {% for toc_item in toc %}
      <li><a href="{{ toc_item.url }}">{{ toc_item.title }}</a></li>
      {% for toc_item in toc_item.children %}
          <li><a href="{{ toc_item.url }}">{{ toc_item.title }}</a></li>
      {% endfor %}
  {% endfor %}
  </ul>
```

##### meta
A mapping of the metadata included at the top of the markdown page.

##### canonical_url
The full, canonical URL to the current page. This includes the site_url from the configuration.

##### current_page
The page object for the current page. The page path and url properties can be displayed like this.

```
<h1>{{ current_page.title }}</h1>
<p> This page is at {{ current_page.url }}</p>
```

##### previous_page
The page object for the previous  page. The isage is the same as for
`current_page`.

##### next_page
The page object for the next page.The isage is the same as for `current_page`.

#### Extra Context

Additional variables can be passed to the template with the [`extra`](/user-guide/configuration/#extra) configuration option. This is a set of key value pairs that can make custom templates far more flexible.

For example, this could be used to include the project version of all pages and a list of links related to the project. This can be achieved with the following `extra` configuration:

```yaml
extra:
    version: 0.13.0
    links:
        - https://github.com/mkdocs
        - https://docs.readthedocs.org/en/latest/builds.html#mkdocs
        - http://www.mkdocs.org/
```

And then displayed with this HTML in the custom theme.

```html
{{ extra.version }}

{% if extra.links %}
  <ul>
  {% for link in extra.links %}
      <li>{{ link }}</li>
  {% endfor %}
  </ul>
{% endif %}
```

### Search and themes

As of MkDocs `0.13` client side search support has been added to MkDocs with [Lunr.js].

Search can either be added to every page in the theme or to a dedicated template which must be named `search.html`. The search template will be build with the same name and can be viewable with `mkdocs serve` at `http://localhost:8000/search.html`. An example of the two different approaches can be seen by comparing the `mkdocs` and `readthedocs` themes.

The following HTML needs to be added to the theme so the JavaScript is loaded for Lunr.js.

    <script>var base_url = '{{ base_url }}';</script>
    <script data-main="{{ base_url }}/mkdocs/js/search.js" src="{{ base_url }}/mkdocs/js/require.js"></script>

!!! note

    The above JavaScript will download the search index, for larger documentation projects this can be a heavy operation. In those cases, it is suggested that you either use the `search.html` approach to only include search on one page or load the JavaScript on an event like a form submit.

This loads the JavaScript and sets a global variable `base_url` which allows the JavaScript to make the links relative to the current page. The above JavaScript, with the following HTML in a `search.html` template will add a full search implementation to your theme.

    <h1 id="search">Search Results</h1>

    <form action="search.html">
      <input name="q" id="mkdocs-search-query" type="text" class="search_input search-query ui-autocomplete-input" placeholder="Search the Docs" autocomplete="off">
    </form>

    <div id="mkdocs-search-results">
      Sorry, page not found.
    </div>

This works by looking for the specific ID's used in the above HTML. The input for the user to type the search query must have the ID `mkdocs-search-query` and `mkdocs-search-results` is the directory where the results will be placed.


[Jinja2 template]: http://jinja.pocoo.org/docs/dev/
[built-in themes]: https://github.com/mkdocs/mkdocs/tree/master/mkdocs/themes
[lunr.js]: http://lunrjs.com/

