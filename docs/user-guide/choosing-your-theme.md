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

The default theme, which was built as a custom [Bootstrap] theme, supports almost
every feature of MkDocs.

![mkdocs](../img/mkdocs.png)

In addition to the default [theme configuration options][theme], the `mkdocs` theme
supports the following options:

*   **`highlightjs`**: Enables highlighting of source code in code blocks using
    the [highlight.js] JavaScript library. Default: `True`.

*   **`hljs_style`**: The highlight.js library provides 79 different [styles]
    (color variations) for highlighting source code in code blocks. Set this to
    the name of the desired style. Default: `github`.

*   **`hljs_languages`**: By default, highlight.js only supports 23 common
    languages. List additional languages here to include support for them.

    ```yaml
    theme:
      name: mkdocs
      highlightjs: true
      hljs_languages:
        - yaml
        - rust
    ```

*   **`analytics`**: Defines configuration options for an analytics service.
    Currently, only Google Analytics v4 is supported via the `gtag` option.

    *   **`gtag`**: To enable Google Analytics, set to a Google Analytics v4
    tracking ID, which uses the `G-` format. See Google's documentation to
    [Set up Analytics for a website and/or app (GA4)][setup-GA4] or to
    [Upgrade to a Google Analytics 4 property][upgrade-GA4].

        ```yaml
        theme:
          name: mkdocs
          analytics:
            gtag: G-ABC123
        ```

        When set to the default (`null`) Google Analytics is disabled for the
        site.

*   **`shortcuts`**: Defines keyboard shortcut keys.

    ```yaml
    theme:
      name: mkdocs
      shortcuts:
        help: 191    # ?
        next: 78     # n
        previous: 80 # p
        search: 83   # s
    ```

    All values must be numeric key codes. It is best to use keys that are
    available on all keyboards. You may use <https://keycode.info/> to determine
    the key code for a given key.

    *   **`help`**: Display a help modal that lists the keyboard shortcuts.
        Default: `191` (&quest;)

    *   **`next`**: Navigate to the "next" page. Default: `78` (n)

    *   **`previous`**: Navigate to the "previous" page. Default: `80` (p)

    *   **`search`**: Display the search modal. Default: `83` (s)

*   **`navigation_depth`**: The maximum depth of the navigation tree in the
    sidebar. Default: `2`.

*   **`nav_style`**: This adjusts the visual style for the top navigation bar; by
    default, this is set to `primary` (the default), but it can also be set to
    `dark` or `light`.

    ```yaml
    theme:
      name: mkdocs
      nav_style: dark
    ```

*   **`locale`**{ #mkdocs-locale }: The locale (language/location) used to
    build the theme. If your locale is not yet supported, it will fall back
    to the default.

    The following locales are supported by this theme:

    * `en`: English (default)
    * (see the list of existing directories `mkdocs/themes/mkdocs/locales/*/`)

    See the guide on [localizing your theme] for more information.

## readthedocs

A clone of the default theme used by the [Read the Docs] service, which offers
the same restricted feature set as its parent theme. Like its parent theme, only
two levels of navigation are supported.

![ReadTheDocs](../img/readthedocs.png)

In addition to the default [theme configuration options][theme], the `readthedocs`
theme supports the following options:

*   **`highlightjs`**: Enables highlighting of source code in code blocks using
    the [highlight.js] JavaScript library. Default: `True`.

*   **`hljs_languages`**: By default, highlight.js only supports 23 common
    languages. List additional languages here to include support for them.

    ```yaml
    theme:
      name: readthedocs
      highlightjs: true
      hljs_languages:
        - yaml
        - rust
    ```

*   **`analytics`**: Defines configuration options for an analytics service.

    *   **`gtag`**: To enable Google Analytics, set to a Google Analytics v4
    tracking ID, which uses the `G-` format. See Google's documentation to
    [Set up Analytics for a website and/or app (GA4)][setup-GA4] or to
    [Upgrade to a Google Analytics 4 property][upgrade-GA4].

        ```yaml
        theme:
          name: readthedocs
          analytics:
            gtag: G-ABC123
        ```

        When set to the default (`null`) Google Analytics is disabled for the

    *   **`anonymize_ip`**: To enable anonymous IP address for Google Analytics,
        set this to `True`. Default: `False`.

*   **`include_homepage_in_sidebar`**: Lists the homepage in the sidebar menu. As
    MkDocs requires that the homepage be listed in the `nav` configuration
    option, this setting allows the homepage to be included or excluded from
    the sidebar. Note that the site name/logo always links to the homepage.
    Default: `True`.

*   **`prev_next_buttons_location`**: One of `bottom`, `top`, `both` , or `none`.
    Displays the “Next” and “Previous” buttons accordingly. Default: `bottom`.

*   **`navigation_depth`**: The maximum depth of the navigation tree in the
    sidebar. Default: `4`.

*   **`collapse_navigation`**: Only include the page section headers in the
    sidebar for the current page. Default: `True`.

*   **`titles_only`**: Only include page titles in the sidebar, excluding all
    section headers for all pages. Default: `False`.

*   **`sticky_navigation`**: If True, causes the sidebar to scroll with the main
    page content as you scroll the page. Default: `True`.

*   **`locale`**{ #readthedocs-locale }: The locale (language/location) used to
    build the theme. If your locale is not yet supported, it will fall back
    to the default.

    The following locales are supported by this theme:

    * `en`: English (default)
    * (see the list of existing directories `mkdocs/themes/readthedocs/locales/*/`)

    See the guide on [localizing your theme] for more information.

*   **`logo`**: To set a logo on your project instead of the plain text
    `site_name`, set this variable to be the location of your image. Default: `null`.

## Third Party Themes

A list of third party themes can be found at the [community wiki] page and [the ranked catalog][catalog]. If you have created your own, please add them there.

WARNING: Installing an MkDocs theme means installing a Python package and executing any code that the author has put in there. So, exercise the usual caution; there's no attempt at sandboxing.

[third party themes]: #third-party-themes
[theme]: configuration.md#theme
[Bootstrap]: https://getbootstrap.com/
[highlight.js]: https://highlightjs.org/
[styles]: https://highlightjs.org/static/demo/
[setup-GA4]: https://support.google.com/analytics/answer/9304153?hl=en&ref_topic=9303319
[upgrade-GA4]: https://support.google.com/analytics/answer/9744165?hl=en&ref_topic=9303319
[Read the Docs]: https://readthedocs.org/
[community wiki]: https://github.com/mkdocs/mkdocs/wiki/MkDocs-Themes
[catalog]: https://github.com/mkdocs/catalog#-theming
[localizing your theme]: localizing-your-theme.md
