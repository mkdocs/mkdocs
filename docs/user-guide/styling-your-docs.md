# Styling your docs

How to style and theme your documentation.

---

## Built-in themes

#### Bootstrap

![Bootstrap](http://bootstrapdocs.com/v2.3.1/docs/assets/img/examples/bootstrap-example-fluid.png)

#### Read the Docs

![ReadTheDocs](https://docs.readthedocs.org/en/latest/_images/screen_mobile.png)

#### The bootswatch themes

![Amelia](http://bootswatch.com/2/amelia/thumbnail.png)

![Cerulean](http://bootswatch.com/cerulean/thumbnail.png)

![Cosmo](http://bootswatch.com/cosmo/thumbnail.png)

![Cyborg](http://bootswatch.com/cyborg/thumbnail.png)

![Flatly](http://bootswatch.com/flatly/thumbnail.png)

![Journal](http://bootswatch.com/journal/thumbnail.png)

![Readable](http://bootswatch.com/readable/thumbnail.png)

![Simplex](http://bootswatch.com/simplex/thumbnail.png)

![Slate](http://bootswatch.com/slate/thumbnail.png)

![Spacelab](http://bootswatch.com/spacelab/thumbnail.png)

![United](http://bootswatch.com/united/thumbnail.png)

![Yeti](http://bootswatch.com/yeti/thumbnail.png)

## Custom themes

The bare minimum required for a custom theme is a `base.html` template file. This should be placed in a directory at the same level as the `mkdocs.yml` configuration file. Within `mkdocs.yml`, specify the `theme_dir` option and set it to the name of the directory containing `base.html`. For example, given this example project layout:

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

The simplest `base.html` file is the following:

    <!DOCTYPE html>
    <html>
      <head>
      </head>
      <body>
        {{ content }}
      </body>
    </html>

Article content from each page specified in `mkdocs.yml` is inserted using the `{{ content }}` tag. Stylesheets and scripts can be brought into this theme as with a normal HTML file. Navbars and tables of contents can also be generated and included automatically, through the `nav` and `toc` objects, respectively. If you wish to write your own theme, it is recommended to start with one of the [built-in themes](https://github.com/tomchristie/mkdocs/tree/master/mkdocs/themes) and modify it accordingly.
