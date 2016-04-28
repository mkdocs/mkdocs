# Styling your docs

How to style and theme your documentation.

---

MkDocs includes a number of different [built-in themes](#built-in-themes) and
[external themes](#bootstrap-and-bootswatch-themes) which can easily be
[customised with extra CSS or JavaScript](#customising-a-theme) or you can
create a [custom theme](/user-guide/custom-themes.md) for your documentation.

To use a theme that is included in MkDocs, simply add this to your
`mkdocs.yml` config file.

    theme: readthedocs

Replace [`readthedocs`](#readthedocs) with any of the [built-in themes](#built-
in-themes) listed below.

To create a new custom theme or more heavily customise an existing theme, see
the [custom themes](#custom-themes) section below.

## Built-in themes

### mkdocs

![mkdocs](/img/mkdocs.png)

### readthedocs

![ReadTheDocs](http://docs.readthedocs.io/en/latest/_images/screen_mobile.png)

### Third Party Themes

Third party themes can be found in the MkDocs [community wiki](
https://github.com/mkdocs/mkdocs/wiki/MkDocs-Themes).

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
