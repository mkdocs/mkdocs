# Configuration

Guide to all available configuration settings.

---

## Introduction

Project settings are always configured by using a YAML configuration file in the project directory named `mkdocs.yml`.

As a miniumum this configuration file must contain the `site_name` setting.  All other settings are optional.

## Project information

#### site_name

This is a **required setting**, and should be a string that is used as the main title for the project documentation.  For example:

    site_name: Mashmallow Generator

When rendering the theme this setting will be passed as the `site_name` context variable.

#### site_url

Set the canonical URL of the site. This will add a link tag with the canonical URL to the generated HTML header.

**default**: `null`

#### repo_url

When set, provides a link to your GitHub or Bitbucket repository on each page.

    repo_url: https://github.com/example/repository/

**default**: `null`

#### site_description

Set the site description. This will add a meta tag to the generated HTML header.
**default**: `null`

#### site_author 

Set the name of the author. This will add a meta tag to the generated HTML header.

**default**: `null`

#### site_favicon

Set the favicon to use. Putting a `favicon.ico` into the `docs/` directory, the config would look as follows:

```yaml
site_favicon: favicon.ico
```

**default**: `null`

## Documentation layout

#### pages

This is setting is used to determine the set of pages that should be built for the documentation.

The setting should be a list.  Each row in the list represents information about a single page as a list of strings.  The first string represents the path of the documentation source file, and should be relative to the `docs_dir` setting.  Remaining strings represent the title of the page in the site navigation.

Here's a simple example that would cause the build stage to create three pages:

    pages:
    - ['index.md', 'Introduction']
    - ['user-guide.md', 'User Guide']
    - ['about.md', 'About']

Assuming the `docs_dir` setting was left with the default value of `docs`, the source files for this site's build process would be `docs/index.md`, `docs/user-guide.md` and `docs/about.md`.

If you have a lot of project documentation you might choose to use headings to break up your site navigation by category.  You can do so by including an extra string in the page configuration for any pages that require a navigation heading, like so: 

    pages:
    - ['index.md', 'Introduction']
    - ['user-guide/creating.md', 'User Guide', 'Creating a new Mashmallow project']
    - ['user-guide/api.md', 'User Guide', 'Mashmallow API guide']
    - ['user-guide/configuration.md', 'User Guide', 'Configuring Mashmallow']
    - ['about/license.md', 'About', 'License']

## Build directories

#### theme

Sets the theme of your documentation site, for a list of available themes visit
[styling your docs](styling-your-docs.md).

**default**: `'mkdocs'`

#### theme_dir

Lets you set a directory to a custom theme.  This can either be a relative directory, in which case it is resolved relative to the directory containing you configuration file, or it can be an absolute directory path.

For example, given this example project layout:

    mkdocs.yml
    docs/
        index.md
        about.md
    custom_theme/
        base.html
        ...

You would include the following setting to use the custom theme directory:

    theme_dir: 'custom_theme'

If used, then this setting overrides any `theme` configuration value.

**default**: `null`

#### docs_dir

Lets you set the directory containing the documentation source markdown files.  This can either be a relative directory, in which case it is resolved relative to the directory containing you configuration file, or it can be an absolute directory path.

**default**: `'docs'`

#### site_dir

Lets you set the directory where the output HTML and other files are created.  This can either be a relative directory, in which case it is resolved relative to the directory containing you configuration file, or it can be an absolute directory path.

**default**: `'site'`

---

**Note**: If you are using source code control you will normally want to ensure that your *build output* files are not commited into the repository, and only keep the *source* files under version control.  For example, if using `git` you might add the following line to your `.gitignore` file:

    site/

If you're using another source code control you'll want to check its documentation on how to ignore specific directories.

---

<!--
## Extra build steps

#### include_search

Mea et graeci persecuti, sit possit neglegentur ex. Nam modus maluisset id. Praesent laboramus expetendis an vis. Mea scripta eleifend et. Ex zril quidam facilis nec, eu inani errem expetendis eum. Falli electram periculis te ius, sed nihil saperet cu. Possit quodsi cu sea, usu ei saperet lobortis adolescens.

#### include_404

Lorem ipsum dolor sit amet, ex usu velit harum dignissim. Graeco saperet tibique ea mea. Mel vocent veritus assentior ne, ponderum dissentiunt nec eu. No civibus commune duo, nec in mollis regione eruditi, nec feugiat accumsan interesset te. Natum accusam legendos sea no, te eam libris tamquam, ius fabulas vocibus rationibus ad. Eum ex sonet nostrum argumentum, mel persius cotidieque repudiandae in, cum legendos patrioque in.

#### include_sitemap

Consul percipitur usu an, no dico facer inermis cum. Eum ea mentitum accommodare. An sea periculis euripidis, dicant minimum patrioque at vis. Justo atomorum abhorreant vel in. Eos agam intellegam disputando at, zril consul nostrud ut eum.
-->

## Preview controls

#### use_directory_urls

This setting controls the style used for linking to pages within the documentation.

The following table demonstrates how the URLs used on the site differ when setting `use_directory_urls` to `true` or `false`.

Source file  | Generated HTML       | use_directory_urls=true  | use_directory_urls=false
------------ | -------------------- | ------------------------ | ------------------------
index.md     | index.html           | /                        | /index.html
api-guide.md | api-guide/index.html | /api-guide/              | /api-guide/index.html
about.md     | about/index.html     | /about/                  | /about/index.html

The default style of `use_directory_urls=true` creates more user friendly URLs, and is usually what you'll want to use.

The alternate style can occasionally be useful if you want your documentation to remain properly linked when opening pages directly from the file system, because it create links that point directly to the target *file* rather than the target *directory*.

**default**: `true`

#### dev_addr

Determines the address used when running `mkdocs serve`.  Setting this allows you to use another port, or allows you to make the service accessible over your local network by using the `0.0.0.0` address.

As with all settings, you can set this from the command line, which can be usful, for example:

    mkdocs serve --dev-addr=0.0.0.0:80  # Run on port 80, accessible over the local network.

**default**: `'127.0.0.1:8000'`

<!--
## Other configuration

Vel at magna falli fierent. Clita putant nam no, cu per eros possit omnium, dicit pertinacia consetetur at has. Nam quis delenit cu, at vix consul expetendis, mucius mediocrem reprimique te mel. Ex vim quem oratio cotidieque, periculis iracundia at his, his omnium consulatu ei.

No sale minim definiebas vis. An quem utinam eam, est et consul patrioque maiestatis. Vel id decore periculis eloquentiam. Eu vim graeco causae, nec ut dicta graecis delicatissimi. Ne quod etiam salutandi vix, est stet veritus ne. Modus corrumpit usu ea, pri et dicam dignissim, quo ea sumo essent interesset.
-->
