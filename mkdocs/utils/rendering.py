import copy
from typing import Callable
from xml.etree import ElementTree as etree

import markdown
import markdown.treeprocessors

# TODO: This will become unnecessary after min-versions have Markdown >=3.4
_unescape: Callable[[str], str]
try:
    _unescape = markdown.treeprocessors.UnescapeTreeprocessor().unescape
except AttributeError:
    _unescape = lambda s: s

# TODO: Most of this file will become unnecessary after https://github.com/Python-Markdown/markdown/pull/1441


def get_heading_text(el: etree.Element, md: markdown.Markdown) -> str:
    el = _remove_fnrefs(_remove_anchorlink(el))
    return _strip_tags(_render_inner_html(el, md))


def _strip_tags(text: str) -> str:
    """Strip HTML tags and return plain text. Note: HTML entities are unaffected."""
    # A comment could contain a tag, so strip comments first
    while (start := text.find('<!--')) != -1 and (end := text.find('-->', start)) != -1:
        text = text[:start] + text[end + 3 :]

    while (start := text.find('<')) != -1 and (end := text.find('>', start)) != -1:
        text = text[:start] + text[end + 1 :]

    # Collapse whitespace
    text = ' '.join(text.split())
    return text


def _render_inner_html(el: etree.Element, md: markdown.Markdown) -> str:
    # The `UnescapeTreeprocessor` runs after `toc` extension so run here.
    text = md.serializer(el)
    text = _unescape(text)

    # Strip parent tag
    start = text.index('>') + 1
    end = text.rindex('<')
    text = text[start:end].strip()

    for pp in md.postprocessors:
        text = pp.run(text)
    return text


def _remove_anchorlink(el: etree.Element) -> etree.Element:
    """Drop anchorlink from a copy of the element, if present."""
    if len(el) > 0 and el[-1].tag == 'a' and el[-1].get('class') == 'headerlink':
        el = copy.copy(el)
        del el[-1]
    return el


def _remove_fnrefs(root: etree.Element) -> etree.Element:
    """Remove footnote references from a copy of the element, if any are present."""
    # If there are no `sup` elements, then nothing to do.
    if next(root.iter('sup'), None) is None:
        return root
    root = copy.deepcopy(root)
    # Find parent elements that contain `sup` elements.
    for parent in root.iterfind('.//sup/..'):
        carry_text = ""
        for child in reversed(parent):  # Reversed for the ability to mutate during iteration.
            # Remove matching footnote references but carry any `tail` text to preceding elements.
            if child.tag == 'sup' and child.get('id', '').startswith('fnref'):
                carry_text = (child.tail or "") + carry_text
                parent.remove(child)
            elif carry_text:
                child.tail = (child.tail or "") + carry_text
                carry_text = ""
        if carry_text:
            parent.text = (parent.text or "") + carry_text
    return root
