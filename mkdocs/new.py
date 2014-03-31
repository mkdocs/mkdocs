# coding: utf-8

import os

config_text = 'site_name: My Docs\n'
index_text = """# Welcome to MkDocs

For full documentation visit [mkdocs.org](http://mkdocs.org).

## Commands

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs help` - Print this help message.

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.
"""


def new(args, options):
    if len(args) != 1:
        print "Usage 'mkdocs new [directory-name]'"
        return

    output_dir = args[0]

    docs_dir = os.path.join(output_dir, 'docs')
    config_path = os.path.join(output_dir, 'mkdocs.yml')
    index_path = os.path.join(docs_dir, 'index.md')

    if os.path.exists(config_path):
        print 'Project already exists.'
        return

    if not os.path.exists(output_dir):
        print 'Creating project directory: %s' % output_dir
        os.mkdir(output_dir)

    print 'Writing config file: %s' % config_path
    open(config_path, 'w').write(config_text)

    print 'Writing initial docs: %s' % index_path
    if not os.path.exists(docs_dir):
        os.mkdir(docs_dir)
    open(index_path, 'w').write(index_text)
