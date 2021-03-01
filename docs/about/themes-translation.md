# MkDocs themes translation

How to add a locale translation to MkDocs built-in themes.

---

## Localization tooling prerequisites

Theme localization uses the [babel][babel] project to handle theme localization
files generation and compilation. We worked on wrapping its usage through
`setup.py` commands as described below to make updating and contributing
translations easy.

Make sure they are installed in your environment:

```bash
pip install -r requirements/project.txt
```

[babel]: http://babel.pocoo.org/en/latest/cmdline.html

## Contributing theme translations

If your favorite language locale is not supported yet on the `mkdocs` and
`readthedocs` built-in themes, you can easily contribute it to the project by
following the steps below.

### Creating the theme localization files

Theme localization is achieved by *extracting text* to be translated from HTML
theme files, then *initializing* a `messages.po` file for a given locale and
finally *adding translations* into it.

Available translation locales are listed under the `locales` folder of every
supported theme:

```text
mkdocs/themes/mkdocs/locales
└── fr
    └── LC_MESSAGES
        └── messages.po
```

Say you'd like to add theme localization for the `es` (Spanish) language, you
would follow the steps below:

#### Extracting text from themes

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

#### Initializing a localization catalog

Now that the text to be translated is extracted, create a catalog to host its
translation for the target locale:

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

It's now time for you to [contribute your nice work to the project][contribute],
thank you!

[contribute]: contributing.md

## Updating theme localization files

When the HTML source files of a theme change it is necessary to *extract* the
theme text again and *update* its translated locales.

1. Run the [text extraction command](#extracting-text-from-themes) on the
modified theme.
2. Update all available locale translations:

        $ python setup.py update_catalog -t mkdocs -l fr
        running update_catalog
        updating catalog mkdocs/themes/mkdocs/locales/fr/LC_MESSAGES/messages.po based on mkdocs/themes/mkdocs/messages.pot

        $ python setup.py update_catalog -t mkdocs -l es
        running update_catalog
        updating catalog mkdocs/themes/mkdocs/locales/es/LC_MESSAGES/messages.po based on mkdocs/themes/mkdocs/messages.pot

3. [Translate the added translations](#translating-the-mkdocs-themes) on all
`messages.po` localization files
