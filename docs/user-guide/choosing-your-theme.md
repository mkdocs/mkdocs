# Choosing your Theme

Selecting and configuring a theme.

---

MkDocs includes two built-in themes ([mkdocs](#mkdocs) and
[readthedocs](#readthedocs)), as documented below. However, many [third party
themes] are available to choose from as well.

To choose a theme, set the [theme] configuration option in your `mkdocs.yml`
config file.

```yaml
theme:
    name: readthedocs
```

## mkdocs

The default theme, which was built as a custom [Bootstrap] theme, supports most
every feature of MkDocs.

![mkdocs](../img/mkdocs.png)

In addition to the default [theme configuration options][theme], the `mkdocs` theme
supports the following options:

* __`highlightjs`__: Enables highlighting of source code in code blocks using
  the [highlight.js] JavaScript library. Default: `True`.

* __`hljs_style`__: The highlight.js library provides 79 different [styles]
  (color variations) for highlighting source code in code blocks. Set this to
  the name of the desired style. Default: `github`.

* __`hljs_languages`__: By default, highlight.js only supports 23 common
  languages. List additional languages here to include support for them.

        theme:
            name: mkdocs
            highlightjs: true
            hljs_languages:
                - yaml
                - rust

* __`analytics`__: Defines configuration options for an analytics service.
  Currently, only Google Analytics v4 is supported via the `gtag` option.

    * __`gtag`__: To enable Google Analytics, set to a Google Analytics v4
    tracking ID, which uses the `G-` format. See Google's documentation to
    [Set up Analytics for a website and/or app (GA4)][setup-GA4] or to
    [Upgrade to a Google Analytics 4 property][upgrade-GA4].

            theme:
                name: mkdocs
                analytics:
                    gtag: G-ABC123

        When set to the default (`null`) Google Analytics is disabled for the
        site.

* __`shortcuts`__: Defines keyboard shortcut keys.

        theme:
            name: mkdocs
            shortcuts:
                help: 191    # ?
                next: 78     # n
                previous: 80 # p
                search: 83   # s

    All values must be numeric key codes. It is best to use keys which are
    available on all keyboards. You may use <https://keycode.info/> to determine
    the key code for a given key.

    * __`help`__: Display a help modal which lists the keyboard shortcuts.
      Default: `191` (&quest;)

    * __`next`__: Navigate to the "next" page. Default: `78` (n)

    * __`previous`__: Navigate to the "previous" page. Default: `80` (p)

    * __`search`__: Display the search modal. Default: `83` (s)

* __`navigation_depth`__: The maximum depth of the navigation tree in the
  sidebar. Default: `2`.

* __`nav_style`__: This adjusts the visual style for the top navigation bar; by
  default, this is set to `primary` (the default), but it can also be set to
  `dark` or `light`.

        theme:
            name: mkdocs
            nav_style: dark

* __`locale`__{ #mkdocs-locale }: The locale (language/location) used to
  build the theme. If your locale is not yet supported, it will fallback
  to the default.

    The following locales are supported by this theme:

    * `en`: English (default)
    * `fr`: French
    * `es`: Spanish
    * `ja`: Japanese
    * `pt_BR`: Portuguese (Brazil)
    * `zh_CN`: Simplified Chinese
    * `de`: German

    See the guide on [localizing your theme] for more information.

## readthedocs

A clone of the default theme used by the [Read the Docs] service, which offers
the same restricted feature-set as its parent theme. Like its parent theme, only
two levels of navigation are supported.

![ReadTheDocs](../img/readthedocs.png)

In addition to the default [theme configuration options][theme], the `readthedocs`
theme supports the following options:

* __`highlightjs`__: Enables highlighting of source code in code blocks using
  the [highlight.js] JavaScript library. Default: `True`.

* __`hljs_languages`__: By default, highlight.js only supports 23 common
  languages. List additional languages here to include support for them.

        theme:
            name: readthedocs
            highlightjs: true
            hljs_languages:
                - yaml
                - rust

* __`analytics`__: Defines configuration options for an analytics service.

    * __`gtag`__: To enable Google Analytics, set to a Google Analytics v4
    tracking ID, which uses the `G-` format. See Google's documentation to
    [Set up Analytics for a website and/or app (GA4)][setup-GA4] or to
    [Upgrade to a Google Analytics 4 property][upgrade-GA4].

            theme:
                name: readthedocs
                analytics:
                    gtag: G-ABC123

        When set to the default (`null`) Google Analytics is disabled for the

    * __`anonymize_ip`__: To enable anonymous IP address for Google Analytics,
    set this to `True`. Default: `False`.

* __`include_homepage_in_sidebar`__: Lists the homepage in the sidebar menu. As
  MkDocs requires that the homepage be listed in the `nav` configuration
  option, this setting allows the homepage to be included or excluded from
  the sidebar. Note that the site name/logo always links to the homepage.
  Default: `True`.

* __`prev_next_buttons_location`__: One of `bottom`, `top`, `both` , or `none`.
  Displays the “Next” and “Previous” buttons accordingly. Default: `bottom`.

* __`navigation_depth`__: The maximum depth of the navigation tree in the
  sidebar. Default: `4`.

* __`collapse_navigation`__: Only include the page section headers in the
  sidebar for the current page. Default: `True`.

* __`titles_only`__: Only include page titles in the sidebar, excluding all
  section headers for all pages. Default: `False`.

* __`sticky_navigation`__: If True, causes the sidebar to scroll with the main
  page content as you scroll the page. Default: `True`.

* __`locale`__{ #readthedocs-locale }: The locale (language/location) used to
  build the theme. If your locale is not yet supported, it will fallback
  to the default.

    The following locales are supported by this theme:

    * `en`: English (default)
    * `fr`: French
    * `es`: Spanish
    * `ja`: Japanese
    * `pt_BR`: Portuguese (Brazil)
    * `zh_CN`: Simplified Chinese
    * `de`: German

    See the guide on [localizing your theme] for more information.

* __`logo`__: To set a logo on your project instead of the plain text
  `site_name`, set this variable to be the location of your image. Default: `null`.

## Third Party Themes

A list of third party themes can be found in the MkDocs [community wiki]. If you
have created your own, please feel free to add it to the list.

[third party themes]: #third-party-themes
[theme]: configuration.md#theme
[Bootstrap]: https://getbootstrap.com/
[highlight.js]: https://highlightjs.org/
[styles]: https://highlightjs.org/static/demo/
[setup-GA4]: https://support.google.com/analytics/answer/9304153?hl=en&ref_topic=9303319
[upgrade-GA4]: https://support.google.com/analytics/answer/9744165?hl=en&ref_topic=9303319
[Read the Docs]: https://readthedocs.org/
[community wiki]: https://github.com/mkdocs/mkdocs/wiki/MkDocs-Themes
[localizing your theme]: localizing-your-theme.md
