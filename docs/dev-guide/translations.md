# Translations

Theme localization guide.

---

The [built-in themes] that are included with MkDocs provide support for
translations. This is a guide for translators, which documents the process for
contributing new translations and/or updating existing translations. For
guidance on modifying the existing themes, see the [Contributing Guide][update
themes]. To enable a specific translation see the documentation about the
specific theme you are using in the [User Guide][built-in themes]. For
translations of third-party themes, please see the documentation for those
themes. For a third-party theme to make use of MkDocs' translation tools and
methods, that theme must be properly [configured] to make use of those tools.

!!! note

    Translations only apply to text contained within a theme's template, such
    as "next" and "previous" links. The Markdown content of a page is not
    translated. If you wish to create multilingual documentation, you need to
    combine theme localization with a third-party
    internationalization/localization plugin.

[built-in themes]: ../user-guide/choosing-your-theme.md
[update themes]: ../about/contributing.md#submitting-changes-to-the-builtin-themes
[configured]: themes.md#supporting-theme-localizationtranslation

## Localization tooling prerequisites

Theme localization makes use of the [babel][babel] project for generation and
compilation of localization files. Custom commands are available from the
MkDocs' `setup.py` script as described below to assist with the process of
updating and contributing translations. You will need to be working from the
git working tree on your local machine to make use of the helper scripts.

See the [Contributing Guide] for direction on how to [Install for Development]
and [Submit a Pull Request]. The instructions in this document assume that you
are working from a properly configured development environment.

Make sure translation requirements are installed in your environment:

```bash
pip install mkdocs[i18n]
```

[babel]: http://babel.pocoo.org/en/latest/cmdline.html
[Contributing Guide]: ../about/contributing.md
[Install for Development]: ../about/contributing.md#installing-for-development
[Submit a Pull Request]: ../about/contributing.md#submitting-pull-requests

## Adding language translations to themes

If your favorite language locale is not yet supported on one (or both) of the
built-in themes (`mkdocs` and `readthedocs`), you can easily contribute a
translation by following the steps below.

Here is a quick summary of what you'll need to do:

1. [Initialize new localization
   catalogs](#initializing-the-localization-catalogs) for your language (if a
   translation for your locale already exists, follow the instructions for
   [updating theme localization
   files](/user-guide/custom-themes/#localizing-themes) instead).
2. [Add a translation](#translating-the-mkdocs-themes) for every text
   placeholder in the localized catalogs.
3. [Locally serve and test](#testing-theme-translations) the translated themes
   for your language.
4. [Update the documentation](#updating-theme-documentation) about
   supported translations for each translated theme.
5. [Contribute your translation](#contributing-translations) through a
   Pull Request.

!!! note

    Translation locales are usually identified using the [ISO-639-1] (2-letter)
    language codes. While territory/region/county codes are also supported,
    location specific translations should only be added after the general
    language translation has been completed and the regional dialect requires
    use of a term which differs from the general language translation.

[ISO-639-1]: https://en.wikipedia.org/wiki/ISO_639-1

### Initializing the localization catalogs

The templates for each theme contain text placeholders that have been extracted
into a Portable Object Template (`messages.pot`) file, which is present in each
theme's folder.

Initializing a catalog consists of running a command which will create a
directory structure for your desired language and prepare a Portable Object
(`messages.po`) file derived from the `pot` file of the theme.

Use the `init_catalog` command on each theme (`-t <theme>`) and provide the
appropriate language code (`-l <language>`). For example, to add a translation
for the Spanish `es` language to the `mkdocs` theme, run the following command:

```bash
python setup.py init_catalog -t mkdocs -l es
```

The above command will create the following file structure:

```text
mkdocs/themes/mkdocs/locales
├── es
│   └── LC_MESSAGES
│       └── messages.po
```

You can now move on to the next step and [add a
translation](#translating-the-mkdocs-themes) for every text placeholder in the
localized catalog.

## Updating a theme translation

If a theme's `messages.pot` template file has been [updated][update themes]
since the `messages.po` was last updated for your locale, follow the steps
below to update the theme's `messages.po` file:

1. [Update the theme's translation catalog](#updating-the-translation-catalogs)
   to refresh the translatable text placeholders of each theme.
2. [Translate](#translating-the-mkdocs-themes) the newly added translatable
   text placeholders on every `messages.po` catalog file language you can.
3. [Locally serve and test](#testing-theme-translations) the translated themes
   for your language.
4. [Contribute your translation](#contributing-translations) through a
   Pull Request.

### Updating the translation catalogs

This step should be completed after a theme template have been [updated][update
themes] for each language that you are comfortable contributing a translation
for.

To update the `fr` translation catalog of the `mkdocs` theme, use the following
command:

```bash
python setup.py update_catalog -t mkdocs -l fr
```

You can now move on to the next step and [add a translation] for every updated
text placeholder in the localized catalog.

[add a translation]: #translating-the-mkdocs-themes

### Translating the MkDocs themes

Now that your localized `messages.po` files are ready, all you need to do is
add a translation in each `msgstr` item for each `msgid` item in the file.

```text
msgid "Next"
msgstr "Siguiente"
```

!!! Warning
    Do not modify the `msgid` as it is common to all translations. Just add
    its translation in the `msgstr` item.

Once you have finished translating all of the terms listed in the `po` file,
you'll want to [test your localized theme](#testing-theme-translations).

### Testing theme translations

To test a theme with translations, you need to first compile the `messages.po`
files of your theme into `messages.mo` files. The following command will compile
the `es` translation for the `mkdocs` theme.

```bash
python setup.py compile_catalog -t mkdocs -l es
```

The above command results in the following file structure:

```text
mkdocs/themes/mkdocs/locales
├── es
│   └── LC_MESSAGES
│       ├── messages.mo
│       └── messages.po
```

Note that the compiled `messages.mo` file was generated based on the
`messages.po` file that you just edited.

Then modify the `mkdocs.yml` file at the root of the project to test the new
and/or updated locale:

```yaml
theme:
    name: mkdocs
    locale: es
```

Finally, run `mkdocs serve` to check out your new localized version of the theme.

!!! Note
    The build and release process takes care of compiling and distributing
    all locales to end users so you only have to worry about contributing the
    actual text translation `messages.po` files (the rest is ignored by git).

    After you have finished testing your work, be sure to undo the change to
    the `locale` setting in the `mkdocs.yml` file before submitting your
    changes.

## Updating theme documentation

Update the lists of supported translations for each translated theme located at
[Choosing your theme](../user-guide/choosing-your-theme.md)
(`docs/user-guide/choosing-your-theme.md`), in their __`locale`__ options.

## Contributing translations

It is now time for you to [contribute](../about/contributing.md) your nice work
to the project. Thank you!
