# Styling your docs

How to style and theme your documentation.

---

MkDocs includes a number of different [builtin themes](#built-in-themes) and
[external themes](#bootstrap-and-bootswatch-themes) which can easily be
[customised with extra CSS or JavaScript](#customising-a-theme) or you can
create a [custom theme](/user-guide/custom-themes.md) for your documentation.

To use a theme that is included in MkDocs, simply add this to your
`mkdocs.yml` config file.

    theme: readthedocs

Replace [`readthedocs`](#readthedocs) with any of the [builtin themes](#built-
in-themes) listed below.

To create a new custom theme or more heavily customise an existing theme, see
the [custom themes](#custom-themes) section below.

## Built-in themes

### mkdocs

![mkdocs](/img/mkdocs.png)

### readthedocs

![ReadTheDocs](https://docs.readthedocs.org/en/latest/_images/screen_mobile.png)

## Bootstrap and Bootswatch Themes

MkDocs also includes themes provided by two packages. [MkDocs Bootstrap] and
[MkDocs Bootswatch]. The Bootstrap theme provides a theme based on [Bootstrap]
and the Bootstrap theme provides 12 different themed Bootstrap themes based on
the [Bootswatch] project.

!!! note

    The Bootstrap and Bootswatch themes will not be included by default from
    MkDocs version 1.0. They will need to be installed manually with `pip
    install mkdocs-bootstrap` or `pip install mkdocs-bootswatch`.

[Bootstrap]: http://getbootstrap.com/
[Bootswatch]: http://bootswatch.com/
[MkDocs Bootstrap]: http://mkdocs.github.io/mkdocs-bootstrap/
[MkDocs Bootswatch]: http://mkdocs.github.io/mkdocs-bootswatch/

### Bootstrap

![Bootstrap](http://bootstrapdocs.com/v2.3.1/docs/assets/img/examples/bootstrap-example-fluid.png)

### Amelia

![Amelia](http://bootswatch.com/2/amelia/thumbnail.png)

### Cerulean

![Cerulean](http://bootswatch.com/cerulean/thumbnail.png)

### Cosmo

![Cosmo](http://bootswatch.com/cosmo/thumbnail.png)

### Cyborg

![Cyborg](http://bootswatch.com/cyborg/thumbnail.png)

### Flatly

![Flatly](http://bootswatch.com/flatly/thumbnail.png)

### Journal

![Journal](http://bootswatch.com/journal/thumbnail.png)

### Readable

![Readable](http://bootswatch.com/readable/thumbnail.png)

### Simplex

![Simplex](http://bootswatch.com/simplex/thumbnail.png)

### Slate

![Slate](http://bootswatch.com/slate/thumbnail.png)

### Spacelab

![Spacelab](http://bootswatch.com/spacelab/thumbnail.png)

### United

![United](http://bootswatch.com/united/thumbnail.png)

### Yeti

![Yeti](http://bootswatch.com/yeti/thumbnail.png)

## Customising a Theme

The [extra_css] and [extra_javascript] configuration options can be used to
make tweaks and customisations to existing themes. To use these, you simply
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

[ReadTheDocs]: ./deploying-your-docs.md#readthedocs
[documentation directory]: /user-guide/configuration/#docs_dir
[extra_css]: /user-guide/configuration.md#extra_css
[extra_javascript]: /user-guide/configuration.md#extra_javascript
