# Localizing Your Theme

Display your theme in your favorite language.

---

!!! Note
    Theme localization only translates the text elements of the theme itself,
    not the actual content of your documentation. If you wish to create a
    multilingual documentation, you need to combine theme localization as
    described here with a third-party internationalization/localization plugin.

## Installation

For theme localization to work, you must install `mkdocs[i18n]` which will
enable `i18n` (internationalization) support on MkDocs:

```bash
pip install mkdocs[i18n]
```

## Usage

!!! Warning
    If you configure a language locale that is not supported by the theme yet,
    it will fallback to the default `en` (English) locale.

The `mkdocs` and `readthedocs` themes support a ISO-639-1 (2-letter) `locale`
parameter that allows you to change the language of all the text elements of
your theme.

For example, to build the `mkdocs` theme in French you would use:

     theme:
         name: mkdocs
         locale: fr

## Contributing theme translations

If your theme has not been translated for your language yet, feel free to
contribute it using the [theme localization guide](../dev-guide/translating-themes.md).
