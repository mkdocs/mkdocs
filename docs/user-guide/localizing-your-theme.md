# Localizing Your Theme

Display your theme in your preferred language.

---

!!! Note

    Theme localization only translates the text elements of the theme itself
    (such as "next" and "previous" links), not the actual content of your
    documentation. If you wish to create multilingual documentation, you need
    to combine theme localization as described here with a third-party
    internationalization/localization plugin.

## Installation

For theme localization to work, you must install `mkdocs[i18n]`, which will
enable `i18n` (internationalization) support on MkDocs:

```bash
pip install mkdocs[i18n]
```

## Supported languages

See the documentation for the theme you are using for a list of supported languages.

- [mkdocs]
- [readthedocs]

## Usage

!!! Warning
    If you configure a language locale that is not supported by the theme yet,
    it will fall back to the default `en` (English) locale.

The `mkdocs` and `readthedocs` themes support a ISO-639-1 (2-letter) `locale`
parameter that allows you to change the language of all the text elements of
your theme.

For example, to build the `mkdocs` theme in French you would use:

     theme:
         name: mkdocs
         locale: fr

Changing the theme's `locale` will also change the HTML's `lang` attribute to
the chosen locale automatically.

## Contributing theme translations

If a theme has not yet been translated for your language, feel free to
contribute a translation using the [Translation Guide].

[Translation Guide]: ../dev-guide/translations.md
[mkdocs]: choosing-your-theme.md#mkdocs-locale
[readthedocs]: choosing-your-theme.md#readthedocs-locale
