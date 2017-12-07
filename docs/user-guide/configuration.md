# Configuration

Guide to all available configuration settings.

---

## Introduction

Project settings are always configured by using a YAML configuration file in the
project directory named `mkdocs.yml`.

As a minimum this configuration file must contain the `site_name` setting. All
other settings are optional.

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

Set the canonical URL of the site. This will add a link tag with the canonical
URL to the generated HTML header.

**default**: `null`

### repo_url

When set, provides a link to your GitHub or Bitbucket repository on each page.

```yaml
repo_url: https://github.com/example/repository/
```

**default**: `null`

### repo_name

When set, provides a link to your GitHub or Bitbucket repository on each page.

**default**: `'GitHub'` or `'Bitbucket'` if the `repo_url` matches those
domains, otherwise `null`

### edit_uri

Path from the base `repo_url` to the docs directory when directly viewing a
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
    On a few known hosts (specifically GitHub and Bitbucket), the `edit_uri` is
    derived from the 'repo_url' and does not need to be set manually. Simply
    defining a `repo_url` will automatically populate the `edit_uri` config
    setting.

    For example, for a GitHub-hosted repository, the `edit_uri` would be
    automatically set as `edit/master/docs/` (Note the `edit` path and `master`
    branch).

    For a Bitbucket-hosted repository, the equivalent `edit_uri` would be
    automatically set as `src/default/docs/` (note the `src` path and `default`
    branch).

    To use a different URI than the default (for example a different branch),
    simply set the `edit_uri` to your desired string. If you do not want any
    "edit URL link" displayed on your pages, then set `edit_uri` to an empty
    string to disable the automatic setting.

!!! warning
    On GitHub, the default "edit" path (`edit/master/docs/`) opens the page in
    the online GitHub editor. This functionality requires that the user have and
    be logged in to a GitHub account. Otherwise, the user will be redirected to
    a login/signup page. Alternatively, use the "blob" path
    (`blob/master/docs/`) to open a read-only view, which supports anonymous
    access.

**default**: `edit/master/docs/` or `src/default/docs/` for GitHub or Bitbucket
repos, respectively, if `repo_url` matches those domains, otherwise `null`

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

### google_analytics

Set the Google analytics tracking configuration.

```yaml
google_analytics: ['UA-36723568-3', 'mkdocs.org']
```

**default**: `null`

### remote_branch

Set the remote branch to commit to when using `gh-deploy` to deploy to Github
Pages. This option can be overridden by a command line option in `gh-deploy`.

**default**: `gh-pages`

### remote_name

Set the remote name to push to when using `gh-deploy` to deploy to Github Pages.
This option can be overridden by a command line option in `gh-deploy`.

**default**: `origin`

## Documentation layout

### pages

This setting is used to determine the set of pages that should be built for the
documentation. For example, the following would create Introduction, User Guide
and About pages, given the three source files `index.md`, `user-guide.md` and
`about.md`, respectively.

```yaml
pages:
    - 'Introduction': 'index.md'
    - 'User Guide': 'user-guide.md'
    - 'About': 'about.md'
```

See the section on [configuring pages and navigation] for a more detailed
breakdown, including how to create sub-sections.

**default**: By default `pages` will contain an alphanumerically sorted, nested
list of all the Markdown files found within the `docs_dir` and its
sub-directories. If none are found it will be `[]` (an empty list).

## Build directories

### theme

Sets the theme and theme specific configuration of your documentation site.
May be either a string or a set of key/value pairs.

If a string, it must be the string name of a known installed theme. For a list
of available themes visit [styling your docs].

An example set of key/value pairs might look something like this:

```yaml
theme:
    name: mkdocs
    custom_dir: my_theme_customizations/
    static_templates:
        - sitemap.html
    include_sidebar: false
```

If a set of key/value pairs, the following nested keys can be defined:

!!! block ""

    #### name:

    The string name of a known installed theme. For a list of available themes
    visit [styling your docs].

    #### custom_dir:

    A directory to custom a theme. This can either be a relative directory, in
    which case it is resolved relative to the directory containing your
    configuration file, or it can be an absolute directory path.

    See [styling your docs][theme_dir] for details if you would like to tweak an
    existing theme.

    See [custom themes] if you would like to build your own theme from the
    ground up.

    #### static_templates:

    A list of templates to render as static pages. The templates must be located
    in either the theme's template directory or in the `custom_dir` defined in
    the theme configuration.

    #### (theme specific keywords)

    Any additional keywords supported by the theme can also be defined. See the
    documentation for the theme you are using for details.

**default**: `'mkdocs'`

### docs_dir

Lets you set the directory containing the documentation source markdown files.
This can either be a relative directory, in which case it is resolved relative
to the directory containing your configuration file, or it can be an absolute
directory path from the root of your local file system.

**default**: `'docs'`

### site_dir

Lets you set the directory where the output HTML and other files are created.
This can either be a relative directory, in which case it is resolved relative
to the directory containing your configuration file, or it can be an absolute
directory path from the root of your local file system.

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
and specifically the section about the [variables that are available] to
templates. See the example in [extra_css] for usage.

**default**: `[]` (an empty list).

### extra

A set of key value pairs, where the values can be any valid YAML construct, that
will be passed to the template. This allows for great flexibility when creating
custom themes.

For example, if you are using a theme that supports displaying the project
version, you can pass it to the theme like this:

```yaml
extra:
    version: 1.0
```

**default**: By default `extra` will be an empty key value mapping.

## Preview controls

### use_directory_urls

This setting controls the style used for linking to pages within the
documentation.

The following table demonstrates how the URLs used on the site differ when
setting `use_directory_urls` to `true` or `false`.

Source file  | Generated HTML       | use_directory_urls: true  | use_directory_urls: false
------------ | -------------------- | ------------------------ | ------------------------
index.md     | index.html           | /                        | /index.html
api-guide.md | api-guide/index.html | /api-guide/              | /api-guide/index.html
about.md     | about/index.html     | /about/                  | /about/index.html

The default style of `use_directory_urls: true` creates more user friendly URLs,
and is usually what you'll want to use.

The alternate style can occasionally be useful if you want your documentation to
remain properly linked when opening pages directly from the file system, because
it create links that point directly to the target *file* rather than the target
*directory*.

**default**: `true`

### strict

Determines if a broken link to a page within the documentation is considered a
warning or an error (link to a page not listed in the pages setting). Set to
true to halt processing when a broken link is found, false prints a warning.

**default**: `false`

### dev_addr

Determines the address used when running `mkdocs serve`. Must be of the format
`IP:PORT`.

Allows a custom default to be set without the need to pass it through the
`--dev_addr` option every time the `mkdocs serve` command is called.

**default**: `'127.0.0.1:8000'`

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
the site . See the [Plugins] documentation for full details.

If the `plugins` config setting is defined in the `mkdocs.yml` config file, then
any defaults (such as `search`) are ignored and you need to explicitly re-enable
the defaults if you would like to continue using them:

```yaml
plugins:
    - search
    - your_other_plugin
```

To completely disable all plugins, including any defaults, set the `plugins`
setting to an empty list:

```yaml
plugins: []
```

**default**: `['search']` (the "search" plugin included with MkDocs).

[custom themes]: custom-themes.md
[variables that are available]: custom-themes.md#template-variables
[pymdk-extensions]: https://python-markdown.github.io/extensions/
[pymkd]: https://python-markdown.github.io/
[smarty]: https://python-markdown.github.io/extensions/smarty/
[exts]: https://python-markdown.github.io/extensions/
[3rd]: https://github.com/Python-Markdown/markdown/wiki/Third-Party-Extensions
[configuring pages and navigation]: writing-your-docs.md#configure-pages-and-navigation
[theme_dir]: styling-your-docs.md#using-the-theme_dir
[styling your docs]: styling-your-docs.md
[extra_css]: #extra_css
[Plugins]: plugins.md
