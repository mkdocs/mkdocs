# MkDocs themes translation

How to add a locale translation to MkDocs built-in themes.

---

## Localization tooling prerequisites

Theme localization uses the [babel][babel] project to handle theme localization
files generation and compilation. We worked on wrapping its usage through
`setup.py` commands as described below to make updating and contributing
translations easy.

Make sure translation requirements are installed in your environment:

```bash
pip install mkdocs[i18n]
```

[babel]: http://babel.pocoo.org/en/latest/cmdline.html

## Contributing a new theme translation

If your favorite language locale is not supported yet on the `mkdocs` and
`readthedocs` built-in themes, you can easily contribute it to the project by
following the steps below.

Here is a quick recap of what you'll have to do:

1. [Initialize new localization catalogs](#initializing-the-localization-catalogs)
for your language (if a translation for your locale already exists,
follow the [updating theme localization files](#updating-theme-localization-files)
instead)
2. [Add a translation](#translating-the-mkdocs-themes) for every text placeholder
in the localized catalogs
3. [Serve and test locally](#testing-themes-translations) the translated themes
for your language
4. [Contribute your translation](#contributing-your-translations) through a
Pull Request

### Initializing the localization catalogs

The MkDocs themes contain text placeholders that have been extracted into
Portable Object Template (messages.pot) files present in each theme's folder.

Initializing a catalog consists of running a command which will create a
directory structure for your desired language and prepare a Portable Object
(messages.po) file derived from the POT file of the theme.

Let's say you want to add a translation for the Spanish `es` language.
You will be using the `init_catalog` command on each `-t <theme>` and providing
the `-l <language>` like so:

```bash
$ python setup.py init_catalog -t mkdocs -l es
running init_catalog
creating catalog mkdocs/themes/mkdocs/locales/es/LC_MESSAGES/messages.po based on mkdocs/themes/mkdocs/messages.pot

$ python setup.py init_catalog -t readthedocs -l es
running init_catalog
creating catalog mkdocs/themes/readthedocs/locales/es/LC_MESSAGES/messages.po based on mkdocs/themes/readthedocs/messages.pot
```

Which will create:

```text
mkdocs/themes/mkdocs/locales
├── es
│   └── LC_MESSAGES
│       └── messages.po
...
mkdocs/themes/readthedocs/locales
├── es
│   └── LC_MESSAGES
│       └── messages.po
```

You can now move on to the next step and [add a translation](#translating-the-mkdocs-themes)
for every text placeholder in the localized catalogs.

## Updating a theme translation

If a [theme's `messages.pot` template file has been updated](/user-guide/custom-themes/#localizing-themes)
since the `messages.po` was last updated for your locale, follow the steps below
to update the theme's `messages.po` file:

1. [Update the themes' translation catalogs](#updating-the-translation-catalogs)
to refresh the translatable text placeholders of each theme
2. [Translate](#translating-the-mkdocs-themes) the newly added translatable text
placeholders on every `messages.po` catalog file language you can
3. [Serve and test locally](#testing-themes-translations) the translated themes
for your language
4. [Contribute your updated translations](#contributing-your-translations)
through a Pull Request

### Updating the translation catalogs

This step has to be done on each updated theme and for every language that you
are comfortable contributing a translation to.

For example, updating the `fr` local translation catalogs should be done like
this:

```bash
$ python setup.py update_catalog -t mkdocs -l fr
running update_catalog
updating catalog mkdocs/themes/mkdocs/locales/fr/LC_MESSAGES/messages.po based on mkdocs/themes/mkdocs/messages.pot

$ python setup.py update_catalog -t readthedocs -l fr
running update_catalog
updating catalog mkdocs/themes/readthedocs/locales/fr/LC_MESSAGES/messages.po based on mkdocs/themes/readthedocs/messages.pot
```

You can now move on to the next step and [add a translation](#translating-the-mkdocs-themes)
for every updated text placeholder in the localized catalogs.

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

Once you're done translating you'll want to [test your localized theme](#testing-theme-translations).

### Testing themes translations

To test your theme, you need to compile the `messages.po` files of your theme
into `messages.mo` files:

```bash
$ python setup.py compile_catalog -t mkdocs -l es
running compile_catalog
18 of 18 messages (100%) translated in mkdocs/themes/mkdocs/locales/es/LC_MESSAGES/messages.po
compiling catalog mkdocs/themes/mkdocs/locales/es/LC_MESSAGES/messages.po to mkdocs/themes/mkdocs/locales/es/LC_MESSAGES/messages.mo

$ python setup.py compile_catalog -t readthedocs -l es
running compile_catalog
12 of 12 messages (100%) translated in mkdocs/themes/readthedocs/locales/es/LC_MESSAGES/messages.po
compiling catalog mkdocs/themes/readthedocs/locales/es/LC_MESSAGES/messages.po to mkdocs/themes/readthedocs/locales/es/LC_MESSAGES/messages.mo
```

You will get the following file structures:

```text
mkdocs/themes/mkdocs/locales
├── es
│   └── LC_MESSAGES
│       ├── messages.mo
│       └── messages.po
...
mkdocs/themes/readthedocs/locales
├── es
│   └── LC_MESSAGES
│       ├── messages.mo
│       └── messages.po
```

Then just modify the `mkdocs.yml` file at the root of the project to add your
development locale to test:

```yaml
theme:
    name: mkdocs
    locale: es
```

And run `mkdocs serve` to check out your new localized version of the theme.

!!! Note
    The build and release process takes care of compiling and distributing
    all locales to end users so you only have to worry about contributing the
    actual text translation `messages.po` files (the rest is git ignored).

### Contributing your translations

It's now time for you to [contribute your nice work to the project][contribute],
thank you!

[contribute]: contributing.md