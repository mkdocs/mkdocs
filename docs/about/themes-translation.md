# MkDocs themes translation

How to add a locale translation to mkdocs built-in themes.

---

## Localization tooling prerequisites

Theme localization uses the [babel][babel] project and its `pybabel`
command-line to handle localization files generation and compilation.

Make sure they are installed in your environment:

```bash
pip install -r requirements/project.txt
```

[babel]: http://babel.pocoo.org/en/latest/cmdline.html

## Contributing theme translations

If your favorite language locale is not supported yet by the `mkdocs` and
`readthedocs` built-in themes, you can easily contribute it to the project by
following the steps below.

### Creating the theme localization files

Theme localization is achieved by adding a `messages.po` file to the `locales`
directory tree of the themes. This is easily achieved using the `pybabel`
command-line which will initialize this file for you by deriving it from the
default `en` (English) one.

```text
mkdocs/themes/mkdocs/locales
├── en
│   └── LC_MESSAGES
│       └── messages.po
└── fr
    └── LC_MESSAGES
        └── messages.po
```

Say you'd like to add theme localization for the `es` (Spanish) language, you
would run:

```bash
$ pybabel init -l es -i mkdocs/themes/mkdocs/locales/en/LC_MESSAGES/messages.po -d mkdocs/themes/mkdocs/locales
creating catalog mkdocs/themes/mkdocs/locales/es/LC_MESSAGES/messages.po based on mkdocs/themes/mkdocs/locales/en/LC_MESSAGES/messages.po

$ pybabel init -l es -i mkdocs/themes/readthedocs/locales/en/LC_MESSAGES/messages.po -d mkdocs/themes/readthedocs/locales
creating catalog mkdocs/themes/readthedocs/locales/es/LC_MESSAGES/messages.po based on mkdocs/themes/readthedocs/locales/en/LC_MESSAGES/messages.po
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

### Translating the mkdocs themes

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

For this you need to compile the `messages.po` files into `messages.mo` files
using `pybabel` like this:

```bash
$ pybabel compile -d mkdocs/themes/mkdocs/locales
compiling catalog mkdocs/themes/mkdocs/locales/es/LC_MESSAGES/messages.po to mkdocs/themes/mkdocs/locales/es/LC_MESSAGES/messages.mo
compiling catalog mkdocs/themes/mkdocs/locales/fr/LC_MESSAGES/messages.po to mkdocs/themes/mkdocs/locales/fr/LC_MESSAGES/messages.mo
compiling catalog mkdocs/themes/mkdocs/locales/en/LC_MESSAGES/messages.po to mkdocs/themes/mkdocs/locales/en/LC_MESSAGES/messages.mo

$ pybabel compile -d mkdocs/themes/readthedocs/locales
compiling catalog mkdocs/themes/readthedocs/locales/es/LC_MESSAGES/messages.po to mkdocs/themes/readthedocs/locales/es/LC_MESSAGES/messages.mo
compiling catalog mkdocs/themes/readthedocs/locales/fr/LC_MESSAGES/messages.po to mkdocs/themes/readthedocs/locales/fr/LC_MESSAGES/messages.mo
compiling catalog mkdocs/themes/readthedocs/locales/en/LC_MESSAGES/messages.po to mkdocs/themes/readthedocs/locales/en/LC_MESSAGES/messages.mo
```

You will get the following file structures:

```text
mkdocs/themes/mkdocs/locales
├── en
│   └── LC_MESSAGES
│       ├── messages.mo
│       └── messages.po
├── es
│   └── LC_MESSAGES
│       ├── messages.mo
│       └── messages.po
└── fr
    └── LC_MESSAGES
        ├── messages.mo
        └── messages.po
...
mkdocs/themes/readthedocs/locales
├── en
│   └── LC_MESSAGES
│       ├── messages.mo
│       └── messages.po
├── es
│   └── LC_MESSAGES
│       ├── messages.mo
│       └── messages.po
└── fr
    └── LC_MESSAGES
        ├── messages.mo
        └── messages.po
```

Then just modify the `mkdocs.yml` file at the root of the project to add your
development locale to test:

```yaml
theme:
    name: mkdocs
    locale: es
```

And run `mkdocs serve` to check out your new localized version of the theme.

It's now time for you to [contribute your nice work to the project][contribute],
thank you!

[contribute]: contributing.md
