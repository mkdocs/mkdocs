# coding: utf-8

from __future__ import unicode_literals
import io
import logging
import os

# Define some directory
scaffold_dir = os.path.join(os.getcwd(), '_scaffold')
config_path = os.path.join(os.getcwd(), 'mkdocs.yml')

# Get log object
log = logging.getLogger(__name__)


def add(template, output_dir, filename, create_directory, template_directory):
    """
        Add a new page with scaffolded template
    """

    # Check if directory is a mkdocs project before continuing
    if not os.path.exists(config_path):
        log.error('This is not a mkdocs projet directory.')
        return

    # Add some path for checking
    if not template_directory is None:
        template_path = os.path.join(
            os.path.join(os.getcwd(), template_directory), template + '.md'
        )
    else:
        template_path = os.path.join(scaffold_dir, template + '.md')
    filename_path = os.path.join(output_dir, filename + '.md')
    output_dir = 'docs/' + output_dir

    # Check if everything exists
    if not __check_existance(template_path, output_dir, filename_path, create_directory):
        return

    # Write the template content to file
    __write_file(template_path, filename_path)

    log.info('The file was successfully created in ' + filename_path)
    return

def __check_existance(template_path, output_dir, filename_path, create_directory):
    """
        Check existance or not of folder/file
    """

    if not os.path.exists(template_path):
        log.error('This template doesn\'t exist. You need to create it first.')
        return False

    if not os.path.exists(output_dir) and not create_directory:
        log.error('Output directory doesn\'t exist. You need to create it first.')
        return False
    elif not os.path.exists(output_dir) and create_directory:
        os.mkdir(output_dir)

    if os.path.exists(filename_path):
        log.error('This file already exist.')
        return False

    return True

def __write_file(template_path, filename_path):
    """
        Write template content to file
    """
    template_value = io.open(template_path, 'r', encoding='utf-8').read()
    io.open(filename_path, 'w', encoding='utf-8').write(template_value)
    return
