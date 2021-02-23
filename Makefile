babel_extract:
	pybabel extract -F mkdocs/themes/babel.cfg -o mkdocs/themes/mkdocs/messages.pot --omit-header --no-wrap mkdocs/themes/mkdocs
	pybabel extract -F mkdocs/themes/babel.cfg -o mkdocs/themes/readthedocs/messages.pot --omit-header --no-wrap mkdocs/themes/readthedocs

babel_init:
ifndef LOCALE
	$(error missing LOCALE environment variable declaration)
endif
	pybabel init -i mkdocs/themes/mkdocs/messages.pot -d mkdocs/themes/mkdocs/locales -l $(LOCALE)
	pybabel init -i mkdocs/themes/readthedocs/messages.pot -d mkdocs/themes/readthedocs/locales -l $(LOCALE)

babel_update:
ifndef LOCALE
	$(error missing LOCALE environment variable declaration)
endif
	pybabel update -i mkdocs/themes/mkdocs/messages.pot -d mkdocs/themes/mkdocs/locales --ignore-obsolete -l $(LOCALE)
	pybabel update -i mkdocs/themes/readthedocs/messages.pot -d mkdocs/themes/readthedocs/locales --ignore-obsolete -l $(LOCALE)

babel_compile: babel_update
ifndef LOCALE
	$(error missing LOCALE environment variable declaration)
endif
	pybabel compile -d mkdocs/themes/mkdocs/locales --statistics -l $(LOCALE)
	pybabel compile -d mkdocs/themes/readthedocs/locales --statistics -l $(LOCALE)
