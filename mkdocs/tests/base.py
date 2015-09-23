from __future__ import unicode_literals
import textwrap
import markdown

from mkdocs import toc


def dedent(text):
    return textwrap.dedent(text).strip()


def markdown_to_toc(markdown_source):
    md = markdown.Markdown(extensions=['toc'])
    md.convert(markdown_source)
    toc_output = md.toc
    return toc.TableOfContents(toc_output)
