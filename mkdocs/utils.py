#coding: utf-8

import os
import shutil


def copy_file(source_path, output_path):
    """
    Copy source_path to output_path, making sure any parent directories exist.
    """
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    shutil.copy(source_path, output_path)


def write_file(content, output_path):
    """
    Write content to output_path, making sure any parent directories exist.
    """
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    open(output_path, 'w').write(content)


def get_html_path(path):
    """
    Map a source file path to an output html path.

    Paths like 'index.md' will be converted to 'index.html'
    Paths like 'about.md' will be converted to 'about/index.html'
    Paths like 'api-guide/core.md' will be converted to 'api-guide/core/index.html'
    """
    path = os.path.splitext(path)[0]
    if os.path.basename(path) == 'index':
        return path + '.html'
    return os.path.join(path, 'index.html')
