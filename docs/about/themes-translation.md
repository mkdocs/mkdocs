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
pip install -r requirements/project.txt
```

[babel]: http://babel.pocoo.org/en/latest/cmdline.html

## Contributing a theme translation

If your favorite language locale is not supported yet on the `mkdocs` and
`readthedocs` built-in themes, you can easily contribute it to the project by
following the steps below.

Here is a quick recap of what you'll have to do:

1. [Initialize new localization catalogs](#initializing-the-localization-catalogs) for your language
2. [Add a translation](#translating-the-mkdocs-themes) for every text placeholder in the localized catalogs
3. [Serve and test locally](#testing-themes-translations) the translated themes for your language
4. [Contribute your translation](#contributing-your-translations) through a Pull Request

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

### Testing themes translations

Once you're done translating you'll want to test your localized theme.

For this you need to compile the `messages.po` files into `messages.mo` files:

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

## Updating theme localization files

If you changed some text in the theme themselves and modified the HTML source
of a theme, it is necessary to follow the steps below:

1. [Extract each theme's text](#extracting-text-from-themes) to update their Portable Object Template files
2. [Update the translation catalog `messages.po` files](#updating-the-translation-catalogs) for every supported locale
3. [Translate](#translating-the-mkdocs-themes) the newly added text placeholders on every `messages.po` file for
every supported locale
4. [Contribute your updated translations](#contributing-your-translations) through a Pull Request

### Extracting text from themes

This step will parse and extract the text from the HTML sources of the themes:

```bash
$ python setup.py extract_messages -t mkdocs
running extract_messages
extracting messages from mkdocs/themes/mkdocs/404.html (ignore_tags="script,style", include_attrs="alt title summary")
extracting messages from mkdocs/themes/mkdocs/base.html (ignore_tags="script,style", include_attrs="alt title summary")
extracting messages from mkdocs/themes/mkdocs/content.html (ignore_tags="script,style", include_attrs="alt title summary")
extracting messages from mkdocs/themes/mkdocs/keyboard-modal.html (ignore_tags="script,style", include_attrs="alt title summary")
extracting messages from mkdocs/themes/mkdocs/main.html (ignore_tags="script,style", include_attrs="alt title summary")
extracting messages from mkdocs/themes/mkdocs/nav-sub.html (ignore_tags="script,style", include_attrs="alt title summary")
extracting messages from mkdocs/themes/mkdocs/search-modal.html (ignore_tags="script,style", include_attrs="alt title summary")
extracting messages from mkdocs/themes/mkdocs/toc.html (ignore_tags="script,style", include_attrs="alt title summary")
writing PO template file to mkdocs/themes/mkdocs/messages.pot

$ python setup.py extract_messages -t readthedocs
running extract_messages
extracting messages from mkdocs/themes/readthedocs/404.html (ignore_tags="script,style", include_attrs="alt title summary")
extracting messages from mkdocs/themes/readthedocs/base.html (ignore_tags="script,style", include_attrs="alt title summary")
extracting messages from mkdocs/themes/readthedocs/breadcrumbs.html (ignore_tags="script,style", include_attrs="alt title summary")
extracting messages from mkdocs/themes/readthedocs/footer.html (ignore_tags="script,style", include_attrs="alt title summary")
extracting messages from mkdocs/themes/readthedocs/main.html (ignore_tags="script,style", include_attrs="alt title summary")
extracting messages from mkdocs/themes/readthedocs/nav.html (ignore_tags="script,style", include_attrs="alt title summary")
extracting messages from mkdocs/themes/readthedocs/search.html (ignore_tags="script,style", include_attrs="alt title summary")
extracting messages from mkdocs/themes/readthedocs/searchbox.html (ignore_tags="script,style", include_attrs="alt title summary")
extracting messages from mkdocs/themes/readthedocs/toc.html (ignore_tags="script,style", include_attrs="alt title summary")
extracting messages from mkdocs/themes/readthedocs/versions.html (ignore_tags="script,style", include_attrs="alt title summary")
writing PO template file to mkdocs/themes/readthedocs/messages.pot
```

### Updating the translation catalogs

This has to be done for every supported language. For example, on the `mkdocs`
theme if there were only the `fr` and `es` locales you would need to:

```bash
$ python setup.py update_catalog -t mkdocs -l fr
running update_catalog
updating catalog mkdocs/themes/mkdocs/locales/fr/LC_MESSAGES/messages.po based on mkdocs/themes/mkdocs/messages.pot

$ python setup.py update_catalog -t mkdocs -l es
running update_catalog
updating catalog mkdocs/themes/mkdocs/locales/es/LC_MESSAGES/messages.po based on mkdocs/themes/mkdocs/messages.pot
```
