# Configuration

Guide to all available configuration settings.

---

## Introduction

Project settings are configured by default using a YAML configuration file in
the project directory named `mkdocs.yml`. You can specify another path for it
by using the `-f`/`--config-file` option (see `mkdocs build --help`).

As a minimum, this configuration file must contain the `site_name` and
`site_url` settings. All other settings are optional.

## Project information

### site_name

This is a **required setting**, and should be a string that is used as the main
title for the project documentation. For example:

```yaml
site_name: Marshmallow Generator
```

When rendering the theme this setting will be passed as the `site_name` context
variable.

### site_url

Set the canonical URL of the site. This will add a `link` tag with the
`canonical` URL to the `head` section of each HTML page. If the 'root' of the
MkDocs site will be within a subdirectory of a domain, be sure to include that
subdirectory in the setting (`https://example.com/foo/`).

This setting is also used for `mkdocs serve`: the server will be mounted onto a
path taken from the path component of the URL, e.g. `some/page.md` will be
served from `http://127.0.0.1:8000/foo/some/page/` to mimic the expected remote
layout.

**default**: `null`

### repo_url

When set, provides a link to your repository (GitHub, Bitbucket, GitLab, ...)
on each page.

```yaml
repo_url: https://github.com/example/repository/
```

**default**: `null`

### repo_name

When set, provides the name for the link to your repository on each page.

**default**: `'GitHub'`, `'Bitbucket'` or `'GitLab'` if the `repo_url` matches
those domains, otherwise the hostname from the `repo_url`.

### edit_uri

The path from the base `repo_url` to the docs directory when directly viewing a
page, accounting for specifics of the repository host (e.g. GitHub, Bitbucket,
etc), the branch, and the docs directory itself. MkDocs concatenates `repo_url`
and `edit_uri`, and appends the input path of the page.

When set, and if your theme supports it, provides a link directly to the page in
your source repository. This makes it easier to find and edit the source for the
page. If `repo_url` is not set, this option is ignored. On some themes, setting
this option may cause an edit link to be used in place of a repository link.
Other themes may show both links.

The `edit_uri` supports query ('?') and fragment ('#') characters. For
repository hosts that use a query or a fragment to access the files, the
`edit_uri` might be set as follows. (Note the `?` and `#` in the URI...)

```yaml
# Query string example
edit_uri: '?query=root/path/docs/'
```

```yaml
# Hash fragment example
edit_uri: '#root/path/docs/'
```

For other repository hosts, simply specify the relative path to the docs
directory.

```yaml
# Query string example
edit_uri: root/path/docs/
```

!!! note
    On a few known hosts (specifically GitHub, Bitbucket and GitLab), the
    `edit_uri` is derived from the 'repo_url' and does not need to be set
    manually. Simply defining a `repo_url` will automatically populate the
    `edit_uri` configs setting.

    For example, for a GitHub- or GitLab-hosted repository, the `edit_uri`
    would be automatically set as `edit/master/docs/` (Note the `edit` path
    and `master` branch).

    For a Bitbucket-hosted repository, the equivalent `edit_uri` would be
    automatically set as `src/default/docs/` (note the `src` path and `default`
    branch).

    To use a different URI than the default (for example a different branch),
    simply set the `edit_uri` to your desired string. If you do not want any
    "edit URL link" displayed on your pages, then set `edit_uri` to an empty
    string to disable the automatic setting.

!!! warning
    On GitHub and GitLab, the default "edit" path (`edit/master/docs/`) opens
    the page in the online editor. This functionality requires that the user
    have and be logged in to a GitHub/GitLab account. Otherwise, the user will
    be redirected to a login/signup page. Alternatively, use the "blob" path
    (`blob/master/docs/`) to open a read-only view, which supports anonymous
    access.

**default**: `edit/master/docs/` for GitHub and GitLab repos or
`src/default/docs/` for a Bitbucket repo, if `repo_url` matches those domains,
otherwise `null`

### site_description

Set the site description. This will add a meta tag to the generated HTML header.

**default**: `null`

### site_author

Set the name of the author. This will add a meta tag to the generated HTML
header.

**default**: `null`

### copyright

Set the copyright information to be included in the documentation by the theme.

**default**: `null`

### remote_branch

Set the remote branch to commit to when using `gh-deploy` to deploy to GitHub
Pages. This option can be overridden by a command line option in `gh-deploy`.

**default**: `gh-pages`

### remote_name

Set the remote name to push to when using `gh-deploy` to deploy to GitHub Pages.
This option can be overridden by a command line option in `gh-deploy`.

**default**: `origin`

## Documentation layout

### nav

This setting is used to determine the format and layout of the global navigation
for the site. A minimal navigation configuration could look like this:

```yaml
nav:
    - 'index.md'
    - 'about.md'
```

All paths in the navigation configuration must be relative to the
[`docs_dir`](#docs_dir) configuration option. See the section on [configuring
pages and navigation] for a more detailed breakdown, including how to create
sub-sections.

Navigation items may also include links to external sites. While titles are
optional for internal links, they are required for external links. An external
link may be a full URL or a relative URL. Any path which is not found in the
files is assumed to be an external link. See the section about [Meta-Data] on
how MkDocs determines the page title of a document.

```yaml
nav:
    - Introduction: 'index.md'
    - 'about.md'
    - 'Issue Tracker': 'https://example.com/'
```

In the above example, the first two items point to local files while the third
points to an external site.

However, sometimes the MkDocs site is hosted in a subdirectory of a project's
site and you may want to link to other parts of the same site without including
the full domain. In that case, you may use an appropriate relative URL.

```yaml
site_url: https://example.com/foo/

nav:
    - Home: '../'
    - 'User Guide': 'user-guide.md'
    - 'Bug Tracker': '/bugs/'
```

In the above example, two different styles of external links are used. First,
note that the `site_url` indicates that the MkDocs site is hosted in the `/foo/`
subdirectory of the domain. Therefore, the `Home` navigation item is a relative
link that steps up one level to the server root and effectively points to
`https://example.com/`. The `Bug Tracker` item uses an absolute path from the
server root and effectively points to `https://example.com/bugs/`. Of course, the
`User Guide` points to a local MkDocs page.

**default**: By default `nav` will contain an alphanumerically sorted, nested
list of all the Markdown files found within the `docs_dir` and its
sub-directories. Index files will always be listed first within a sub-section.

## Build directories

### theme

Sets the theme and theme specific configuration of your documentation site.
May be either a string or a set of key/value pairs.

If a string, it must be the string name of a known installed theme. For a list
of available themes visit [Choosing Your Theme].

An example set of key/value pairs might look something like this:

```yaml
theme:
    name: mkdocs
    locale: en
    custom_dir: my_theme_customizations/
    static_templates:
        - sitemap.html
    include_sidebar: false
```

If a set of key/value pairs, the following nested keys can be defined:

!!! block ""

    #### name:

    The string name of a known installed theme. For a list of available themes
    visit [Choosing Your Theme].

    #### locale:

    A code representing the language of your site. See [Localizing your theme]
    for details.

    #### custom_dir:

    A directory containing a custom theme. This can either be a relative
    directory, in which case it is resolved relative to the directory containing
    your configuration file or it can be an absolute directory path from the
    root of your local file system.

    See [Customizing Your Theme][theme_dir] for details if you would like to tweak an
    existing theme.

    See the [Theme Developer Guide] if you would like to build your own theme
    from the ground up.

    #### static_templates:

    A list of templates to render as static pages. The templates must be located
    in either the theme's template directory or in the `custom_dir` defined in
    the theme configuration.

    #### (theme specific keywords)

    Any additional keywords supported by the theme can also be defined. See the
    documentation for the theme you are using for details.

**default**: `'mkdocs'`

### docs_dir

The directory containing the documentation source markdown files. This can
either be a relative directory, in which case it is resolved relative to the
directory containing your configuration file, or it can be an absolute directory
path from the root of your local file system.

**default**: `'docs'`

### site_dir

The directory where the output HTML and other files are created. This can either
be a relative directory, in which case it is resolved relative to the directory
containing your configuration file, or it can be an absolute directory path from
the root of your local file system.

**default**: `'site'`

!!! note "Note:"
    If you are using source code control you will normally want to ensure that
    your *build output* files are not committed into the repository, and only
    keep the *source* files under version control. For example, if using `git`
    you might add the following line to your `.gitignore` file:

        site/

    If you're using another source code control tool, you'll want to check its
    documentation on how to ignore specific directories.

### extra_css

Set a list of CSS files in your `docs_dir` to be included by the theme. For
example, the following example will include the extra.css file within the
css subdirectory in your [docs_dir](#docs_dir).

```yaml
extra_css:
    - css/extra.css
    - css/second_extra.css
```

**default**: `[]` (an empty list).

### extra_javascript

Set a list of JavaScript files in your `docs_dir` to be included by the theme.
See the example in [extra_css] for usage.

**default**: `[]` (an empty list).

### extra_templates

Set a list of templates in your `docs_dir` to be built by MkDocs. To see more
about writing templates for MkDocs read the documentation about [custom themes]
and specifically the section about the [available variables] to
templates. See the example in [extra_css] for usage.

**default**: `[]` (an empty list).

### extra

A set of key-value pairs, where the values can be any valid YAML construct, that
will be passed to the template. This allows for great flexibility when creating
custom themes.

For example, if you are using a theme that supports displaying the project
version, you can pass it to the theme like this:

```yaml
extra:
    version: 1.0
```

**default**: By default `extra` will be an empty key-value mapping.

## Preview controls

## Live Reloading

### watch

Determines additional directories to watch when running `mkdocs serve`.
Configuration is a YAML list.

```yaml
watch:
- directory_a
- directory_b
```

Allows a custom default to be set without the need to pass it through the `-w`/`--watch`
option every time the `mkdocs serve` command is called.

!!! Note

    The paths provided via the configuration file are relative to the configuration file.

    The paths provided via the `-w`/`--watch` CLI parameters are not. 

### use_directory_urls

This setting controls the style used for linking to pages within the
documentation.

The following table demonstrates how the URLs used on the site differ when
setting `use_directory_urls` to `true` or `false`.

Source file      | use_directory_urls: true  | use_directory_urls: false
---------------- | ------------------------- | -------------------------
index.md         | /                         | /index.html
api-guide.md     | /api-guide/               | /api-guide.html
about/license.md | /about/license/           | /about/license.html

The default style of `use_directory_urls: true` creates more user friendly URLs,
and is usually what you'll want to use.

The alternate style can be useful if you want your documentation to remain
properly linked when opening pages directly from the file system, because it
creates links that point directly to the target *file* rather than the target
*directory*.

**default**: `true`

### strict

Determines how warnings are handled. Set to `true` to halt processing when a
warning is raised. Set to `false` to print a warning and continue processing.

**default**: `false`

### dev_addr

Determines the address used when running `mkdocs serve`. Must be of the format
`IP:PORT`.

Allows a custom default to be set without the need to pass it through the
`--dev-addr` option every time the `mkdocs serve` command is called.

**default**: `'127.0.0.1:8000'`

See also: [site_url](#site_url).

## Formatting options

### markdown_extensions

MkDocs uses the [Python Markdown][pymkd] library to translate Markdown files
into HTML. Python Markdown supports a variety of [extensions][pymdk-extensions]
that customize how pages are formatted. This setting lets you enable a list of
extensions beyond the ones that MkDocs uses by default (`meta`, `toc`, `tables`,
and `fenced_code`).

For example, to enable the [SmartyPants typography extension][smarty], use:

```yaml
markdown_extensions:
    - smarty
```

Some extensions provide configuration options of their own. If you would like to
set any configuration options, then you can nest a key/value mapping
(`option_name: option value`) of any options that a given extension supports.
See the documentation for the extension you are using to determine what options
they support.

For example, to enable permalinks in the (included) `toc` extension, use:

```yaml
markdown_extensions:
    - toc:
        permalink: True
```

Note that a colon (`:`) must follow the extension name (`toc`) and then on a new
line the option name and value must be indented and separated by a colon. If you
would like to define multiple options for a single extension, each option must be
defined on a separate line:

```yaml
markdown_extensions:
    - toc:
        permalink: True
        separator: "_"
```

Add an additional item to the list for each extension. If you have no
configuration options to set for a specific extension, then simply omit options
for that extension:

```yaml
markdown_extensions:
    - smarty
    - toc:
        permalink: True
    - sane_lists
```

In the above examples, each extension is a list item (starts with a `-`). As an
alternative, key/value pairs can be used instead. However, in that case an empty
value must be provided for extensions for which no options are defined.
Therefore, the last example above could also be defined as follows:

```yaml
markdown_extensions:
    smarty: {}
    toc:
        permalink: True
    sane_lists: {}
```

This alternative syntax is required if you intend to override some options via
[inheritance].

!!! note "See Also:"
    The Python-Markdown documentation provides a [list of extensions][exts]
    which are available out-of-the-box. For a list of configuration options
    available for a given extension, see the documentation for that extension.

    You may also install and use various [third party extensions][3rd]. Consult
    the documentation provided by those extensions for installation instructions
    and available configuration options.

**default**: `[]` (an empty list).

### plugins

A list of plugins (with optional configuration settings) to use when building
the site. See the [Plugins] documentation for full details.

If the `plugins` config setting is defined in the `mkdocs.yml` config file, then
any defaults (such as `search`) are ignored and you need to explicitly re-enable
the defaults if you would like to continue using them:

```yaml
plugins:
    - search
    - your_other_plugin
```

To define options for a given plugin, use a nested set of key/value pairs:

```yaml
plugins:
    - search
    - your_other_plugin:
        option1: value
        option2: other value
```

In the above examples, each plugin is a list item (starts with a `-`). As an
alternative, key/value pairs can be used instead. However, in that case an empty
value must be provided for plugins for which no options are defined. Therefore,
the last example above could also be defined as follows:

```yaml
plugins:
    search: {}
    your_other_plugin:
        option1: value
        option2: other value
```

This alternative syntax is required if you intend to override some options via
[inheritance].

To completely disable all plugins, including any defaults, set the `plugins`
setting to an empty list:

```yaml
plugins: []
```

**default**: `['search']` (the "search" plugin included with MkDocs).

#### Search

A search plugin is provided by default with MkDocs which uses [lunr.js] as a
search engine. The following config options are available to alter the behavior
of the search plugin:

##### **separator**

A regular expression which matches the characters used as word separators when
building the index. By default whitespace and the hyphen (`-`) are used. To add
the dot (`.`) as a word separator you might do this:

```yaml
plugins:
    - search:
        separator: '[\s\-\.]+'
```

  **default**: `'[\s\-]+'`

##### **min_search_length**

An integer value that defines the minimum length for a search query. By default
searches shorter than 3 chars in length are ignored as search result quality with
short search terms are poor. However, for some use cases (such as documentation
about Message Queues which might generate searches for 'MQ') it may be preferable
to set a shorter limit.

```yaml
plugins:
    - search:
        min_search_length: 2
```

  **default**: 3

##### **lang**

A list of languages to use when building the search index as identified by their
[ISO 639-1] language codes. With [Lunr Languages], the following languages are
supported:

* `ar`: Arabic
* `da`: Danish
* `nl`: Dutch
* `en`: English
* `fi`: Finnish
* `fr`: French
* `de`: German
* `hu`: Hungarian
* `it`: Italian
* `ja`: Japanese
* `no`: Norwegian
* `pt`: Portuguese
* `ro`: Romanian
* `ru`: Russian
* `es`: Spanish
* `sv`: Swedish
* `th`: Thai
* `tr`: Turkish
* `vi`: Vietnamese

You may [contribute additional languages].

!!! Warning

    While search does support using multiple languages together, it is best not
    to add additional languages unless you really need them. Each additional
    language adds significant bandwidth requirements and uses more browser
    resources. Generally, it is best to keep each instance of MkDocs to a single
    language.

!!! Note

    Lunr Languages does not currently include support for Chinese or other Asian
    languages. However, some users have reported decent results using Japanese.

**default**: The value of `theme.locale` if set, otherwise `[en]`.

##### **prebuild_index**

Optionally generates a pre-built index of all pages, which provides some
performance improvements for larger sites. Before enabling, confirm that the
theme you are using explicitly supports using a prebuilt index (the builtin
themes do). Set to `true` to enable.

!!! warning

    This option requires that [Node.js] be installed and the command `node` be
    on the system path. If the call to `node` fails for any reason, a warning
    is issued and the build continues uninterrupted. You may use the `--strict`
    flag when building to cause such a failure to raise an error instead.

!!! Note

    On smaller sites, using a pre-built index is not recommended as it creates a
    significant increase is bandwidth requirements with little to no noticeable
    improvement to your users. However, for larger sites (hundreds of pages),
    the bandwidth increase is relatively small and your users will notice a
    significant improvement in search performance.

**default**: `False`

[Node.js]: https://nodejs.org/

##### **indexing**

Configures what strategy the search indexer will use when building the index
for your pages. This property is particularly useful if your project is large
in scale, and the index takes up an enormous amount of disk space.

```yaml
plugins:
    - search:
        indexing: 'full'
```

###### Options

|Option|Description|
|------|-----------|
|`full`|Indexes the title, section headings, and full text of each page.|
|`sections`|Indexes the title and section headings of each page.|
|`titles`|Indexes only the title of each page.|

**default**: `full`

## Environment Variables

In most cases, the value of a configuration option is set directly in the
configuration file. However, as an option, the value of a configuration option
may be set to the value of an environment variable using the `!ENV` tag. For
example, to set the value of the `site_name` option to the value of the
variable `SITE_NAME` the YAML file may contain the following:

```yaml
site_name: !ENV SITE_NAME
```

If the environment variable is not defined, then the configuration setting
would be assigned a `null` (or `None` in Python) value. A default value can be
defined as the last value in a list. Like this:

```yaml
site_name: !ENV [SITE_NAME, 'My default site name']
```

Multiple fallback variables can be used as well. Note that the last value is
not an environment variable, but must be a value to use as a default if none
of the specified environment variables are defined.

```yaml
site_name: !ENV [SITE_NAME, OTHER_NAME, 'My default site name']
```

Simple types defined within an environment variable such as string, bool,
integer, float, datestamp and null are parsed as if they were defined directly
in the YAML file, which means that the value will be converted to the
appropriate type. However, complex types such as lists and key/value pairs
cannot be defined within a single environment variable.

For more details, see the [pyyaml_env_tag](https://github.com/waylan/pyyaml-env-tag)
project.

## Configuration Inheritance

Generally, a single file would hold the entire configuration for a site.
However, some organizations may maintain multiple sites which all share a common
configuration across them. Rather than maintaining separate configurations for
each, the common configuration options can be defined in a parent configuration
while which each site's primary configuration file inherits.

To define the parent for a configuration file, set the `INHERIT` (all caps) key
to the path of the parent file. The path must be relative to the location of the
primary file.

For configuration options to be merged with a parent configuration, those
options must be defined as key/value pairs. Specifically, the
[markdown_extensions] and [plugins] options must use the alternative syntax
which does not use list items (lines which start with  `-`).

For example, suppose the common (parent) configuration is defined in `base.yml`:

```yaml
theme:
    name: mkdocs
    locale: en
    highlightjs: true

markdown_extensions:
    toc:
        permalink: true
    admonition: {}
```

Then, for the "foo" site, the primary configuration file would be defined at
`foo/mkdocs.yml`:

```yml
INHERIT: ../base.yml
site_name: Foo Project
site_url: https://example.com/foo
```

When running `mkdocs build`, the file at `foo/mkdocs.yml` would be passed in as
the configuration file. MkDocs will then parse that file, retrieve and parse the
parent file `base.yml` and deep merge the two. This would result in MkDocs
receiving the following merged configuration:

```yaml
site_name: Foo Project
site_url: https://example.com/foo

theme:
    name: mkdocs
    locale: en
    highlightjs: true

markdown_extensions:
    toc:
        permalink: true
    admonition: {}
```

Deep merging allows you to add and/or override various values in your primary
configuration file. For example, suppose for one site you wanted to add support
for definition lists, use a different symbol for permalinks, and define a
different separator. In that site's primary configuration file you could do:

```yaml
INHERIT: ../base.yml
site_name: Bar Project
site_url: https://example.com/bar

markdown_extensions:
    def_list: {}
    toc:
        permalink: 
        separator: "_"
```

In that case, the above configuration would be deep merged with `base.yml` and
result in the following configuration:

```yaml
site_name: Bar Project
site_url: https://example.com/bar

theme:
    name: mkdocs
    locale: en
    highlightjs: true

markdown_extensions:
    def_list: {}
    toc:
        permalink: 
        separator: "_"
    admonition: {}
```

Notice that the `admonition` extension was retained from the parent
configuration, the `def_list` extension was added, the value of
`toc.permalink` was replaced, and the value of `toc.separator` was added.

You can replace or merge the value of any key. However, any non-key is always
replaced. Therefore, you cannot append items to a list. You must redefine the
entire list.

As the [nav] configuration is made up of nested lists, this means that you
cannot merge navigation items. Of course, you can replace the entire `nav`
configuration with a new one. However, it is generally expected that the entire
navigation would be defined in the primary configuration file for a project.

!!! warning

    As a reminder, all path based configuration options must be relative to the
    primary configuration file and MkDocs does not alter the paths when merging.
    Therefore, defining paths in a parent file which is inherited by multiple
    different sites may not work as expected. It is generally best to define
    path based options in the primary configuration file only.

[Theme Developer Guide]: ../dev-guide/themes.md
[variables that are available]: ../dev-guide/themes.md#template-variables
[pymdk-extensions]: https://python-markdown.github.io/extensions/
[pymkd]: https://python-markdown.github.io/
[smarty]: https://python-markdown.github.io/extensions/smarty/
[exts]: https://python-markdown.github.io/extensions/
[3rd]: https://github.com/Python-Markdown/markdown/wiki/Third-Party-Extensions
[configuring pages and navigation]: writing-your-docs.md#configure-pages-and-navigation
[theme_dir]: customizing-your-theme.md#using-the-theme_dir
[choosing your theme]: choosing-your-theme.md
[Localizing your theme]: localizing-your-theme.md
[extra_css]: #extra_css
[Plugins]: ../dev-guide/plugins.md
[lunr.js]: https://lunrjs.com/
[ISO 639-1]: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
[Lunr Languages]: https://github.com/MihaiValentin/lunr-languages#lunr-languages-----
[contribute additional languages]: https://github.com/MihaiValentin/lunr-languages/blob/master/CONTRIBUTING.md
[Node.js]: https://nodejs.org/
[Lunr.py]: http://lunr.readthedocs.io/
[Lunr.py's issues]: https://github.com/yeraydiazdiaz/lunr.py/issues
[markdown_extensions]: #markdown_extensions
[plugins]: #plugins
[nav]: #nav
[inheritance]: #configuration-inheritance
