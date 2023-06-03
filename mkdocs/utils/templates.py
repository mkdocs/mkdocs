from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Sequence

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

if TYPE_CHECKING:
    import datetime

try:
    from jinja2 import pass_context as contextfilter  # type: ignore
except ImportError:
    from jinja2 import contextfilter  # type: ignore

from mkdocs.utils import normalize_url

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import File
    from mkdocs.structure.nav import Navigation
    from mkdocs.structure.pages import Page


class TemplateContext(TypedDict):
    nav: Navigation
    pages: Sequence[File]
    base_url: str
    extra_css: Sequence[str]
    extra_javascript: Sequence[str]
    mkdocs_version: str
    build_date_utc: datetime.datetime
    config: MkDocsConfig
    page: Page | None


@contextfilter
def url_filter(context: TemplateContext, value: str) -> str:
    """A Template filter to normalize URLs."""
    return normalize_url(value, page=context['page'], base=context['base_url'])
