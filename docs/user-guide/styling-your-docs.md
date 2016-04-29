# Styling your docs

How to style and theme your documentation.

---

MkDocs includes a couple [built-in themes] as well as various [third party
themes], all of which can easily be customized with [extra CSS or
JavaScript][docs_dir] or overridden from the [theme directory][theme_dir]. You
can also create your own [custom theme] from the grown up for your
documentation.

To use a theme that is included in MkDocs, simply add this to your
`mkdocs.yml` config file.

    theme: readthedocs

Replace [`readthedocs`](#readthedocs) with any of the [built-in themes] listed below.

To create a new custom theme see the [Custom Themes][custom theme] page, or to
more heavily customize an existing theme, see
the [Customizing a Theme][customize] section below.

## Built-in themes

### mkdocs

![mkdocs](/img/mkdocs.png)

### readthedocs

![ReadTheDocs](http://docs.readthedocs.io/en/latest/_images/screen_mobile.png)

### Third Party Themes

A list of third party themes can be found in the MkDocs [community wiki]. If you
have created your own, please feel free to add it to the list.

## Customizing a Theme

If you would like to make a few tweaks to an existing theme, there is no need to
create your own theme from scratch. For minor tweaks which only require some CSS
and/or JavaScript, you can use the [docs_dir]. However, for more complex
customizations, including overriding templates, you will need to use the
[theme_dir].

### Using the docs_dir

The [extra_css] and [extra_javascript] configuration options can be used to
make tweaks and customizations to existing themes. To use these, you simply
need to include either CSS or JavaScript files within your [documentation
directory].

For example, to change the colour of the headers in your documentation, create
a file called `extra.css` and place it next to the documentation Markdown. In
that file add the following CSS.

```CSS
h1 {
  color: red;
}
```

!!! note

    If you are deploying your documentation with [ReadTheDocs]. You will need
    to explicitly list the CSS and JavaScript files you want to include in
    your config. To do this, add the following to your mkdocs.yml.

        extra_css: [extra.css]

After making these changes, they should be visible when you run
`mkdocs serve` - if you already had this running, you should see that the CSS
changes were automatically picked up and the documentation will be updated.

!!! note

    Any extra CSS or JavaScript files will be added to the generated HTML
    document after the page content. If you desire to include a JavaScript
    library, you may have better sucess including the library by using the
    [theme_dir].

### Using the theme_dir

The [theme_dir] configuration option can be used to point to a directory of
files which override the files in the theme set on the [theme] configuration
option. Any file in the `theme_dir` with the same name as a file in the `theme`
will replace the file of the same name in the `theme`. Any additional files in
the `theme_dir` will be added to the `theme`. The contents of the `theme_dir`
should mirror the directory structure of the `theme`. You may include templates,
JavaScript files, CSS files, images, fonts, or any other media included in a
theme.

For example, the [mkdocs] theme ([browse source]), contains the following
directory structure (in part):

```nohighlight
- css\
- fonts\
- img\
  - favicon.ico
  - grid.png
- js\
- 404.html
- base.html
- content.html
- nav-sub.html
- nav.html
- toc.html
```

To override any of the files contained in that theme, create a new directory
next to your `docs_dir`:

```bash
mkdir custom_theme
```

And then point your `mkdocs.yml` configuration file at the new directory:

```yaml
theme_dir: custom_theme
```

To override the 404 error page ("file not found"), add a new template file named
`404.html` to the `custom_theme` directory. For information on what can be
included in a template, review the documentation for building a [custom theme].

To override the favicon, you can add a new icon file at
`custom_theme/img/favicon.ico`.

To include a JavaScript library, copy the library to the `custom_theme/js/`
directory.

Your directory structure should now look like this:

```nohighlight
- docs/
  - index.html
- custom_theme/
  - img/
    - favicon.ico
  - js/
    - somelib.js
  - 404.html
- config.yml
```

!!! Note

    Any files included in the `theme` but not included in the `theme_dir` will
    still be utilized. The `theme_dir` will only override/replace files in the
    `theme`. If you want to remove files, or build a theme from scratch, then
    you should review the documentation for building a [custom theme].

[built-in themes]: #built-in-themes
[third party themes]: #third-party-themes
[docs_dir]: #using-the-docs_dir
[theme_dir]: #using-the-theme_dir
[customize]: #customizing-a-theme
[custom theme]: ./custom-themes.md
[ReadTheDocs]: ./deploying-your-docs.md#readthedocs
[community wiki]: https://github.com/mkdocs/mkdocs/wiki/MkDocs-Themes
[documentation directory]: ./configuration/#docs_dir
[extra_css]: ./configuration.md#extra_css
[extra_javascript]: ./configuration.md#extra_javascript
[theme_dir]: ./configuration/#theme_dir
[theme]: ./configuration/#theme
[mkdocs]: #mkdocs
[browse source]: https://github.com/mkdocs/mkdocs/tree/master/mkdocs/themes/mkdocs
