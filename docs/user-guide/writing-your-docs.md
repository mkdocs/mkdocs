# Writing your docs

How to layout and write your Markdown source files.

---

## File layout

Your documentation source should be written as regular Markdown files (see
[Writing with Markdown](#writing-with-markdown) below), and placed in the
[documentation directory](configuration.md#docs_dir). By default, this directory
will be named `docs` and will exist at the top level of your project, alongside
the `mkdocs.yml` configuration file.

The simplest project you can create will look something like this:

```no-highlight
mkdocs.yml
docs/
    index.md
```

By convention your project homepage should always be named `index`. Any of the
following extensions may be used for your Markdown source files: `markdown`,
`mdown`, `mkdn`, `mkd`, `md`.

You can also create multi-page documentation, by creating several Markdown
files:

```no-highlight
mkdocs.yml
docs/
    index.md
    about.md
    license.md
```

The file layout you use determines the URLs that are used for the generated
pages. Given the above layout, pages would be generated for the following URLs:

```no-highlight
/
/about/
/license/
```

You can also include your Markdown files in nested directories if that better
suits your documentation layout.

```no-highlight
docs/
    index.md
    user-guide/getting-started.md
    user-guide/configuration-options.md
    license.md
```

Source files inside nested directories will cause pages to be generated with
nested URLs, like so:

```no-highlight
/
/user-guide/getting-started/
/user-guide/configuration-options/
/license/
```

### Configure Pages and Navigation

The [pages configuration](configuration.md#pages) in your `mkdocs.yml` defines
which pages are built by MkDocs and how they appear in the documentation
navigation. If not provided, the pages configuration will be automatically
created by discovering all the Markdown files in the [documentation
directory](configuration.md#docs_dir). An automatically created pages
configuration will always be sorted alphanumerically by file name. You will need
to manually define your pages configuration if you would like your pages sorted
differently.

A simple pages configuration looks like this:

```no-highlight
pages:
- 'index.md'
- 'about.md'
```

With this example we will build two pages at the top level and they will
automatically have their titles inferred from the filename. Assuming `docs_dir`
has the default value, `docs`, the source files for this documentation would be
`docs/index.md` and `docs/about.md`. To provide a custom name for these pages,
they can be added before the filename.

```no-highlight
pages:
- Home: 'index.md'
- About: 'about.md'
```

Subsections can be created by listing related pages together under a section
title. For example:

```no-highlight
pages:
- Home: 'index.md'
- User Guide:
    - 'Writing your docs': 'user-guide/writing-your-docs.md'
    - 'Styling your docs': 'user-guide/styling-your-docs.md'
- About:
    - 'License': 'about/license.md'
    - 'Release Notes': 'about/release-notes.md'
```

With the above configuration we have three top level sections: Home, User Guide
and About. Then under User Guide we have two pages, Writing your docs and
Styling your docs. Under the About section we also have two pages, License and
Release Notes.

Note that a section cannot have a page assigned to it. Sections are only
containers for child pages and sub-sections. You may nest sections as deeply as
you like. However, be careful that you don't make it too difficult for your
users to navigate through the site navigation by over-complicating the nesting.
While sections may mirror your directly structure, they do not have to.

## Writing with Markdown

MkDocs pages must be authored in [Markdown][md], a lightweight markup language
which results in easy-to-read, easy-to-write plain text documents that can be
converted to valid HTML documents in a predictable manner.

MkDocs uses the [Python-Markdown] library to render Markdown documents to HTML.
Python-Markdown is almost completely compliant with the [reference
implementation][md], although there are a few very minor [differences].

In addition to the base Markdown [syntax] which is common across all Markdown
implementations, MkDocs includes support for extending the Markdown syntax with
Python-Markdown [extensions]. See the MkDocs' [markdown_extensions]
configuration setting for details on how to enable extensions.

MkDocs includes some extensions by default, which are highlighted below.

[Python-Markdown]: https://python-markdown.github.io/
[md]: http://daringfireball.net/projects/markdown/
[differences]: https://python-markdown.github.io/#differences
[syntax]: https://daringfireball.net/projects/markdown/syntax
[extensions]: https://python-markdown.github.io/extensions/
[markdown_extensions]: configuration.md#markdown_extensions

### Internal links

MkDocs allows you to interlink your documentation by using regular Markdown
[links]. However, there are a few additional benefits to formatting those links
specifically for MkDocs as outlines below.

[links]: https://daringfireball.net/projects/markdown/syntax#link

#### Linking to pages

When linking between pages in the documentation you can simply use the regular
Markdown [linking][links] syntax, including the *relative path* to the Markdown
document you wish to link to.

```no-highlight
Please see the [project license](license.md) for further details.
```

When the MkDocs build runs, these Markdown links will automatically be
transformed into an HTML hyperlink to the appropriate HTML page.

If the target documentation file is in another directory you'll need to make
sure to include any relative directory path in the link.

```no-highlight
Please see the [project license](../about/license.md) for further details.
```

The [toc] extension is used by MkDocs to generate an ID for every header in your
Markdown documents. You can use that ID to link to a section within a target
document by using an anchor link. The generated HTML will correctly transform
the path portion of the link, and leave the anchor portion intact.

```no-highlight
Please see the [project license](about.md#license) for further details.
```

Note that IDs are created from the text of a header. All text is converted to
lowercase and any disallowed characters, including white-space, are converted to
dashes. Consecutive dashes are then reduced to a single dash.

There are a few configuration settings provided by the toc extension which you
can set in your `mkdocs.yml` configuration file to alter the default behavior:

`permalink`:

: Generate permanent links at the end of each header. Default: `False`.

    When set to True the paragraph symbol (&para; or `&para;`) is used as the
    link text. When set to a string, the provided string is used as the link
    text. For example, to use the hash symbol (`#`) instead, do:

        markdown_extensions:
            - toc:
                permalink: "#"

`baselevel`:

: Base level for headers. Default: `1`.

    This setting allows the header levels to be automatically adjusted to fit
    within the hierarchy of your HTML templates. For example, if the Markdown
    text for a page should not contain any headers higher than level 2 (`<h2>`),
    do:

        markdown_extensions:
            - toc:
                baselevel: 2

    Then any headers in your document would be increased by 1. For example, the
    header `# Header` would be rendered as a level 2 header (`<h2>`) in the HTML
    output.

`separator`:

: Word separator. Default: `-`.

    Character which replaces white-space in generated IDs. If you prefer
    underscores, then do:

        markdown_extensions:
            - toc:
                separator: "_"

Note that if you would like to define multiple of the above settings, you must
do so under a single `toc` entry in the `markdown_extensions` configuration
option.

```yml
markdown_extensions:
    - toc:
        permalink: "#"
        baselevel: 2
        separator: "_"
```

[toc]: https://python-markdown.github.io/extensions/toc/

#### Linking to images and media

As well as the Markdown source files, you can also include other file types in
your documentation, which will be copied across when generating your
documentation site. These might include images and other media.

For example, if your project documentation needed to include a [GitHub pages
CNAME file] and a PNG formatted screenshot image then your file layout might
look as follows:

```no-highlight
mkdocs.yml
docs/
    CNAME
    index.md
    about.md
    license.md
    img/
        screenshot.png
```

To include images in your documentation source files, simply use any of the
regular Markdown image syntaxes:

```Markdown
Cupcake indexer is a snazzy new project for indexing small cakes.

![Screenshot](img/screenshot.png)

*Above: Cupcake indexer in progress*
```

Your image will now be embedded when you build the documentation, and should
also be previewed if you're working on the documentation with a Markdown editor.

[GitHub pages CNAME file]: https://help.github.com/articles/using-a-custom-domain-with-github-pages/

### Meta-Data

MkDocs includes support for [MultiMarkdown] style meta-data (often called
front-matter). Meta-data consists of a series of keywords and values defined at
the beginning of a Markdown document like this:

```no-highlight
Title:   My Document
Summary: A brief description of my document.
Authors: Waylan Limberg
         Tom Christie
Date:    January 23, 2018
blank-value:
some_url: http://example.com

This is the first paragraph of the document.
```

The keywords are case-insensitive and may consist of letters, numbers,
underscores and dashes and must end with a colon. The values consist of anything
following the colon on the line and may even be blank.

If a line is indented by 4 or more spaces, that line is assumed to be an
additional line of the value for the previous keyword. A keyword may have as
many lines as desired.

The first blank line ends all meta-data for the document. Therefore, the first
line of a document must not be blank.

Alternatively, you may use YAML style deliminators to mark the start and/or end
of your meta-data. When doing so, the first line of your document must be `---`.
The meta-data ends at the first blank line or the first line containing an end
deliminator (either `---` or `...`), whichever comes first. Even though YAML
deliminators are supported, meta-data is not parsed as YAML.

All meta-data is stripped from the document prior to being processing by
Python-Markdown. The keys and values are passed by MkDocs to the page template.
Therefore, if a theme includes support, the values of any keys can be displayed
on the page. See the documentation for your theme for information about which
keys may be supported, if any.

In addition to displaying information in a template, MkDocs includes support for
a few predefined meta-data keys which can alter the behavior of MkDocs for that
specific page. The following keys are supported:

`template`:

: The template to use with the current page.

    By default, MkDocs uses the `main.html` template of a theme to render
    Markdown pages. You can use the `template` meta-data key to define a
    different template file for that specific page. The template file must be
    available on the path(s) defined in the theme's environment.

`title`:

: The "title" to use for the document.

    MkDocs will attempt to determine the title of a document in the following
    ways, in order:

    1. A title defined in the [pages] configuration setting for a document.
    2. A title defined in the `title` meta-data key of a document.
    3. A level 1 Markdown header on the first line of the document body.
    4. The filename of a document.

    Upon finding a title for a page, MkDoc does not continue checking any
    additional sources in the above list.

[MultiMarkdown]: http://fletcherpenney.net/MultiMarkdown_Syntax_Guide#metadata
[pages]: configuration.md#pages

### Tables

The [tables] extension adds a basic table syntax to Markdown which is popular
across multiple implementations. The syntax is rather simple and is generally
only useful for simple tabular data.

A simple table looks like this:

```no-highlight
First Header | Second Header | Third Header
------------ | ------------- | ------------
Content Cell | Content Cell  | Content Cell
Content Cell | Content Cell  | Content Cell
```

If you wish, you can add a leading and tailing pipe to each line of the table:

```no-highlight
| First Header | Second Header | Third Header |
| ------------ | ------------- | ------------ |
| Content Cell | Content Cell  | Content Cell |
| Content Cell | Content Cell  | Content Cell |
```

Specify alignment for each column by adding colons to separator lines:

```no-highlight
First Header | Second Header | Third Header
:----------- |:-------------:| -----------:
Left         | Center        | Right
Left         | Center        | Right
```

Note that table cells cannot contain any block level elements and cannot contain
multiple lines of text. They can, however, include inline Markdown as defined in
Markdown's [syntax] rules.

Additionally, a table must be surrounded by blank lines. There must be a blank
line before and after the table.

[tables]: https://python-markdown.github.io/extensions/tables/

### Fenced code blocks

The [fenced code blocks] extension adds an alternate method of defining code
blocks without indentation.

The first line should contain 3 or more backtick (`` ` ``) characters, and the
last line should contain the same number of backtick characters (`` ` ``):

~~~no-highlight
```
Fenced code blocks are like Standard
Markdown’s regular code blocks, except that
they’re not indented and instead rely on
start and end fence lines to delimit the
code block.
```
~~~

With this approach, the language can optionally be specified on the first line
after the backticks which informs any syntax highlighters of the language used:

~~~no-highlight
```python
def fn():
    pass
```
~~~

Note that fenced code blocks can not be indented. Therefore, they cannot be
nested inside list items, blockquotes, etc.

[fenced code blocks]: https://python-markdown.github.io/extensions/fenced_code_blocks/
