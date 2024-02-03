# Release Notes

---

## Upgrading

To upgrade MkDocs to the latest version, use pip:

```bash
pip install -U mkdocs
```

You can determine your currently installed version using `mkdocs --version`:

```console
$ mkdocs --version
mkdocs, version 1.5.0 from /path/to/mkdocs (Python 3.10)
```

## Maintenance team

The current and past members of the MkDocs team.

* [@tomchristie](https://github.com/tomchristie/)
* [@d0ugal](https://github.com/d0ugal/)
* [@waylan](https://github.com/waylan/)
* [@oprypin](https://github.com/oprypin/)
* [@ultrabug](https://github.com/ultrabug/)

## Version 1.5.3 (2023-09-18)

*   Fix `mkdocs serve` sometimes locking up all browser tabs when navigating quickly (#3390)

*   Add many new supported languages for "search" plugin - update lunr-languages to 1.12.0 (#3334)

*   Bugfix (regression in 1.5.0): In "readthedocs" theme the styling of "breadcrumb navigation" was broken for nested pages (#3383)

*   Built-in themes now also support Chinese (Traditional, Taiwan) language (#3154)

*   Plugins can now set `File.page` to their own subclass of `Page`. There is also now a warning if `File.page` is set to anything other than a strict subclass of `Page`. (#3367, #3381)

    Note that just instantiating a `Page` [sets the file automatically](https://github.com/mkdocs/mkdocs/blob/f94ab3f62d0416d484d81a0c695c8ca86ab3b975/mkdocs/structure/pages.py#L34), so care needs to be taken not to create an unneeded `Page`.

Other small improvements; see [commit log](https://github.com/mkdocs/mkdocs/compare/1.5.2...1.5.3).

## Version 1.5.2 (2023-08-02)

*   Bugfix (regression in 1.5.0): Restore functionality of `--no-livereload`. (#3320)

*   Bugfix (regression in 1.5.0): The new page title detection would sometimes be unable to drop anchorlinks - fix that. (#3325)

*   Partly bring back pre-1.5 API: `extra_javascript` items will once again be mostly strings, and only sometimes `ExtraScriptValue` (when the extra `script` functionality is used).

    Plugins should be free to append strings to `config.extra_javascript`, but when reading the values, they must still make sure to read it as `str(value)` in case it is an `ExtraScriptValue` item. For querying the attributes such as `.type` you need to check `isinstance` first. Static type checking will guide you in that. (#3324)

See [commit log](https://github.com/mkdocs/mkdocs/compare/1.5.1...1.5.2).

## Version 1.5.1 (2023-07-28)

*   Bugfix (regression in 1.5.0): Make it possible to treat `ExtraScriptValue` as a path. This lets some plugins still work despite the breaking change.

*   Bugfix (regression in 1.5.0): Prevent errors for special setups that have 3 conflicting files, such as `index.html`, `index.md` *and* `README.md` (#3314)

See [commit log](https://github.com/mkdocs/mkdocs/compare/1.5.0...1.5.1).

## Version 1.5.0 (2023-07-26)

### New command `mkdocs get-deps`

This command guesses the Python dependencies that a MkDocs site requires in order to build. It simply prints the PyPI packages that need to be installed. In the terminal it can be combined directly with an installation command as follows:

```bash
pip install $(mkdocs get-deps)
```

The idea is that right after running this command, you can directly follow it up with `mkdocs build` and it will almost always "just work", without needing to think which dependencies to install.

The way it works is by scanning `mkdocs.yml` for `themes:`, `plugins:`, `markdown_extensions:` items and doing a reverse lookup based on a large list of known projects (catalog, see below).

Of course, you're welcome to use a "virtualenv" with such a command. Also note that for environments that require stability (for example CI) directly installing deps in this way is not a very reliable approach as it precludes dependency pinning.

The command allows overriding which config file is used (instead of `mkdocs.yml` in the current directory) as well as which catalog of projects is used (instead of downloading it from the default location). See [`mkdocs get-deps --help`](../user-guide/cli.md#mkdocs-get-deps).

Context: #3205

### MkDocs has an official catalog of plugins

Check out <https://github.com/mkdocs/catalog> and add all your general-purpose plugins, themes and extensions there, so that they can be looked up through `mkdocs get-deps`.

This was renamed from "best-of-mkdocs" and received significant updates. In addition to `pip` installation commands, the page now shows the config boilerplate needed to add a plugin.

### Expanded validation of links

#### Validated links in Markdown

> As you may know, within Markdown, MkDocs really only recognizes **relative** links that lead to another physical `*.md` document (or media file). This is a good convention to follow because then the source pages are also freely browsable without MkDocs, for example on GitHub. MkDocs knows that in the output it should turn those `*.md` links into `*.html` as appropriate, and it would also always tell you if such a link doesn't actually lead to an existing file.

However, the checks for links were really loose and had many concessions. For example, links that started with `/` ("absolute") and links that *ended* with `/` were left as is and no warning was shown, which allowed such very fragile links to sneak into site sources: links that happen to work right now but get no validation and links that confusingly need an extra level of `..` with `use_directory_urls` enabled.

Now, in addition to validating relative links, MkDocs will print `INFO` messages for unrecognized types of links (including absolute links). They look like this:

```text
INFO - Doc file 'example.md' contains an absolute link '/foo/bar/', it was left as is. Did you mean 'foo/bar.md'?
```

If you don't want any changes, not even the `INFO` messages, and wish to revert to the silence from MkDocs 1.4, add the following configs to `mkdocs.yml` (**not** recommended):

```yaml
validation:
  absolute_links: ignore
  unrecognized_links: ignore
```

If, on the opposite end, you want these to print `WARNING` messages and cause `mkdocs build --strict` to fail, you are recommended to configure these to `warn` instead.

See [**documentation**](../user-guide/configuration.md#validation) for actual recommended settings and more details. Context: #3283

#### Validated links in the nav

Links to documents in the [`nav` configuration](../user-guide/configuration.md#nav) now also have configurable validation, though with no changes to the defaults.

You are welcomed to turn on validation for files that were forgotten and excluded from the nav. Example:

```yaml
validation:
  nav:
    omitted_files: warn
    absolute_links: warn
```

This can make the following message appear with the `WARNING` level (as opposed to `INFO` as the only option previously), thus being caught by `mkdocs --strict`:

```text
INFO - The following pages exist in the docs directory, but are not included in the "nav" configuration: ...
```

See [**documentation**](../user-guide/configuration.md#validation). Context: #3283, #1755

#### Mark docs as intentionally "not in nav"

There is a new config `not_in_nav`. With it, you can mark particular patterns of files as exempt from the above `omitted_files` warning type; no messages will be printed for them anymore. (As a corollary, setting this config to `*` is the same as ignoring `omitted_files` altogether.)

This is useful if you generally like these warnings about files that were forgotten from the nav, but still have some pages that you knowingly excluded from the nav and just want to build and copy them.

The `not_in_nav` config is a set of gitignore-like patterns. See the next section for an explanation of another such config.

See [**documentation**](../user-guide/configuration.md#not_in_nav). Context: #3224, #1888

### Excluded doc files

There is a new config `exclude_docs` that tells MkDocs to ignore certain files under `docs_dir` and *not* copy them to the built `site` as part of the build.

Historically MkDocs would always ignore file names starting with a dot, and that's all. Now this is all configurable: you can un-ignore these and/or ignore more patterns of files.

The `exclude_docs` config follows the [.gitignore pattern format](https://git-scm.com/docs/gitignore#_pattern_format) and is specified as a multiline YAML string. For example:

```yaml
exclude_docs: |
  *.py               # Excludes e.g. docs/hooks/foo.py
  /requirements.txt  # Excludes docs/requirements.txt
```

Validation of links (described above) is also affected by `exclude_docs`. During `mkdocs serve` the messages explain the interaction, whereas during `mkdocs build` excluded files are as good as nonexistent.

As an additional related change, if you have a need to have both `README.md` and `index.md` files in a directory but publish only one of them, you can now use this feature to explicitly ignore one of them and avoid warnings.

See [**documentation**](../user-guide/configuration.md#exclude_docs). Context: #3224

#### Drafts

> DANGER: **Dropped from version 1.6:**
>
> The `exclude_docs` config no longer applies the "drafts" functionality for `mkdocs serve`. This was renamed to [`draft_docs`](../user-guide/configuration.md#draft_docs).

The `exclude_docs` config has another behavior: all excluded Markdown pages will still be previewable in `mkdocs serve` only, just with a "DRAFT" marker on top. Then they will of course be excluded from `mkdocs build` or `gh-deploy`.

If you don't want `mkdocs serve` to have any special behaviors and instead want it to perform completely normal builds, use the new flag `mkdocs serve --clean`.

See [**documentation**](../user-guide/configuration.md#exclude_docs). Context: #3224

### `mkdocs serve` no longer exits after build errors

If there was an error (from the config or a plugin) during a site re-build, `mkdocs serve` used to exit after printing a stack trace. Now it will simply freeze the server until the author edits the files to fix the problem, and then will keep reloading.

But errors on the *first* build still cause `mkdocs serve` to exit, as before.

Context: #3255

### Page titles will be deduced from any style of heading

MkDocs always had the ability to infer the title of a page (if it's not specified in the `nav`) based on the first line of the document, if it had a `<h1>` heading that had to written starting with the exact character `#`. Now any style of Markdown heading is understood (#1886). Due to the previous simplistic parsing, it was also impossible to use `attr_list` attributes in that first heading (#3136). Now that is also fixed.

### Markdown extensions can use paths relative to the current document

This is aimed at extensions such as `pymdownx.snippets` or `markdown_include.include`: you can now specify their include paths to be relative to the currently rendered Markdown document, or relative to the `docs_dir`. Any other extension can of course also make use of the new `!relative` YAML tag.

```yaml
markdown_extensions:
  - pymdownx.snippets:
      base_path: !relative
```

See [**documentation**](../user-guide/configuration.md#paths-relative-to-the-current-file-or-site). Context: #2154, #3258

### `<script>` tags can specify `type="module"` and other attributes

In `extra_javascript`, if you use the `.mjs` file extension or explicitly specify a `type: module` key, the script will be added with the `type="module"` attribute. `defer: true` and `async: true` keys are also available.

See [updated **documentation** for `extra_javascript`](../user-guide/configuration.md#extra_javascript).

**At first this is only supported in built-in themes, other themes need to follow up, see below.**

Context: #3237

### Changes for theme developers (action required!)

Using the construct `{% for script in extra_javascript %}` is now fully obsolete because it cannot allow customizing the attributes of the `<script>` tag. It will keep working but blocks some of MkDocs' features.

Instead, you now need to use `config.extra_javascript` (which was already the case for a while) and couple it with the new `script_tag` filter:

```django
    {%- for script in config.extra_javascript %}
      {{ script | script_tag }}
    {%- endfor %}
```

See [**documentation**](../dev-guide/themes.md#picking-up-css-and-javascript-from-the-config).

### Upgrades for plugin developers

*   Breaking change: `config.extra_javascript` is no longer a plain list of strings, but instead a list of `ExtraScriptValue` items. So you can no longer treat the list values as strings. If you want to keep compatibility with old versions, just always reference the items as `str(item)` instead. And you can still append plain strings to the list if you wish. See information about `<script>` tags above. Context: #3237

*   `File` has a new attribute `inclusion`. Its value is calculated from both the `exclude_docs` and `not_in_nav` configs, and implements their behavior. Plugins can read this value or write to it. New `File` instances by default follow whatever the configs say, but plugins can choose to make this decision explicitly, per file.

*   When creating a `File`, one can now set a `dest_uri` directly, rather than having to update it (and other dependent attributes) after creation. [Context](https://github.com/mkdocs/mkdocs/commit/d5af6426c52421f1113f6dcc591de1e01bea48bd)

*   A new config option was added - `DictOfItems`. Similarly to `ListOfItems`, it validates a mapping of config options that all have the same type. Keys are arbitrary but always strings. Context: #3242

*   A new function `get_plugin_logger` was added. In order to opt into a standardized way for plugins to log messages, please use the idiom:

    ```python
    log = mkdocs.plugins.get_plugin_logger(__name__)
    ...
    log.info("Hello, world")
    ```

    Context: #3245

*   `SubConfig` config option can be conveniently subclassed with a particular type of config specified. For example, `class ExtraScript(SubConfig[ExtraScriptValue]):`. To see how this is useful, search for this class in code. [Context](https://github.com/mkdocs/mkdocs/commit/73e503990e3e3504bfe1cb627d41a7e97970687e)

*   Bugfix: `SubConfig` had a bug where paths (from `FilesystemObject` options) were not made relative to the main config file as intended, because `config_file_path` was not properly inherited to it. This is now fixed. Context: #3265

*   `Config` members now have a way to avoid clashing with Python's reserved words. This is achieved by stripping a trailing underscore from each member's name.

    Example of adding an `async` boolean option that can be set by the user as `async: true` and read programmatically as `config.async_`:

    ```python
    class ExampleConfig(Config):
        async_ = Type(bool, default=False)
    ```

    Previously making a config key with a reserved name was impossible with new-style schemas. [Context](https://github.com/mkdocs/mkdocs/commit/1db8e884fa7135a49adf7740add5d875a16a18bc)

*   `Theme` has its attributes properly declared and gained new attributes `theme.locale`, `theme.custom_dir`.

*   Some type annotations were made more precise. For example:

    * The `context` parameter has gained the type `TemplateContext` (`TypedDict`). [Context](https://github.com/mkdocs/mkdocs/commit/0f793b9984c7e6a1d53ce874e7d17b6d27ebf4b2)
    * The classes `Page`, `Section`, `Link` now have a common base class `StructureItem`. [Context](https://github.com/mkdocs/mkdocs/commit/01be507e30b05db0a4c44ef05ba62b2098010653)
    * Some methods stopped accepting `Config` and only accept `MkDocsConfig` as was originally intended. [Context](https://github.com/mkdocs/mkdocs/commit/c459cd24fc0320333f51525e9cf681d4a8370f50)
    * `config.mdx_configs` got a proper type. Context: #3229

### Theme updates

*   Built-in themes mostly stopped relying on `<script defer>`. This may affect some usages of `extra_javascript`, mainly remove the need for custom handling of "has the page fully loaded yet". Context: #3237

*   "mkdocs" theme now has a styling for `>` blockquotes, previously they were not distinguished at all. Context: #3291

*   "readthedocs" theme was updated to v1.2.0 according to upstream, with improved styles for `<kbd>` and breadcrumb navigation. Context: #3058

*   Both built-in themes had their version of highlight.js updated to 11.8.0, and jQuery updated to 3.6.0.

### Bug fixes

#### Relative paths in the nav can traverse above the root

Regression in 1.2 - relative paths in the nav could no longer traverse above the site's root and were truncated to the root. Although such traversal is discouraged and produces a warning, this was a documented behavior. The behavior is now restored.

Context: #2752, #3010

#### MkDocs can accept the config from stdin

This can be used for config overrides on the fly. See updated section at the bottom of [Configuration Inheritance](../user-guide/configuration.md#configuration-inheritance).

The command to use this is `mkdocs build -f -`. In previous versions doing this led to an error.

[Context](https://github.com/mkdocs/mkdocs/commit/d5bb15fa108da86a8e53fb7d84109d8f8d9d6453)

### New command line flags

* `mkdocs --no-color build` disables color output and line wrapping. This option is also available through an environment variable `NO_COLOR=true`. Context: #3282
* `mkdocs build --no-strict` overrides the `strict` config to `false`. Context: #3254
* `mkdocs build -f -` (described directly above).
* `mkdocs serve --clean` (described above).
* `mkdocs serve --dirty` is the new name of `mkdocs serve --dirtyreload`.

### Deprecations

*   `extra_javascript` underwent a change that can break plugins in rare cases, and it requires attention from theme developers. See respective entries above.

*   Python-Markdown was unpinned from `<3.4`. That version is known to remove functionality. If you are affected by those removals, you can still choose to pin the version for yourself: `Markdown <3.4`. Context: #3222, #2892

*   `mkdocs.utils.warning_filter` now shows a warning about being deprecated. It does nothing since MkDocs 1.2. Consider `get_plugin_logger` or just logging under `mkdocs.plugins.*` instead. Context: #3008

*   Accessing the `_vars` attribute of a `Theme` is deprecated - just access the keys directly.

*   Accessing the `user_configs` attribute of a `Config` is deprecated. Note: instead of `config.user_configs[*]['theme']['custom_dir']`, please use the new attribute `config.theme.custom_dir`.

Other small improvements; see [commit log](https://github.com/mkdocs/mkdocs/compare/1.4.3...1.5.0).

## Version 1.4.3 (2023-05-02)

*   Bugfix: for the `hooks` feature, modules no longer fail to load if using some advanced Python features like dataclasses (#3193)

*   Bugfix: Don't create `None` sitemap entries if the page has no populated URL - affects sites that exclude some files from navigation ([`07a297b`](https://github.com/mkdocs/mkdocs/commit/07a297b3b4de4a1b49469b1497ee34039b9f38fa))

*   "readthedocs" theme:
    * Accessibility: add aria labels to Home logo (#3129) and search inputs (#3046)
    * "readthedocs" theme now supports `hljs_style:` config, same as "mkdocs" theme (#3199)

*   Translations:
    * Built-in themes now also support Indonesian language (#3154)
    * Fixed `zh_CN` translation (#3125)
    * `tr_TR` translation becomes just `tr` - usage should remain unaffected (#3195)

See [commit log](https://github.com/mkdocs/mkdocs/compare/1.4.2...1.4.3).

## Version 1.4.2 (2022-11-01)

*   Officially support Python 3.11 (#3020)

    NEW: **Tip:** Simply upgrading to Python 3.11 can cut off 10-15% of your site's build time.

*   Support multiple instances of the same plugin (#3027)

    If a plugin is specified multiple times in the list under the `plugins:` config, that will create 2 (or more) instances of the plugin with their own config each.

    Previously this case was unforeseen and, as such, bugged.

    Now even though this works, by default a warning will appear from MkDocs anyway, unless the plugin adds a class variable `supports_multiple_instances = True`.

*   Bugfix (regression in 1.4.1): Don't error when a plugin puts a plain string into `warnings` (#3016)

*   Bugfix: Relative links will always render with a trailing slash (#3022)

    Previously under `use_directory_urls`, links *from* a sub-page *to* the main index page rendered as e.g. `<a href="../..">` even though in all other cases the links look like `<a href="../../">`. This caused unwanted behavior on some combinations of Web browsers and servers. Now this special-case bug was removed.

*   Built-in "mkdocs" theme now also supports Norwegian language (#3024)

*   Plugin-related warnings look more readable (#3016)

See [commit log](https://github.com/mkdocs/mkdocs/compare/1.4.1...1.4.2).

## Version 1.4.1 (2022-10-15)

*   Support theme-namespaced plugin loading (#2998)

    Plugins' entry points can be named as 'sometheme/someplugin'. That will have the following outcome:

    * If the current theme is 'sometheme', the plugin 'sometheme/someplugin' will always be preferred over 'someplugin'.
    * If the current theme *isn't* 'sometheme', the only way to use this plugin is by specifying `plugins: [sometheme/someplugin]`.

    One can also specify `plugins: ['/someplugin']` instead of `plugins: ['someplugin']` to definitely avoid the theme-namespaced plugin.

*   Bugfix: `mkdocs serve` will work correctly with non-ASCII paths and redirects (#3001)

*   Windows: 'colorama' is now a dependency of MkDocs, to ensure colorful log output (#2987)

*   Plugin-related config options have more reliable validation and error reporting (#2997)

*   Translation sub-commands of `setup.py` were completely dropped. See documentation [[1]](../about/contributing.md#submitting-changes-to-the-builtin-themes) [[2]](../dev-guide/translations.md#updating-the-translation-catalogs) for their new replacements (#2990)

*   The ['mkdocs' package](https://pypi.org/project/mkdocs/#files) (wheel and source) is now produced by Hatch build system and pyproject.toml instead of setup.py (#2988)

Other small improvements; see [commit log](https://github.com/mkdocs/mkdocs/compare/1.4.0...1.4.1).

## Version 1.4.0 (2022-09-27)

### Feature upgrades

#### Hooks (#2978)

The new `hooks:` config allows you to add plugin-like event handlers from local Python files, without needing to set up and install an actual plugin.

See [**documentation**](../user-guide/configuration.md#hooks).

#### `edit_uri` flexibility (#2927)

There is a new `edit_uri_template:` config.  
It works like `edit_uri` but more generally covers ways to construct an edit URL.  
See [**documentation**](../user-guide/configuration.md#edit_uri_template).

Additionally, the `edit_uri` functionality will now fully work even if `repo_url` is omitted (#2928)

### Upgrades for plugin developers

NOTE: This release has big changes to the implementation of plugins and their configs. But, the intention is to have zero breaking changes in all reasonably common use cases. Or at the very least if a code fix is required, there should always be a way to stay compatible with older MkDocs versions. Please report if this release breaks something.

#### Customize event order for plugin event handlers (#2973)

Plugins can now choose to set a priority value for their event handlers. This can override the old behavior where for each event type, the handlers are called in the order that their plugins appear in the [`plugins` config](../user-guide/configuration.md#plugins).

If this is set, events with higher priority are called first. Events without a chosen priority get a default of 0. Events that have the same priority are ordered as they appear in the config.

Recommended priority values: `100` "first", `50` "early", `0` "default", `-50` "late", `-100` "last".  
As different plugins discover more precise relations to each other, the values should be further tweaked.

See [**documentation**](../dev-guide/plugins.md#event-priorities).

#### New events that persist across builds in `mkdocs serve` (#2972)

The new events are `on_startup` and `on_shutdown`. They run at the very beginning and very end of an `mkdocs` invocation.  
`on_startup` also receives information on how `mkdocs` was invoked (e.g. `serve` `--dirtyreload`).

See [**documentation**](../dev-guide/plugins.md#events).

#### Replace `File.src_path` to not deal with backslashes (#2930)

The property `src_path` uses backslashes on Windows, which doesn't make sense as it's a virtual path.  
To not make a breaking change, there's no change to how *this* property is used, but now you should:

* Use **`File.src_uri`** instead of `File.src_path`
* and **`File.dest_uri`** instead of `File.dest_path`.

These consistently use forward slashes, and are now the definitive source that MkDocs itself uses.

See [source code](https://github.com/mkdocs/mkdocs/blob/1.4.0/mkdocs/structure/files.py#L151).

As a related tip: you should also stop using `os.path.*` or `pathlib.Path()` to deal with these paths, and instead use `posixpath.*` or `pathlib.PurePosixPath()`

#### MkDocs is type-annotated, ready for use with [mypy](https://mypy.readthedocs.io/) (#2941, #2970)

##### Type annotations for event handler methods (#2931)

MkDocs' plugin event methods now have type annotations. You might have been adding annotations to events already, but now they will be validated to match the original.

See [source code](https://github.com/mkdocs/mkdocs/blob/1.4.0/mkdocs/plugins.py#L165) and [documentation](../dev-guide/plugins.md#events).

One big update is that now you should annotate method parameters more specifically as `config: defaults.MkDocsConfig` instead of `config: base.Config`. This not only makes it clear that it is the [main config of MkDocs itself](https://github.com/mkdocs/mkdocs/blob/1.4.0/mkdocs/config/defaults.py), but also provides type-safe access through attributes of the object (see next section).

See [source code](https://github.com/mkdocs/mkdocs/blob/1.4.0/mkdocs/config/defaults.py) and [documentation](../dev-guide/plugins.md#on_event_name).

#### Rework ConfigOption schemas as class-based (#2962)

When developing a plugin, the settings that it accepts used to be specified in the `config_scheme` variable on the plugin class.  
This approach is now soft-deprecated, and instead you should specify the config in a sub-class of `base.Config`.

Old example:

```python
from mkdocs import plugins
from mkdocs.config import base, config_options

class MyPlugin(plugins.BasePlugin):
    config_scheme = (
        ('foo', config_options.Type(int)),
        ('bar', config_options.Type(str, default='')),
    )

    def on_page_markdown(self, markdown: str, *, config: base.Config, **kwargs):
        if self.config['foo'] < 5:
            if config['site_url'].startswith('http:'):
                return markdown + self.config['baz']
```

This code snippet actually has many mistakes but it will pass all type checks and silently run and even succeed in some cases.

So, on to the new equivalent example, changed to new-style schema and attribute-based access:  
(Complaints from "mypy" added inline)

```python
from mkdocs import plugins
from mkdocs.config import base, config_options as c

class MyPluginConfig(base.Config):
    foo = c.Optional(c.Type(int))
    bar = c.Type(str, default='')

class MyPlugin(plugins.BasePlugin[MyPluginConfig]):
    def on_page_markdown(self, markdown: str, *, config: defaults.MkDocsConfig, **kwargs):
        if self.config.foo < 5:  # Error, `foo` might be `None`, need to check first.
            if config.site_url.startswith('http:'):  # Error, MkDocs' `site_url` also might be `None`.
                return markdown + self.config.baz  # Error, no such attribute `baz`!
```

This lets you notice the errors from a static type checker before running the code and fix them as such:

```python
class MyPlugin(plugins.BasePlugin[MyPluginConfig]):
    def on_page_markdown(self, markdown: str, *, config: defaults.MkDocsConfig, **kwargs):
        if self.config.foo is not None and self.config.foo < 5:  # OK, `int < int` is valid.
            if (config.site_url or '').startswith('http:'):  # OK, `str.startswith(str)` is valid.
                return markdown + self.config.bar  # OK, `str + str` is valid.
```

See [**documentation**](../dev-guide/plugins.md#config_scheme).

Also notice that we had to explicitly mark the config attribute `foo` as `Optional`.  
The new-style config has all attributes marked as required by default, and specifying `required=False` or `required=True` is not allowed!

##### New: `config_options.Optional` (#2962)

Wrapping something into `Optional` is conceptually similar to "I want the default to be `None`" -- and you *have* to express it like that, because writing `default=None` doesn't actually work.

Breaking change: the method `BaseConfigOption.is_required()` was removed. Use `.required` instead. (#2938)  
And even the `required` property should be mostly unused now.  
For class-based configs, there's a new definition for whether an option is "required":

* It has no default, and
* It is not wrapped into `config_options.Optional`.

##### New: `config_options.ListOfItems` (#2938)

Defines a list of items that each must adhere to the same constraint. Kind of like a validated `Type(list)`

Examples how to express a list of integers (with `from mkdocs.config import config_options as c`):

Description | Code entry
----------- | ----------
Required to specify | `foo = c.ListOfItems(c.Type(int))`
Optional, default is [] | `foo = c.ListOfItems(c.Type(int), default=[])`
Optional, default is None | `foo = c.Optional(c.ListOfItems(c.Type(int)))`

See more [examples in **documentation**](../dev-guide/plugins.md#examples-of-config-definitions).

##### Updated: `config_options.SubConfig` (#2807)

`SubConfig` used to silently ignore all validation of its config options. Now you should pass `validate=True` to it or just use new class-based configs where this became the default.

So, it can be used to validate a nested sub-dict with all keys pre-defined and value types strictly validated.

See [examples in **documentation**](../dev-guide/plugins.md#examples-of-config-definitions).

#### Other changes to config options

`URL`'s default is now `None` instead of `''`. This can still be checked for truthiness in the same way - `if config.some_url:` (#2962)

`FilesystemObject` is no longer abstract and can be used directly, standing for "file or directory" with optional existence checking (#2938)

Bug fixes:

* Fix `SubConfig`, `ConfigItems`, `MarkdownExtensions` to not leak values across different instances (#2916, #2290)
* `SubConfig` raises the correct kind of validation error without a stack trace (#2938)
* Fix dot-separated redirect in `config_options.Deprecated(moved_to)` (#2963)

Tweaked logic for handling `ConfigOption.default` (#2938)

Deprecated config option classes: `ConfigItems` (#2983), `OptionallyRequired` (#2962), `RepoURL` (#2927)

### Theme updates

*   Styles of admonitions in "MkDocs" theme (#2981):
    * Update colors to increase contrast
    * Apply admonition styles also to `<details>` tag, to support Markdown extensions that provide it ([pymdownx.details](https://facelessuser.github.io/pymdown-extensions/extensions/details/), [callouts](https://oprypin.github.io/markdown-callouts/#collapsible-blocks))

*   Built-in themes now also support these languages:
    * Russian (#2976)
    * Turkish (Turkey) (#2946)
    * Ukrainian (#2980)

### Future compatibility

*   `extra_css:` and `extra_javascript:` warn if a backslash `\` is passed to them. (#2930, #2984)

*   Show `DeprecationWarning`s as INFO messages. (#2907)

    If any plugin or extension that you use relies on deprecated functionality of other libraries, it is at risk of breaking in the near future. Plugin developers should address these in a timely manner.

*   Avoid a dependency on `importlib_metadata` starting from Python 3.10 (#2959)

*   Drop support for Python 3.6 (#2948)

#### Incompatible changes to public APIs

*   `mkdocs.utils`:
    * `create_media_urls` and `normalize_url` warn if a backslash `\` is passed to them. (#2930)
    * `is_markdown_file` stops accepting case-insensitive variants such as `.MD`, which is how MkDocs build was already operating. (#2912)
    * Hard-deprecated: `modified_time`, `reduce_list`, `get_html_path`, `get_url_path`, `is_html_file`, `is_template_file`. (#2912)

### Miscellaneous

*   If a plugin adds paths to `watch` in `LiveReloadServer`, it can now `unwatch` them. (#2777)

*   Bugfix (regression in 1.2): Support listening on an IPv6 address in `mkdocs serve`. (#2951)

Other small improvements; see [commit log](https://github.com/mkdocs/mkdocs/compare/1.3.1...1.4.0).

## Version 1.3.1 (2022-07-19)

*   Pin Python-Markdown version to &lt;3.4, thus excluding its latest release that breaks too many external extensions (#2893)

*   When a Markdown extension fails to load, print its name and traceback (#2894)

*   Bugfix for "readthedocs" theme (regression in 1.3.0): add missing space in breadcrumbs (#2810)

*   Bugfix: don't complain when a file "readme.md" (lowercase) exists, it's not recognized otherwise (#2852)

*   Built-in themes now also support these languages:
    * Italian (#2860)

Other small improvements; see [commit log](https://github.com/mkdocs/mkdocs/compare/1.3.0...1.3.1).

## Version 1.3.0 (2022-03-26)

### Feature upgrades

*   ReadTheDocs theme updated from v0.4.1 to v1.0.0 according to upstream (#2585)

    The most notable changes:

    * New option `logo`: Rather than displaying the `site_name` in the title, one can specify a path to an image to display instead.
    * New option `anonymize_ip` for Google Analytics.
    * Dependencies were upgraded: jQuery upgraded to 3.6.0, Modernizr.js dropped, and others.

    See [documentation of config options for the theme](https://www.mkdocs.org/user-guide/choosing-your-theme/#readthedocs)

*   Built-in themes now also support these languages:
    * German (#2633)
    * Persian (Farsi) (#2787)

*   Support custom directories to watch when running `mkdocs serve` (#2642)

    MkDocs by default watches the *docs* directory and the config file. Now there is a way to add more directories to watch for changes, either via the YAML `watch` key or the command line flag `--watch`.

    Normally MkDocs never reaches into any other directories (so this feature shouldn't be necessary), but some plugins and extensions may do so.

    See [documentation](https://www.mkdocs.org/user-guide/configuration/#watch).

*   New `--no-history` option for `gh_deploy` (#2594)

    Allows to discard the history of commits when deploying, and instead replace it with one root commit

### Bug fixes

*   An XSS vulnerability when using the search function in built-in themes was fixed (#2791)

*   Setting the `edit_uri` option no longer erroneously adds a trailing slash to `repo_url` (#2733)

### Miscellaneous

*   Breaking change: the `pages` config option that was deprecated for a very long time now causes an error when used (#2652)

    To fix the error, just change from `pages` to `nav`.

*   Performance optimization: during startup of MkDocs, code and dependencies of other commands will not be imported (#2714)

    The most visible effect of this is that dependencies of `mkdocs serve` will not be imported when `mkdocs build` is used.

*   Recursively validate `nav` (#2680)

    Validation of the nested `nav` structure has been reworked to report errors early and reliably. Some [edge cases](https://github.com/mkdocs/mkdocs/blob/b7272150bbc9bf8f66c878f6517742de3528972b/mkdocs/tests/config/config_options_tests.py#L783) have been declared invalid.

Other small improvements; see [commit log](https://github.com/mkdocs/mkdocs/compare/1.2.3...1.3.0).

## Version 1.2.4 (2022-03-26)

*   Compatibility with Jinja2 3.1.0 (#2800)

    Due to a breaking change in Jinja2, MkDocs would crash with the message
    `AttributeError: module 'jinja2' has no attribute 'contextfilter'`

## Version 1.2.3 (2021-10-12)

*   Built-in themes now also support these languages:
    * Simplified Chinese (#2497)
    * Japanese (#2525)
    * Brazilian Portuguese (#2535)
    * Spanish (#2545, previously #2396)

*   Third-party plugins will take precedence over built-in plugins with the same name (#2591)

*   Bugfix: Fix ability to load translations for some languages: core support (#2565) and search plugin support with fallbacks (#2602)

*   Bugfix (regression in 1.2): Prevent directory traversal in the dev server (#2604)

*   Bugfix (regression in 1.2): Prevent webserver warnings from being treated as a build failure in strict mode (#2607)

*   Bugfix: Correctly print colorful messages in the terminal on Windows (#2606)

*   Bugfix: Python version 3.10 was displayed incorrectly in `--version` (#2618)

Other small improvements; see [commit log](https://github.com/mkdocs/mkdocs/compare/1.2.2...1.2.3).

## Version 1.2.2 (2021-07-18)

*   Bugfix (regression in 1.2): Fix serving files/paths with Unicode characters (#2464)

*   Bugfix (regression in 1.2): Revert livereload file watching to use polling observer (#2477)

    This had to be done to reasonably support usages that span virtual filesystems such as non-native Docker and network mounts.

    This goes back to the polling approach, very similar to that was always used prior, meaning most of the same downsides with latency and CPU usage.

*   Revert from 1.2: Remove the requirement of a `site_url` config and the restriction on `use_directory_urls` (#2490)

*   Bugfix (regression in 1.2): Don't require trailing slash in the URL when serving a directory index in `mkdocs serve` server (#2507)

    Instead of showing a 404 error, detect if it's a directory and redirect to a path with a trailing slash added, like before.

*   Bugfix: Fix `gh_deploy` with config-file in the current directory (#2481)

*   Bugfix: Fix reversed breadcrumbs in "readthedocs" theme (#2179)

*   Allow "mkdocs.yaml" as the file name when '--config' is not passed (#2478)

*   Stop treating ";" as a special character in URLs: urlparse -> urlsplit (#2502)

*   Improve build performance for sites with many pages (partly already done in 1.2) (#2407)

## Version 1.2.1 (2021-06-09)

* Bugfix (regression in 1.2): Ensure 'gh-deploy' always pushes.

## Version 1.2 (2021-06-04)

### Major Additions to Version 1.2

#### Support added for Theme Localization (#2299)

The `mkdocs` and `readthedocs` themes now support language localization using
the `theme.locale` parameter, which defaults to `en` (English). The only other
supported languages in this release are `fr` (French) and `es` (Spanish). For
details on using the provided translations, see the [user
guide](../user-guide/localizing-your-theme.md). Note that translation will not
happen by default. Users must first install the necessary dependencies with
the following command:

```bash
pip install 'mkdocs[i18n]'
```

Translation contributions are welcome and detailed in the [Translation
Guide](../dev-guide/translations.md).

Developers of third party themes may want to review the relevant section of
the [Theme Development
Guide](../dev-guide/themes.md#supporting-theme-localizationtranslation).

Contributors who are updating the templates to the built-in themes should
review the [Contributing
Guide](contributing.md#submitting-changes-to-the-builtin-themes).

The `lang` setting of the `search` plugin now defaults to the language
specified in `theme.locale`.

#### Support added for Environment Variables in the configuration file (#1954)

Environments variables may now be specified in the configuration file with the
`!ENV` tag. The value of the variable will be parsed by the YAML parser and
converted to the appropriate type.

```yaml
somekey: !ENV VAR_NAME
otherkey: !ENV [VAR_NAME, FALLBACK_VAR, 'default value']
```

See [Environment Variables](../user-guide/configuration.md#environment-variables)
in the Configuration documentation for details.

#### Support added for Configuration Inheritance (#2218)

A configuration file may now inherit from a parent configuration file. In the
primary file set the `INHERIT` key to the relative path of the parent file.

```yaml
INHERIT: path/to/base.yml
```

The two files will then be deep merged. See
[Configuration Inheritance](../user-guide/configuration.md#configuration-inheritance)
for details.

#### Update `gh-deploy` command (#2170)

The vendored (and modified) copy of ghp_import has been replaced with a
dependency on the upstream library. As of version 1.0.0, [ghp-import] includes a
Python API which makes it possible to call directly.

MkDocs can now benefit from recent bug fixes and new features, including the following:

* A `.nojekyll` file is automatically included when deploying to GitHub Pages.
* The `--shell` flag is now available, which reportedly works better on Windows.
* Git author and committer environment variables should be respected (#1383).

[ghp-import]: https://github.com/c-w/ghp-import/

#### Rework auto-reload and HTTP server for `mkdocs serve` (#2385)

`mkdocs serve` now uses a new underlying server + file watcher implementation,
based on [http.server] from standard library and [watchdog]. It provides similar
functionality to the previously used [livereload] library (which is now dropped
from dependencies, along with [tornado]).

This makes reloads more responsive and consistent in terms of timing. Multiple
rapid file changes no longer cause the site to repeatedly rebuild (issue #2061).

Almost every aspect of the server is slightly different, but actual visible
changes are minor. The logging outputs are only *similar* to the old ones.
Degradations in behavior are not expected, and should be reported if found.

[http.server]: https://docs.python.org/3/library/http.server.html
[watchdog]: https://pypi.org/project/watchdog/
[livereload]: https://pypi.org/project/livereload/
[tornado]: https://pypi.org/project/tornado/

##### Offset the local site root according to the sub-path of the `site_url` (#2424)

When using `mkdocs serve` and having the `site_url` specified as e.g.
`http://example.org/sub/path/`, now the root of the locally served site
becomes `http://127.0.0.1:8000/sub/path/` and all document paths are offset
accordingly.

#### A `build_error` event was added (#2103)

Plugin developers can now use the `on_build_error` hook
to execute code when an exception is raised while building the site.

See [`on_build_error`](../dev-guide/plugins.md#on_build_error)
in the Plugins documentation for details.

#### Three new exceptions: BuildError PluginError and Abort (#2103)

MkDocs now has tree new exceptions defined in `mkdocs.exceptions`:
`BuildError`, `PluginError`, and `Abort`:

* `PluginError` can be raised from a plugin to stop the build and log an error message *without traceback*.
* `BuildError` should not be used by third-party plugins developers and is reserved for internal use only.
* `Abort` is used internally to abort the build and display an error without a traceback.

See [`Handling errors`](../dev-guide/plugins.md#handling-errors)
in the Plugins documentation for details.

#### Search Indexing Strategy configuration

Users can now specify which strategy they wish to use when indexing
their site for search. A user can select between the following options:

* **full**: Adds page title, section headings, and full page text to the search index.
* **sections**: Adds page titles and section headings only to the search index.
* **titles**: Adds only the page titles to the search index.

See [`Search Indexing`](../user-guide/configuration.md#indexing) in the
configuration documentation for details.

### Backward Incompatible Changes in 1.2

*   The [site_url](../user-guide/configuration.md#site_url) configuration option
    is now **required**. If it is not set, a warning will be issued. In a future
    release an error will be raised (#2189).

    The [use_directory_urls](../user-guide/configuration.md#use_directory_urls)
    configuration option will be forced to `false` if
    [site_url](../user-guide/configuration.md#site_url) is set to an empty
    string. In that case, if `use_directory_urls` is not explicitly set to
    `false`, a warning will be issued (#2189).

    NOTE: This was reverted in release 1.2.2

*   The `google_analytics` configuration option is deprecated as Google appears to
    be phasing it out in favor of its new Google Analytics 4 property. See the
    documentation for your theme for alternatives which can be configured as part
    of your theme configuration. For example, the [mkdocs][mkdocs-theme] and
    [readthedocs][rtd-theme] themes have each added a new `theme.analytics.gtag`
    configuration option which uses the new Google Analytics 4 property. See
    Google's documentation on how to [Upgrade to a Google Analytics 4
    property][ga4]. Then set  `theme.analytics.gtag` to the "G-" ID and delete the
    `google_analytics` configuration option which contains a "UA-" ID. So long
    as the old "UA-" ID and new "G-" ID are properly linked in your Google
    account, and you are using the "G-" ID, the data will be made available in
    both the old and new formats by Google Analytics. See #2252.

*   A theme's files are now excluded from the list of watched files by default
    when using the `--livereload` server. This new default behavior is what most
    users need and provides better performance when editing site content.
    Theme developers can enable the old behavior with the `--watch-theme`
    option. (#2092).

*   The `mkdocs` theme now removes the sidebar when printing a page. This frees
    up horizontal space for better rendering of content like tables (#2193).

*   The `mkdocs.config.DEFAULT_SCHEMA` global variable has been replaced with the
    function `mkdocs.config.defaults.get_schema()`, which ensures that each
    instance of the configuration is unique (#2289).

*   The `mkdocs.utils.warning_filter` is deprecated and now does nothing. Plugins
    should remove any reference to is as it may be deleted in a future release.
    To ensure any warnings get counted, simply log them to the `mkdocs` log (i.e.:
    `mkdocs.plugins.pluginname`).

*   The `on_serve` event (which receives the `server` object and the `builder`
    function) is affected by the server rewrite. `server` is now a
    `mkdocs.livereload.LiveReloadServer` instead of `livereload.server.Server`.
    The typical action that plugins can do with these is to call
    `server.watch(some_dir, builder)`, which basically adds that directory to
    watched directories, causing the site to be rebuilt on file changes. That
    still works, but passing any other function to `watch` is deprecated and shows
    a warning. This 2nd parameter is already optional, and will accept only this
    exact `builder` function just for compatibility.

*   The `python` method of the `plugins.search.prebuild_index` configuration
    option is pending deprecation as of version 1.2. It is expected that in
    version 1.3 it will raise a warning if used and in version 1.4 it will raise
    an error. Users are encouraged to use an alternate method to generate a
    prebuilt index for search.

*   The `lunr` and `lunr[languages]` dependencies are no longer installed by
    default. The dependencies are only needed for the rare user who pre-builds the
    search index and uses the `python` option, which is now pending deprecation.
    If you use this feature, then you will need to manually install `lunr` and
    `lunr[languages]`. A warning is issued if the dependencies are needed but not
    installed.

[mkdocs-theme]: ../user-guide/choosing-your-theme.md#mkdocs
[rtd-theme]: ../user-guide/choosing-your-theme.md#readthedocs
[ga4]: https://support.google.com/analytics/answer/9744165?hl=en

### Other Changes and Additions to Version 1.2

* Bugfix: Properly process navigation child items in `_get_by_type` when filtering for sections (#2203).
* Official support for Python 3.9 has been added and support for Python 3.5 has been dropped.
* Bugfix: Fixes an issue that would result in a partially cut-off navigation item in the ReadTheDocs theme (#2297).
* Structure Files object now has a `remove` method to help plugin developers manipulate the Files tree. The corresponding `src_paths` has become a property to accommodate this possible dynamic behavior. See #2305.
* Updated highlight.js to 10.5.0. See #2313.
* Bugfix: Search plugin now works with Japanese language. See #2178.
* Documentation has been refactored (#1629).
* Restore styling of tables in the `readthedocs` theme (#2028).
* Ensure `site_url` ends with a slash (#1785).
* Correct documentation of `pages` template context variable (#1736).
* The `lunr` dependency has been updated to 0.5.9, and `lunr.js` to the corresponding 2.3.9 version (#2306).
* Color is now used in log messages to identify errors, warnings and debug messages.
* Bugfix: Identify homepage when `use_directory_urls` is `False` (#2362).

## Version 1.1.2 (2020-05-14)

* Bugfix: Normalize IP addresses and change unsupported address error to a warning (#2108).

## Version 1.1.1 (2020-05-12)

* Bugfix: Allow compressed sitemap to be deterministic by supporting the `SOURCE_DATE_EPOCH` environment variable (#2100).
* Bugfix: Use `README.md` as `index.html` even if `use_directory_urls` is false (#2081).
* Bugfix: Ignore links which start with a backslash (#1680).
* Bugfix: Pass `builder` to the `on_serve` event so that it can be passed to `server.watch` by plugins (#1952).
* Bugfix: Use `lunr[languages]==0.5.8` to avoid `nltk` incompatibilities (#2062).
* Bugfix: Ensure wheel is Python 3 only (#2021).
* Bugfix: Clean up `dev_addr` validation and disallow `0.0.0.0` (#2022).
* Add support for `min_search_length` parameter for search plugin (#2014).
* Bugfix: `readthedocs` theme `code` colors (#2027).

## Version 1.1 (2020-02-22)

### Major Additions to Version 1.1

#### Support for Lunr.py as `prebuild_index` engine

Mkdocs now supports pre-building indices using [Lunr.py][lunrpy-docs], a pure
Python implementation of Lunr.js, allowing the user to avoid installing a
NodeJS environment if so desired. For more information please read the
[`prebuild_index` documentation][prebuildindex-docs].

[lunrpy-docs]: http://lunr.readthedocs.io/
[prebuildindex-docs]: ../user-guide/configuration.md#prebuild_index

#### `readthedocs` theme updated with upstream (#588 and #1374)

The `readthedocs` theme now more closely matches the [upstream] Sphinx theme
(version 0.4.1). A number of new theme configuration settings were added which
mirror the upstream configuration options. See the [theme
documentation][rtd-docs] for details.

[upstream]: https://github.com/rtfd/sphinx_rtd_theme/
[rtd-docs]: ../user-guide/choosing-your-theme.md#readthedocs

#### Update `mkdocs` theme to Bootswatch 4.1.3 (#1563)

The `mkdocs` theme now supports all the features of [Bootswatch 4.1].
Additionally, 2 filenames were changed in this update. If you are using a theme
which inherits from the `mkdocs` theme, the theme developer may need to update
these filenames as follows.

```text
css/bootstrap-custom.min.css => css/bootstrap.min.css
js/bootstrap-3.0.3.min.js => js/bootstrap.min.js
```

[Bootswatch 4.1]: https://getbootstrap.com/docs/4.1/getting-started/introduction/

#### Improved configuration support on the command line (#1401)

The `build`, `serve`, and `gh-deploy` subcommands now support flags to control
whether [directory URLs][directory-urls] should be created:
`--use-directory-urls` / `--no-directory-urls`. In addition, the `gh-deploy`
subcommand now supports all the configuration options that `build` and `serve`
do, adding `--strict`, `--theme`, `--theme-dir`, and `--site-dir`.

[directory-urls]: ../user-guide/configuration.md#use_directory_urls

#### Updated lunr-languages support (#1729)

The `lunr-languages` plugin has been updated to 1.4.0, adding support for
Arabic (`ar`) and Vietnamese (`vi`) languages. In addition, the Dutch and
Japanese language codes have been changed to their standard values: `nl` and
`ja`, respectively. The old language codes (`du` and `jp`) remain as aliases but
may be removed in a future version of MkDocs.

### Other Changes and Additions to Version 1.1

* Bugfix: Ensure nested dot files in themes are ignored and document behavior (#1981).
* Update minimum dependency to Markdown 3.2.1.
* Updated minimum dependency to Jinja 2.10.1 to address security concerns (#1780).
* Update to lunr.js 2.3.8 (#1989).
* Add support for Python 3.8.
* Drop support for Python 3.4.
* Drop support for Python 2.7. MkDocs is PY3 only now (#1926).
* Bugfix: Select appropriate asyncio event loop on Windows for Python 3.8+ (#1885).
* Bugfix: Ensure nested index pages do not get identified as the homepage (#1919).
* Bugfix: Properly identify deployment version (#1879).
* Bugfix: Properly build `ValidationError` message for `custom_dir` (#1849).
* Bugfix: Exclude Markdown files and READMEs from theme (#1766).
* Bugfix: Account for encoded URLs (#1670).
* Bugfix: Ensure theme files do not override `docs_dir` files (#1671).
* Bugfix: Do not normalize URL fragments (#1655).
* Bugfix: Skip external URLs in sitemap.xml (#1742).
* Bugfix: Ensure theme files do not override docs_dir files on Windows (#1876)
* Add canonical tag to `readthedocs` theme (#1669).
* Improved error message for when `git` is not available.
* Add support for `nav_style` theme option for the `mkdocs` theme (#1930).
* Bugfix: Long/nested dropdowns now behave more consistently for the `mkdocs` theme (#1234).
* Bugfix: Multi-row nav headers in the `mkdocs` theme no longer obscure the document content (#716).
* Add support for `navigation_depth` theme option for the `mkdocs` theme (#1970).
* `level` attribute in `page.toc` items is now 1-indexed to match the level in `<hN>` tags (#1970).

## Version 1.0.4 (2018-09-07)

* Bugfix: Ignore absolute links in Markdown (#1621).

## Version 1.0.3 (2018-08-29)

* Bugfix: Warn on relative paths in navigation (#1604).
* Bugfix: Handle empty `theme_config.yml` files correctly (#1602).

## Version 1.0.2 (2018-08-22)

* Bugfix: Provide absolute `base_url` to error templates (#1598).

## Version 1.0.1 (2018-08-13)

* Bugfix: Prevent page reload when [Enter] is pressed in search box (#1589).
* Bugfix: Avoid calling `search` until all assets are ready (#1584).
* Bugfix: Exclude `README.md` if `index.md` is present (#1580).
* Bugfix: Fix `readthedocs` theme navigation bug with homepage (#1576).

## Version 1.0 (2018-08-03)

### Major Additions to Version 1.0

#### Internal Refactor of Pages, Files, and Navigation

Internal handling of pages, files and navigation has been completely refactored.
The changes included in the refactor are summarized below.

*   Support for hidden pages. All Markdown pages are now included in the build
    regardless of whether they are included in the navigation configuration
    (#699).
*   The navigation can now include links to external sites (#989 #1373 & #1406).
*   Page data (including titles) is properly determined for all pages before any
    page is rendered (#1347).
*   Automatically populated navigation now sorts index pages to the top. In other
    words, The index page will be listed as the first child of a directory, while
    all other documents are sorted alphanumerically by file name after the index
    page (#73 & #1042).
*   A `README.md` file is now treated as an index file within a directory and
    will be rendered to `index.html` (#608).
*   The URLs for all files are computed once and stored in a files collection.
    This ensures all internal links are always computed correctly regardless of
    the configuration. This also allows all internal links to be validated, not
    just links to other Markdown pages. (#842 & #872).
*   A new [url] template filter smartly ensures all URLs are relative to the
    current page (#1526).
*   An [on_files] plugin event has been added, which could be used to include
    files not in the `docs_dir`, exclude files, redefine page URLs (i.e.
    implement extensionless URLs), or to manipulate files in various other ways.

[on_files]: ../dev-guide/plugins.md#on_files

##### Backward Incompatible Changes

As part of the internal refactor, a number of backward incompatible changes have
been introduced, which are summarized below.

###### URLs have changed when `use_directory_urls` is `False`

Previously, all Markdown pages would be have their filenames altered to be index
pages regardless of how the [use_directory_urls] setting was configured.
However, the path munging is only needed when `use_directory_urls` is set to
`True` (the default). The path mangling no longer happens when
`use_directory_urls` is set to `False`, which will result in different URLs for
all pages that were not already index files. As this behavior only effects a
non-default configuration, and the most common user-case for setting the option
to `False` is for local file system (`file://`) browsing, its not likely to
effect most users. However, if you have `use_directory_urls` set to `False`
for a MkDocs site hosted on a web server, most of your URLs will now be broken.
As you can see below, the new URLs are much more sensible.

Markdown file   | Old URL              | New URL
--------------- | -------------------- | --------------
`index.md`      | `index.html`         | `index.html`
`foo.md`        | `foo/index.html`     | `foo.html`
`foo/bar.md`    | `foo/bar/index.html` | `foo/bar.html`

Note that there has been no change to URLs or file paths when
`use_directory_urls` is set to `True` (the default), except that MkDocs more
consistently includes an ending slash on all internally generated URLs.

[use_directory_urls]: ../user-guide/configuration.md#use_directory_urls

###### The `pages` configuration setting has been renamed to `nav`

The `pages` configuration setting is deprecated and will issue a warning if set
in the configuration file. The setting has been renamed `nav`. To update your
configuration, simply rename the setting to `nav`. In other words, if your
configuration looked like this:

```yaml
pages:
  - Home: index.md
  - User Guide: user-guide.md
```

Simply edit the configuration as follows:

```yaml
nav:
  - Home: index.md
  - User Guide: user-guide.md
```

In the current release, any configuration which includes a `pages` setting, but
no `nav` setting, the `pages` configuration will be copied to `nav` and a
warning will be issued. However, in a future release, that may no longer happen.
If both `pages` and `nav` are defined, the `pages` setting will be ignored.

###### Template variables and `base_url`

In previous versions of MkDocs some URLs expected the [base_url] template
variable to be prepended to the URL and others did not. That inconsistency has
been removed in that no URLs are modified before being added to the template
context.

For example, a theme template might have previously included a link to
the `site_name` as:

```django
<a href="{{ nav.homepage.url }}">{{ config.site_name }}</a>
```

And MkDocs would magically return a URL for the homepage which was relative to
the current page. That "magic" has been removed and the [url] template filter
should be used:

```django
<a href="{{ nav.homepage.url|url }}">{{ config.site_name }}</a>
```

This change applies to any navigation items and pages, as well as the
`page.next_page` and `page.previous_page` attributes. For the time being, the
`extra_javascript` and `extra_css` variables continue to work as previously
(without the `url` template filter), but they have been deprecated and the
corresponding configuration values (`config.extra_javascript` and
`config.extra_css` respectively) should be used with the filter instead.

```django
{% for path in config.extra_css %}
    <link href="{{ path|url }}" rel="stylesheet">
{% endfor %}
```

Note that navigation can now include links to external sites. Obviously, the
`base_url` should not be prepended to these items. However, the `url` template
filter is smart enough to recognize the URL is absolute and does not alter it.
Therefore, all navigation items can be passed to the filter and only those that
need to will be altered.

```django
{% for nav_item in nav %}
    <a href="{{ nav_item.url|url }}">{{ nav_item.title }}</a>
{% endfor %}
```

[base_url]: ../dev-guide/themes.md#base_url
[url]: ../dev-guide/themes.md#url

#### Path Based Settings are Relative to Configuration File (#543)

Previously any relative paths in the various configuration options were
resolved relative to the current working directory. They are now resolved
relative to the configuration file. As the documentation has always encouraged
running the various MkDocs commands from the directory that contains the
configuration file (project root), this change will not affect most users.
However, it will make it much easier to implement automated builds or otherwise
run commands from a location other than the project root.

Simply use the `-f/--config-file` option and point it at the configuration file:

```sh
mkdocs build --config-file /path/to/my/config/file.yml
```

As previously, if no file is specified, MkDocs looks for a file named
`mkdocs.yml` in the current working directory.

#### Added support for YAML Meta-Data (#1542)

Previously, MkDocs only supported MultiMarkdown style meta-data, which does not
recognize different data types and is rather limited. MkDocs now also supports
YAML style meta-data in Markdown documents. MkDocs relies on the the presence or
absence of the deliminators (`---` or `...`) to determine whether YAML style
meta-data or MultiMarkdown style meta-data is being used.

Previously MkDocs would recognize MultiMarkdown style meta-data between the
deliminators. Now, if the deliminators are detected, but the content between the
deliminators is not valid YAML meta-data, MkDocs does not attempt to parse the
content as MultiMarkdown style meta-data. Therefore, MultiMarkdown's style
meta-data must not include the deliminators. See the [MultiMarkdown style
meta-data documentation] for details.

Prior to version 0.17, MkDocs returned all meta-data values as a list of strings
(even a single line would return a list of one string). In version 0.17, that
behavior was changed to return each value as a single string (multiple lines
were joined), which some users found limiting (see #1471). That behavior
continues for MultiMarkdown style meta-data in the current version. However,
YAML style meta-data supports the full range of "safe" YAML data types.
Therefore, it is recommended that any complex meta-data make use of the YAML
style (see the [YAML style meta-data documentation] for details). In fact, a
future version of MkDocs may deprecate support for MultiMarkdown style
meta-data.

[MultiMarkdown style meta-data documentation]: ../user-guide/writing-your-docs.md#multimarkdown-style-meta-data
[YAML style meta-data documentation]: ../user-guide/writing-your-docs.md#yaml-style-meta-data

#### Refactor Search Plugin

The search plugin has been completely refactored to include support for the
following features:

* Use a web worker in the browser with a fallback (#1396).
* Optionally pre-build search index locally (#859 & #1061).
* Upgrade to lunr.js 2.x (#1319).
* Support search in languages other than English (#826).
* Allow the user to define the word separators (#867).
* Only run searches for queries of length > 2 (#1127).
* Remove dependency on require.js (#1218).
* Compress the search index (#1128).

Users can review the [configuration options][search config] available and theme
authors should review how [search and themes] interact.

[search config]: ../user-guide/configuration.md#search
[search and themes]: ../dev-guide/themes.md#search-and-themes

#### `theme_dir` Configuration Option fully Deprecated

As of version 0.17, the [custom_dir] option replaced the deprecated `theme_dir`
option. If users had set the `theme_dir` option, MkDocs version 0.17 copied the
value to the `theme.custom_dir` option and a warning was issued. As of version
1.0, the value is no longer copied and an error is raised.

### Other Changes and Additions to Version 1.0

* Keyboard shortcuts changed to not conflict with commonly used accessibility shortcuts (#1502.)
* User friendly YAML parse errors (#1543).
* Officially support Python 3.7.
* A missing theme configuration file now raises an error.
* Empty `extra_css` and `extra_javascript` settings no longer raise a warning.
* Add highlight.js configuration settings to built-in themes (#1284).
* Close search modal when result is selected (#1527).
* Add a level attribute to AnchorLinks (#1272).
* Add MkDocs version check to gh-deploy script (#640).
* Improve Markdown extension error messages. (#782).
* Drop official support for Python 3.3 and set `tornado>=5.0` (#1427).
* Add support for GitLab edit links (#1435).
* Link to GitHub issues from release notes (#644).
* Expand {sha} and {version} in gh-deploy commit message (#1410).
* Compress `sitemap.xml` (#1130).
* Defer loading JS scripts (#1380).
* Add a title attribute to the search input (#1379).
* Update RespondJS to latest version (#1398).
* Always load Google Analytics over HTTPS (#1397).
* Improve scrolling frame rate (#1394).
* Provide more version info. (#1393).
* Refactor `writing-your-docs.md` (#1392).
* Workaround Safari bug when zooming to &lt; 100% (#1389).
* Remove addition of `clicky` class to body and animations. (#1387).
* Prevent search plugin from re-injecting `extra_javascript` files (#1388).
* Refactor `copy_media_files` util function for more flexibility (#1370).
* Remove PyPI Deployment Docs (#1360).
* Update links to Python-Markdown library (#1360).
* Document how to generate manpages for MkDocs commands (#686).

## Version 0.17.5 (2018-07-06)

* Bugfix: Fix Python 3.7 and PEP 479 incompatibility (#1518).

## Version 0.17.4 (2018-06-08)

* Bugfix: Add multi-level nesting support to sitemap.xml (#1482).

## Version 0.17.3 (2018-03-07)

* Bugfix: Set dependency `tornado>=4.1,<5.0` due to changes in 5.0 (#1428).

## Version 0.17.2 (2017-11-15)

* Bugfix: Correct `extra_*` config setting regressions (#1335 & #1336).

## Version 0.17.1 (2017-10-30)

* Bugfix: Support `repo_url` with missing ending slash. (#1321).
* Bugfix: Add length support to `mkdocs.toc.TableOfContext` (#1325).
* Bugfix: Add some theme specific settings to the search plugin for third party themes (#1316).
* Bugfix: Override `site_url` with `dev_addr` on local server (#1317).

## Version 0.17.0 (2017-10-19)

### Major Additions to Version 0.17.0

#### Plugin API. (#206)

A new [Plugin API] has been added to MkDocs which allows users to define their
own custom behaviors. See the included documentation for a full explanation of
the API.

The previously built-in search functionality has been removed and wrapped in a
plugin (named "search") with no changes in behavior. When MkDocs builds, the
search index is now written to `search/search_index.json` instead of
`mkdocs/search_index.json`. If no plugins setting is defined in the config,
then the `search` plugin will be included by default. See the
[configuration][plugin_config] documentation for information on overriding the
default.

[Plugin API]: ../dev-guide/plugins.md
[plugin_config]: ../user-guide/configuration.md#plugins

#### Theme Customization. (#1164)

Support had been added to provide theme specific customizations. Theme authors
can define default options as documented in [Theme Configuration]. A theme can
now inherit from another theme, define various static templates to be rendered,
and define arbitrary default variables to control behavior in the templates.
The theme configuration is defined in a configuration file named
`mkdocs_theme.yml` which should be placed at the root of your template files. A
warning will be raised if no configuration file is found and an error will be
raised in a future release.

Users can override those defaults under the [theme] configuration option of
their `mkdocs.yml` configuration file, which now accepts nested options. One
such nested option is the [custom_dir] option, which replaces the now deprecated
`theme_dir` option. If users had previously set the `theme_dir` option, a
warning will be issued, with an error expected in a future release.

If a configuration previously defined a `theme_dir` like this:

```yaml
theme: mkdocs
theme_dir: custom
```

Then the configuration should be adjusted as follows:

```yaml
theme:
  name: mkdocs
  custom_dir: custom
```

See the [theme] configuration option documentation for details.

[Theme Configuration]: ../dev-guide/themes.md#theme-configuration
[theme]: ../user-guide/configuration.md#theme
[custom_dir]: ../user-guide/configuration.md#custom_dir

#### Previously deprecated Template variables removed. (#1168)

##### Page Template

The primary entry point for page templates has been changed from `base.html` to
`main.html`. This allows `base.html` to continue to exist while allowing users
to override `main.html` and extend `base.html`. For version 0.16, `base.html`
continued to work if no `main.html` template existed, but it raised a
deprecation warning. In version 1.0, a build will fail if no `main.html`
template exists.

##### Context Variables

Page specific variable names in the template context have been refactored as
defined in [Custom Themes](../dev-guide/themes.md#page). The
old variable names issued a warning in version 0.16, but have been removed in
version 1.0.

Any of the following old page variables should be updated to the new ones in
user created and third-party templates:

Old Variable Name | New Variable Name
----------------- | -----------------
current_page      | [page]
page_title        | page.title
content           | page.content
toc               | page.toc
meta              | page.meta
canonical_url     | page.canonical_url
previous_page     | page.previous_page
next_page         | page.next_page

[page]: ../dev-guide/themes.md#page

Additionally, a number of global variables have been altered and/or removed
and user created and third-party templates should be updated as outlined below:

Old Variable Name | New Variable Name or Expression
----------------- | --------------------------------------
current_page      | page
include_nav       | nav&#124;length&gt;1
include_next_prev | (page.next_page or page.previous_page)
site_name         | config.site_name
site_author       | config.site_author
page_description  | config.site_description
repo_url          | config.repo_url
repo_name         | config.repo_name
site_url          | config.site_url
copyright         | config.copyright
google_analytics  | config.google_analytics
homepage_url      | nav.homepage.url
favicon           | {{ base_url }}/img/favicon.ico

#### Auto-Populated extra_css and extra_javascript Fully Deprecated. (#986)

In previous versions of MkDocs, if the `extra_css` or `extra_javascript` config
settings were empty, MkDocs would scan the `docs_dir` and auto-populate each
setting with all of the CSS and JavaScript files found. On version 0.16 this
behavior was deprecated and a warning was issued. In 0.17 any unlisted CSS and
JavaScript files will not be included in the HTML templates, however, a warning
will be issued. In other words, they will still be copied to the `site-dir`, but
they will not have any effect on the theme if they are not explicitly listed.

All CSS and JavaScript files in the `docs_dir` should be explicitly listed in
the `extra_css` or `extra_javascript` config settings going forward.

### Other Changes and Additions to Version 0.17.0

* Add "edit Link" support to MkDocs theme (#1129)
* Open files with `utf-8-sig` to account for BOM (#1186)
* Symbolic links are now followed consistently (#1134)
* Support for keyboard navigation shortcuts added to included themes (#1095)
* Some refactoring and improvements to config_options (#1296)
* Officially added support for Python 3.6 (#1296)
* 404 Error page added to readthedocs theme (#1296))
* Internal refactor of Markdown processing (#713)
* Removed special error message for mkdocs-bootstrap and mkdocs-bootswatch themes (#1168)
* The legacy pages config is no longer supported (#1168)
* The deprecated `json` command has been removed (#481)
* Support for Python 2.6 has been dropped (#165)
* File permissions are no longer copied during build (#1292)
* Support query and fragment strings in `edit_uri` (#1224 & #1273)

## Version 0.16.3 (2017-04-04)

* Fix error raised by autoscrolling in the readthedocs theme (#1177)
* Fix a few documentation typos (#1181 & #1185)
* Fix a regression to livereload server introduced in 0.16.2 (#1174)

## Version 0.16.2 (2017-03-13)

* System root (`/`) is not a valid path for site_dir or docs_dir (#1161)
* Refactor readthedocs theme navigation (#1155 & #1156)
* Add support to dev server to serve custom error pages (#1040)
* Ensure nav.homepage.url is not blank on error pages (#1131)
* Increase livereload dependency to 2.5.1 (#1106)

## Version 0.16.1 (2016-12-22)

* Ensure scrollspy behavior does not affect nav bar (#1094)
* Only "load" a theme when it is explicitly requested by the user (#1105)

## Version 0.16 (2016-11-04)

### Major Additions to Version 0.16.0

#### Template variables refactored. (#874)

##### Page Context

Page specific variable names in the template context have been refactored as
defined in [Custom Themes](../dev-guide/themes.md#page). The
old variable names will issue a warning but continue to work for version 0.16,
but may be removed in a future version.

Any of the following old page variables should be updated to the new ones in
user created and third-party templates:

Old Variable Name | New Variable Name
----------------- | ------------------
current_page      | [page]
page_title        | page.title
content           | page.content
toc               | page.toc
meta              | page.meta
canonical_url     | page.canonical_url
previous_page     | page.previous_page
next_page         | page.next_page

##### Global Context

Additionally, a number of global variables have been altered and/or deprecated
and user created and third-party templates should be updated as outlined below:

Previously, the global variable `include_nav` was altered programmatically based
on the number of pages in the nav. The variable will issue a warning but
continue to work for version 0.16, but may be removed in a future version. Use
`{% if nav|length>1 %}` instead.

Previously, the global variable `include_next_prev` was altered programmatically
based on the number of pages in the nav. The variable will issue a warning but
continue to work for version 0.16, but may be removed in a future version. Use
`{% if page.next_page or page.previous_page %}` instead.

Previously the global variable `page_description` was altered programmatically
based on whether the current page was the homepage. Now it simply maps to
`config['site_description']`. Use `{% if page.is_homepage %}` in the template to
conditionally change the description.

The global variable `homepage_url` maps directly to `nav.homepage.url` and is
being deprecated. The variable will issue a warning but continue to work for
version 0.16, but may be removed in a future version. Use `nav.homepage.url`
instead.

The global variable `favicon` maps to the configuration setting `site_favicon`.
Both the template variable and the configuration setting are being deprecated
and will issue a warning but continue to work for version 0.16, and may be
removed in a future version. Use `{{ base_url }}/img/favicon.ico` in your
template instead. Users can simply save a copy of their custom favicon icon to
`img/favicon.ico` in either their `docs_dir` or `theme_dir`.

A number of variables map directly to similarly named variables in the `config`.
Those variables are being deprecated and will issue a warning but continue to
work for version 0.16, but may be removed in a future version. Use
`config.var_name` instead, where `var_name` is the name of one of the
[configuration] variables.

[configuration]: ../user-guide/configuration.md

Below is a summary of all of the changes made to the global context:

Old Variable Name | New Variable Name or Expression
----------------- | --------------------------------------
current_page      | page
include_nav       | nav&#124;length&gt;1
include_next_prev | (page.next_page or page.previous_page)
site_name         | config.site_name
site_author       | config.site_author
page_description  | config.site_description
repo_url          | config.repo_url
repo_name         | config.repo_name
site_url          | config.site_url
copyright         | config.copyright
google_analytics  | config.google_analytics
homepage_url      | nav.homepage.url
favicon           | {{ base_url }}/img/favicon.ico

#### Increased Template Customization. (#607)

The built-in themes have been updated by having each of their many parts wrapped
in template blocks which allow each individual block to be easily overridden
using the `theme_dir` config setting. Without any new settings, you can use a
different analytics service, replace the default search function, or alter the
behavior of the navigation, among other things. See the relevant
[documentation][blocks] for more details.

To enable this feature, the primary entry point for page templates has been
changed from `base.html` to `main.html`. This allows `base.html` to continue to
exist while allowing users to override `main.html` and extend `base.html`. For
version 0.16, `base.html` will continue to work if no `main.html` template
exists, but it is deprecated and will raise a warning. In version 1.0, a build
will fail if no `main.html` template exists. Any custom and third party
templates should be updated accordingly.

The easiest way for a third party theme to be updated would be to simply add a
`main.html` file which only contains the following line:

```django
{% extends "base.html" %}
```

That way, the theme contains the `main.html` entry point, and also supports
overriding blocks in the same manner as the built-in themes. Third party themes
are encouraged to wrap the various pieces of their templates in blocks in order
to support such customization.

[blocks]: ../user-guide/customizing-your-theme.md#overriding-template-blocks

#### Auto-Populated `extra_css` and `extra_javascript` Deprecated. (#986)

In previous versions of MkDocs, if the `extra_css` or `extra_javascript` config
settings were empty, MkDocs would scan the `docs_dir` and auto-populate each
setting with all of the CSS and JavaScript files found. This behavior is
deprecated and a warning will be issued. In the next release, the auto-populate
feature will stop working and any unlisted CSS and JavaScript files will not be
included in the HTML templates. In other words, they will still be copied to the
`site-dir`, but they will not have any effect on the theme if they are not
explicitly listed.

All CSS and JavaScript files in the `docs_dir` should be explicitly listed in
the `extra_css` or `extra_javascript` config settings going forward.

#### Support for dirty builds. (#990)

For large sites the build time required to create the pages can become problematic,
thus a "dirty" build mode was created. This mode simply compares the modified time
of the generated HTML and source markdown. If the markdown has changed since the
HTML then the page is re-constructed. Otherwise, the page remains as is. This mode
may be invoked in both the `mkdocs serve` and `mkdocs build` commands:

```text
mkdocs serve --dirtyreload
```

```text
mkdocs build --dirty
```

It is important to note that this method for building the pages is for development
of content only, since the navigation and other links do not get updated on other
pages.

#### Stricter Directory Validation

Previously, a warning was issued if the `site_dir` was a child directory of the
`docs_dir`. This now raises an error. Additionally, an error is now raised if
the `docs_dir` is set to the directory which contains your config file rather
than a child directory. You will need to rearrange you directory structure to
better conform with the documented [layout].

[layout]: ../user-guide/writing-your-docs.md#file-layout

### Other Changes and Additions to Version 0.16.0

* Bugfix: Support `gh-deploy` command on Windows with Python 3 (#722)
* Bugfix: Include .woff2 font files in Python package build (#894)
* Various updates and improvements to Documentation Home Page/Tutorial (#870)
* Bugfix: Support livereload for config file changes (#735)
* Bugfix: Non-media template files are no longer copied with media files (#807)
* Add a flag (-e/--theme-dir) to specify theme directory with the commands `mkdocs build` and `mkdocs serve` (#832)
* Fixed issues with Unicode file names under Windows and Python 2. (#833)
* Improved the styling of in-line code in the MkDocs theme. (#718)
* Bugfix: convert variables to JSON when being passed to JavaScript (#850)
* Updated the ReadTheDocs theme to match the upstream font sizes and colors more closely. (#857)
* Fixes an issue with permalink markers showing when the mouse was far above them (#843)
* Bugfix: Handle periods in directory name when automatically creating the pages config. (#728)
* Update searching to Lunr 0.7, which comes with some performance enhancements for larger documents (#859)
* Bugfix: Support SOURCE_DATE_EPOCH environment variable for "reproducible" builds (#938)
* Follow links when copying media files (#869).
* Change "Edit on..." links to point directly to the file in the source repository, rather than to the root of the repository (#975), configurable via the new [`edit_uri`](../user-guide/configuration.md#edit_uri) setting.
* Bugfix: Don't override config value for strict mode if not specified on CLI (#738).
* Add a `--force` flag to the `gh-deploy` command to force the push to the repository (#973).
* Improve alignment for current selected menu item in readthedocs theme (#888).
* `http://user.github.io/repo` => `https://user.github.io/repo/` (#1029).
* Improve installation instructions (#1028).
* Account for wide tables and consistently wrap inline code spans (#834).
* Bugfix: Use absolute URLs in nav & media links from error templates (#77).

## Version 0.15.3 (2016-02-18)

* Improve the error message the given theme can't be found.
* Fix an issue with relative symlinks (#639)

## Version 0.15.2 (2016-02-08)

* Fix an incorrect warning that states external themes [will be removed from MkDocs](#add-support-for-installable-themes).

## Version 0.15.1 (2016-01-30)

* Lower the minimum supported Click version to 3.3 for package maintainers. (#763)

## Version 0.15.0 (2016-01-21)

### Major Additions to Version 0.15.0

#### Add support for installable themes

MkDocs now supports themes that are distributed via Python packages. With this
addition, the Bootstrap and Bootswatch themes have been moved to external git
repositories and python packages. See their individual documentation for more
details about these specific themes.

* [MkDocs Bootstrap]
* [MkDocs Bootswatch]

[MkDocs Bootstrap]: https://mkdocs.github.io/mkdocs-bootstrap/
[MkDocs Bootswatch]: https://mkdocs.github.io/mkdocs-bootswatch/

They will be included with MkDocs by default until a future release. After that
they will be installable with pip: `pip install mkdocs-bootstrap` and `pip
install mkdocs-bootswatch`

See the documentation for [Customizing Your Theme] for more information about using
and customizing themes and [Custom themes] for creating and distributing new
themes

[Customizing Your Theme]: ../user-guide/customizing-your-theme.md
[Custom themes]: ../dev-guide/themes.md

### Other Changes and Additions to Version 0.15.0

* Fix issues when using absolute links to Markdown files. (#628)
* Deprecate support of Python 2.6, pending removal in 1.0.0. (#165)
* Add official support for Python version 3.5.
* Add support for [site_description] and [site_author] to the [ReadTheDocs] theme. (#631)
* Update FontAwesome to 4.5.0. (#789)
* Increase IE support with X-UA-Compatible. (#785)
* Added support for Python's `-m` flag. (#706)
* Bugfix: Ensure consistent ordering of auto-populated pages. (#638)
* Bugfix: Scroll the tables of contents on the MkDocs theme if it is too long for the page. (#204)
* Bugfix: Add all ancestors to the page attribute `ancestors` rather than just the initial one. (#693)
* Bugfix: Include HTML in the build output again. (#691)
* Bugfix: Provide filename to Read the Docs. (#721 and RTD#1480)
* Bugfix: Silence Click's unicode_literals warning. (#708)

[site_description]: ../user-guide/configuration.md#site_description
[site_author]: ../user-guide/configuration.md#site_author
[ReadTheDocs]: ../user-guide/choosing-your-theme.md#readthedocs

## Version 0.14.0 (2015-06-09)

* Improve Unicode handling by ensuring that all config strings are loaded as Unicode. (#592)
* Remove dependency on the six library. (#583)
* Remove dependency on the ghp-import library. (#547)
* Add `--quiet` and `--verbose` options to all sub-commands. (#579)
* Add short options (`-a`) to most command line options. (#579)
* Add copyright footer for readthedocs theme. (#568)
* If the requested port in `mkdocs serve` is already in use, don't show the user a full stack trace. (#596)
* Bugfix: Fix a JavaScript encoding problem when searching with spaces. (#586)
* Bugfix: gh-deploy now works if the mkdocs.yml is not in the git repo root. (#578)
* Bugfix: Handle (pass-through instead of dropping) HTML entities while parsing TOC. (#612)
* Bugfix: Default extra_templates to an empty list, don't automatically discover them. (#616)

## Version 0.13.3 (2015-06-02)

* Bugfix: Reduce validation error to a warning if the site_dir is within the docs_dir as this shouldn't cause any problems with building but will inconvenience users building multiple times. (#580)

## Version 0.13.2 (2015-05-30)

* Bugfix: Ensure all errors and warnings are logged before exiting. (#536)
* Bugfix: Fix compatibility issues with ReadTheDocs. (#554)

## Version 0.13.1 (2015-05-27)

* Bugfix: Fix a problem with minimal configurations which only contain a list of paths in the pages config. (#562)

## Version 0.13.0 (2015-05-26)

### Deprecations to Version 0.13.0

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
[site_dir]: ../user-guide/configuration.md#site_dir

#### Change the pages configuration

Provide a [new way] to define pages, and specifically nested pages, in the
mkdocs.yml file and deprecate the existing approach, support will be removed
with MkDocs 1.0.

[new way]: ../user-guide/writing-your-docs.md#configure-pages-and-navigation

#### Warn users about the removal of builtin themes

All themes other than mkdocs and readthedocs will be moved into external
packages in a future release of MkDocs. This will enable them to be more easily
supported and updates outside MkDocs releases.

### Major Additions to Version 0.13.0

#### Search

Support for search has now been added to MkDocs. This is based on the
JavaScript library [lunr.js]. It has been added to both the `mkdocs` and
`readthedocs` themes. See the custom theme documentation on [supporting search]
for adding it to your own themes.

[lunr.js]: https://lunrjs.com/
[supporting search]: ../dev-guide/themes.md#search-and-themes

#### New Command Line Interface

The command line interface for MkDocs has been re-written with the Python
library [Click]. This means that MkDocs now has an easier to use interface
with better help output.

This change is partially backwards incompatible as while undocumented it was
possible to pass any configuration option to the different commands. Now only
a small subset of the configuration options can be passed to the commands. To
see in full commands and available arguments use `mkdocs --help` and
`mkdocs build --help` to have them displayed.

[Click]: https://click.palletsprojects.com/

#### Support Extra HTML and XML files

Like the [extra_javascript] and [extra_css] configuration options, a new
option named [extra_templates] has been added. This will automatically be
populated with any `.html` or `.xml` files in the project docs directory.

Users can place static HTML and XML files and they will be copied over, or they
can also use Jinja2 syntax and take advantage of the [global variables].

By default MkDocs will use this approach to create a sitemap for the
documentation.

[extra_javascript]: ../user-guide/configuration.md#extra_javascript
[extra_css]: ../user-guide/configuration.md#extra_css
[extra_templates]: ../user-guide/configuration.md#extra_templates
[global variables]: ../dev-guide/themes.md#global-context

### Other Changes and Additions to Version 0.13.0

* Add support for [Markdown extension configuration options]. (#435)
* MkDocs now ships Python [wheels]. (#486)
* Only include the build date and MkDocs version on the homepage. (#490)
* Generate sitemaps for documentation builds. (#436)
* Add a clearer way to define nested pages in the configuration. (#482)
* Add an [extra config] option for passing arbitrary variables to the template. (#510)
* Add `--no-livereload` to `mkdocs serve` for a simpler development server. (#511)
* Add copyright display support to all themes (#549)
* Add support for custom commit messages in a `mkdocs gh-deploy` (#516)
* Bugfix: Fix linking to media within the same directory as a markdown file called index.md (#535)
* Bugfix: Fix errors with Unicode filenames (#542).

[extra config]: ../user-guide/configuration.md#extra
[Markdown extension configuration options]: ../user-guide/configuration.md#markdown_extensions
[wheels]: https://pythonwheels.com/

## Version 0.12.2 (2015-04-22)

* Bugfix: Fix a regression where there would be an error if some child titles were missing but others were provided in the pages config. (#464)

## Version 0.12.1 (2015-04-14)

* Bugfix: Fixed a CSS bug in the table of contents on some browsers where the bottom item was not clickable.

## Version 0.12.0 (2015-04-14)

* Display the current MkDocs version in the CLI output. (#258)
* Check for CNAME file when using gh-deploy. (#285)
* Add the homepage back to the navigation on all themes. (#271)
* Add a strict more for local link checking. (#279)
* Add Google analytics support to all themes. (#333)
* Add build date and MkDocs version to the ReadTheDocs and MkDocs theme outputs. (#382)
* Standardize highlighting across all themes and add missing languages. (#387)
* Add a verbose flag. (-v) to show more details about what the build. (#147)
* Add the option to specify a remote branch when deploying to GitHub. This enables deploying to GitHub pages on personal and repo sites. (#354)
* Add favicon support to the ReadTheDocs theme HTML. (#422)
* Automatically refresh the browser when files are edited. (#163)
* Bugfix: Never re-write URLs in code blocks. (#240)
* Bugfix: Don't copy dotfiles when copying media from the `docs_dir`. (#254)
* Bugfix: Fix the rendering of tables in the ReadTheDocs theme. (#106)
* Bugfix: Add padding to the bottom of all bootstrap themes. (#255)
* Bugfix: Fix issues with nested Markdown pages and the automatic pages configuration. (#276)
* Bugfix: Fix a URL parsing error with GitHub enterprise. (#284)
* Bugfix: Don't error if the mkdocs.yml is completely empty. (#288)
* Bugfix: Fix a number of problems with relative URLs and Markdown files. (#292)
* Bugfix: Don't stop the build if a page can't be found, continue with other pages. (#150)
* Bugfix: Remove the site_name from the page title, this needs to be added manually. (#299)
* Bugfix: Fix an issue with table of contents cutting off Markdown. (#294)
* Bugfix: Fix hostname for BitBucket. (#339)
* Bugfix: Ensure all links end with a slash. (#344)
* Bugfix: Fix repo links in the readthedocs theme. (#365)
* Bugfix: Include jQuery locally to avoid problems using MkDocs offline. (#143)
* Bugfix: Don't allow the docs_dir to be in the site_dir or vice versa. (#384)
* Bugfix: Remove inline CSS in the ReadTheDocs theme. (#393)
* Bugfix: Fix problems with the child titles due to the order the pages config was processed. (#395)
* Bugfix: Don't error during live reload when the theme doesn't exist. (#373)
* Bugfix: Fix problems with the Meta extension when it may not exist. (#398)
* Bugfix: Wrap long inline code otherwise they will run off the screen. (#313)
* Bugfix: Remove HTML parsing regular expressions and parse with HTMLParser to fix problems with titles containing code. (#367)
* Bugfix: Fix an issue with the scroll to anchor causing the title to be hidden under the navigation. (#7)
* Bugfix: Add nicer CSS classes to the HTML tables in bootswatch themes. (#295)
* Bugfix: Fix an error when passing in a specific config file with `mkdocs serve`. (#341)
* Bugfix: Don't overwrite index.md files with the `mkdocs new` command. (#412)
* Bugfix: Remove bold and italic from code in the ReadTheDocs theme. (#411)
* Bugfix: Display images inline in the MkDocs theme. (#415)
* Bugfix: Fix problems with no-highlight in the ReadTheDocs theme. (#319)
* Bugfix: Don't delete hidden files when using `mkdocs build --clean`. (#346)
* Bugfix: Don't block newer versions of Python-markdown on Python >= 2.7. (#376)
* Bugfix: Fix encoding issues when opening files across platforms. (#428)

## Version 0.11.1 (2014-11-20)

* Bugfix: Fix a CSS wrapping issue with code highlighting in the ReadTheDocs theme. (#233)

## Version 0.11.0 (2014-11-18)

* Render 404.html files if they exist for the current theme. (#194)
* Bugfix: Fix long nav bars, table rendering and code highlighting in MkDocs and ReadTheDocs themes. (#225)
* Bugfix: Fix an issue with the google_analytics code. (#219)
* Bugfix: Remove `__pycache__` from the package tar. (#196)
* Bugfix: Fix markdown links that go to an anchor on the current page. (#197)
* Bugfix: Don't add `prettyprint well` CSS classes to all HTML, only add it in the MkDocs theme. (#183)
* Bugfix: Display section titles in the ReadTheDocs theme. (#175)
* Bugfix: Use the polling observer in watchdog so rebuilding works on filesystems without inotify. (#184)
* Bugfix: Improve error output for common configuration related errors. (#176)

## Version 0.10.0 (2014-10-29)

* Added support for Python 3.3 and 3.4. (#103)
* Configurable Python-Markdown extensions with the config setting `markdown_extensions`. (#74)
* Added `mkdocs json` command to output your rendered documentation as json files. (#128)
* Added `--clean` switch to `build`, `json` and `gh-deploy` commands to remove stale files from the output directory. (#157)
* Support multiple theme directories to allow replacement of individual templates rather than copying the full theme. (#129)
* Bugfix: Fix `<ul>` rendering in readthedocs theme. (#171)
* Bugfix: Improve the readthedocs theme on smaller displays. (#168)
* Bugfix: Relaxed required python package versions to avoid clashes. (#104)
* Bugfix: Fix issue rendering the table of contents with some configs. (#146)
* Bugfix: Fix path for embedded images in sub pages. (#138)
* Bugfix: Fix `use_directory_urls` config behavior. (#63)
* Bugfix: Support `extra_javascript` and `extra_css` in all themes. (#90)
* Bugfix: Fix path-handling under Windows. (#121)
* Bugfix: Fix the menu generation in the readthedocs theme. (#110)
* Bugfix: Fix the mkdocs command creation under Windows. (#122)
* Bugfix: Correctly handle external `extra_javascript` and `extra_css`. (#92)
* Bugfix: Fixed favicon support. (#87)
