#coding: utf-8

from mkdocs.config import load_config
from mkdocs.build import build
from mkdocs.serve import serve
import sys


def main(*args):
    config = load_config()
    build(config)
    if '--serve' in args:
        serve(config)


if __name__ == '__main__':
    main(sys.argv[1:])
