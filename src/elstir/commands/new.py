import logging
import os

config_text = 'site_name: My Docs\n'
index_text = """# Welcome to elstir

For full documentation visit [elstir.org](https://github.com/claudioperez/elstir).

## Commands

* `elstir new [dir-name]` - Create a new project.
* `elstir serve` - Start the live-reloading docs server.
* `elstir build` - Build the documentation site.
* `elstir -h` - Print help message and exit.

## Project layout

    elstir.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.
"""

log = logging.getLogger(__name__)


def new(output_dir):

    docs_dir = os.path.join(output_dir, 'docs')
    config_path = os.path.join(output_dir, 'elstir.yml')
    index_path = os.path.join(docs_dir, 'index.md')

    if os.path.exists(config_path):
        log.info('Project already exists.')
        return

    if not os.path.exists(output_dir):
        log.info('Creating project directory: %s', output_dir)
        os.mkdir(output_dir)

    log.info('Writing config file: %s', config_path)
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_text)

    if os.path.exists(index_path):
        return

    log.info('Writing initial docs: %s', index_path)
    if not os.path.exists(docs_dir):
        os.mkdir(docs_dir)
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_text)
