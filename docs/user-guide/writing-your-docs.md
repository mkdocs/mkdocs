# Writing your docs

How to write and layout your markdown source files.

---

## Configure Pages and Navigation

The [pages configuration](/user-guide/configuration.md#pages) in your
`mkdocs.yml` defines which pages are built by MkDocs and how they appear in the
documentation navigation. If not provided, the pages configuration will be
automatically created by discovering all the Markdown files in the
[documentation directory](/user-guide/configuration.md#docs_dir). An
automatically created pages configuration will always be sorted
alphanumerically by file name. You will need to manually define your pages
configuration if you would like your pages sorted differantly.

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

### Multilevel documentation

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

## File layout

Your documentation source should be written as regular Markdown files, and
placed in a directory somewhere in your project. Normally this directory will be
named `docs` and will exist at the top level of your project, alongside the
`mkdocs.yml` configuration file.

The simplest project you can create will look something like this:

```no-highlight
mkdocs.yml
docs/
    index.md
```

By convention your project homepage should always be named `index`. Any of the
following extensions may be used for your Markdown source files: `markdown`,
`mdown`, `mkdn`, `mkd`, `md`.

You can also create multi-page documentation, by creating several markdown
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

## Linking documents

MkDocs allows you to interlink your documentation by using regular Markdown
hyperlinks.

### Internal hyperlinks

When linking between pages in the documentation you can simply use the regular
Markdown hyperlinking syntax, including the relative path to the Markdown
document you wish to link to.

    Please see the [project license](license.md) for further details.

When the MkDocs build runs, these hyperlinks will automatically be transformed
into a hyperlink to the appropriate HTML page.

When working on your documentation you should be able to open the linked
Markdown document in a new editor window simply by clicking on the link.

If the target documentation file is in another directory you'll need to make
sure to include any relative directory path in the hyperlink.

    Please see the [project license](../about/license.md) for further details.

You can also link to a section within a target documentation page by using an
anchor link. The generated HTML will correctly transform the path portion of the
hyperlink, and leave the anchor portion intact.

    Please see the [project license](about.md#license) for further details.

## Images and media

As well as the Markdown source files, you can also include other file types in
your documentation, which will be copied across when generating your
documentation site. These might include images and other media.

For example, if your project documentation needed to include a [GitHub pages
CNAME
file](https://help.github.com/articles/using-a-custom-domain-with-github-pages/)
and a PNG formatted screenshot image then your file layout might look as
follows:

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

You image will now be embedded when you build the documentation, and should also
be previewed if you're working on the documentation with a Markdown editor.

## Markdown extensions

MkDocs supports the following Markdown extensions.

### Tables

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

### Fenced code blocks

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
after the backticks:

~~~no-highlight
```python
def fn():
    pass
```
~~~
