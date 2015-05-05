# Release Notes

---

## Upgrading

To upgrade MkDocs to the latest version, use pip:

    pip install -U mkdocs

You can determine your currently installed version using `mkdocs --version`:

    $ mkdocs --version
    mkdocs, version 0.13.0


## Version 0.13.0 (2015-05-??)

### Deprecations

#### Deprecate the JSON command

In this release the  `mkdocs json` command has been marked as deprecated and
when used a deprecation warning will be shown. It will be removed in a [future
release] of MkDocs, version 1.0 at the latest. The `mkdocs json` command
provided  a convenient way for users to output the documentation contents as
JSON files but with the additions of search to MkDocs this functionality is
duplicated.

A new index with all the contents from a MkDocs build is created in the
[site_dir], so with the default value for the `site_dir` It can be found in
`site/mkdocs/search_index.json`.

This new file is created on every MkDocs build (with `mkdocs build`) and
no configuration is needed to enable it.

[future release]: https://github.com/mkdocs/mkdocs/pull/481
[site_dir]: /user-guide/configuration/#site_dir

### Major Additions

#### Search

Support for search has now been added to MkDocs. This is based on the
JavaScript library [lunr.js]. It has been added to both the `mkdocs` and
`readthedocs` themes. See the custom theme documentation on [supporting search]
for adding it to your own themes.

[lunr.js]: http://lunrjs.com/
[supporting search]: /user-guide/styling-your-docs/#search-and-themes

#### New Command Line Interface

The command line interface for MkDocs has been re-written with the Python
library [Click]. This means that MkDocs now has an easier to use interface
with better help output.

This change is partially backwards incompatible as while undocumented it was
possible to pass any configuration option to the different commands. Now only
a small subset of the configuration options can be passed to the commands. To
see in full commands and available arguments use `mkdocs --help` and
`mkdocs build --help` to have them displayed.

[Click]: http://click.pocoo.org/4/

#### Support Extra HTML and XML files

Like the [extra_javascript] and [extra_css] configuration options, a new
option named [extra_templates] has been added. This will automatically be
populated with any `.html` or `.xml` files in the project docs directory.

Users can place static HTML and XML files and they will be copied over, or they
can also use Jinja2 syntax and take advantage of the [global variables].

By default MkDocs will use this approach to create a sitemap for the
documentation.

[extra_javascript]: /user-guide/configuration/#extra_javascript
[extra_css]: /user-guide/configuration/#extra_css
[extra_templates]: /user-guide/configuration/#extra_templates
[global variables]: /user-guide/styling-your-docs/#global-context

### Other Changes and Additions

* Add support for [Markdown extension configuration options]. (#435)
* MkDocs now ships Python [wheels]. (#486)
* Only include the build date and MkDocs version on the homepage. (#490)
* Generate sitemaps for documentation builds. (#436)
* Automatically take titles from the first H1 on a Makrdown document if they
  are not provided in the config. (#497)

[Markdown extension configuration options]: /user-guide/configuration/#markdown_extensions
[wheels]: http://pythonwheels.com/


## Version 0.12.2 (2015-04-22)

* Bugfix: Fix a regression where there would be an error if some child titles
  were missing but others were provided in the pages config. (#464)


## Version 0.12.1 (2015-04-14)

* Bugfix: Fixed a CSS bug in the table of contents on some browsers where the
  bottom item was not clickable.


## Version 0.12.0 (2015-04-14)

* Display the current MkDocs version in the CLI output. (#258)
* Check for CNAME file when using gh-deploy. (#285)
* Add the homepage back to the navigation on all themes. (#271)
* Add a strict more for local link checking. (#279)
* Add Google analytics support to all themes. (#333)
* Add build date and MkDocs version to the ReadTheDocs and MkDocs theme
  outputs. (#382)
* Standardise highlighting across all themes and add missing languages. (#387)
* Add a verbose flag. (-v) to show more details about what the build. (#147)
* Add the option to specify a remote branch when deploying to GitHub. This
  enables deploying to GitHub pages on personal and repo sites. (#354)
* Add favicon support to the ReadTheDocs theme HTML. (#422)
* Automatically refresh the browser when files are edited. (#163)
* Bugfix: Never re-write URL's in code blocks. (#240)
* Bugfix: Don't copy ditfiles when copying media from the `docs_dir`. (#254)
* Bugfix: Fix the rendering of tables in the ReadTheDocs theme. (#106)
* Bugfix: Add padding to the bottom of all bootstrap themes. (#255)
* Bugfix: Fix issues with nested Markdown pages and the automatic pages
  configuration. (#276)
* Bugfix: Fix a URL parsing error with GitHub enterprise. (#284)
* Bugfix: Don't error if the mkdocs.yml is completely empty. (#288)
* Bugfix: Fix a number of problems with relative urls and Markdown files. (#292)
* Bugfix: Don't stop the build if a page can't be found, continue with other
  pages. (#150)
* Bugfix: Remove the site_name from the page title, this needs to be added
  manually. (#299)
* Bugfix: Fix an issue with table of contents cutting off Markdown. (#294)
* Bugfix: Fix hostname for BitBucket. (#339)
* Bugfix: Ensure all links end with a slash. (#344)
* Bugfix: Fix repo links in the readthedocs theme. (#365)
* Bugfix: Include jQuery locally to avoid problems using MkDocs offline. (#143)
* Bugfix: Don't allow the docs_dir to be in the site_dir or vice versa. (#384)
* Bugfix: Remove inline CSS in the ReadTheDocs theme. (#393)
* Bugfix: Fix problems with the child titles due to the order the pages config
  was processed. (#395)
* Bugfix: Don't error during live reload when the theme doesn't exist. (#373)
* Bugfix: Fix problems with the Meta extension when it may not exist. (#398)
* Bugfix: Wrap long inline code otherwise they will run off the screen. (#313)
* Bugfix: Remove HTML parsing regular expressions and parse with HTMLParser to
  fix problems with titles containing code. (#367)
* Bugfix: Fix an issue with the scroll to anchor causing the title to be hidden
  under the navigation. (#7)
* Bugfix: Add nicer CSS classes to the HTML tables in bootswatch themes. (#295)
* Bugfix: Fix an error when passing in a specific config file with
  `mkdocs serve`. (#341)
* Bugfix: Don't overwrite index.md diles with the `mkdocs new` command. (#412)
* Bugfix: Remove bold and italic from code in the ReadTheDocs theme. (#411)
* Bugfix: Display images inline in the MkDocs theme. (#415)
* Bugfix: Fix problems with no-highlight in the ReadTheDocs theme. (#319)
* Bugfix: Don't delete hidden files when using `mkdocs build --clean`. (#346)
* Bugfix: Don't block newer verions of Python-markdown on Python >= 2.7. (#376)
* Bugfix: Fix encoding issues when opening files across platforms. (#428)


## Version 0.11.1 (2014-11-20)

* Bugfix: Fix a CSS wrapping issue with code highlighting in the ReadTheDocs
  theme. (#233)


## Version 0.11.0 (2014-11-18)

* Render 404.html files if they exist for the current theme. (#194)
* Bugfix: Fix long nav bars, table rendering and code highlighting in MkDocs
  and ReadTheDocs themes. (#225)
* Bugfix: Fix an issue with the google_analytics code. (#219)
* Bugfix: Remove `__pycache__` from the package tar. (#196)
* Bugfix: Fix markdown links that go to an anchor on the current page. (#197)
* Bugfix: Don't add `prettyprint well` CSS classes to all HTML, only add it in
  the MkDocs theme. (#183)
* Bugfix: Display section titles in the ReadTheDocs theme. (#175)
* Bugfix: Use the polling observer in watchdog so rebuilding works on
  filesystems without inotify. (#184)
* Bugfix: Improve error output for common configuration related errors. (#176)


## Version 0.10.0 (2014-10-29)

* Added support for Python 3.3 and 3.4. (#103)
* Configurable Python-Markdown extensions with the config setting
  `markdown_extensions`. (#74)
* Added `mkdocs json` command to output your rendered
  documentation as json files. (#128)
* Added `--clean` switch to `build`, `json` and `gh-deploy` commands to
  remove stale files from the output directory. (#157)
* Support multiple theme directories to allow replacement of
  individual templates rather than copying the full theme. (#129)
* Bugfix: Fix `<ul>` rendering in readthedocs theme. (#171)
* Bugfix: Improve the readthedocs theme on smaller displays. (#168)
* Bugfix: Relaxed required python package versions to avoid clashes. (#104)
* Bugfix: Fix issue rendering the table of contents with some configs. (#146)
* Bugfix: Fix path for embedded images in sub pages. (#138)
* Bugfix: Fix `use_directory_urls` config behaviour. (#63)
* Bugfix: Support `extra_javascript` and `extra_css` in all themes. (#90)
* Bugfix: Fix path-handling under Windows. (#121)
* Bugfix: Fix the menu generation in the readthedocs theme. (#110)
* Bugfix: Fix the mkdocs command creation under Windows. (#122)
* Bugfix: Correctly handle external `extra_javascript` and `extra_css`. (#92)
* Bugfix: Fixed favicon support. (#87)

