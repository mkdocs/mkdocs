from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.nav import Page


def _get_language_of_translation_file(path: Path) -> str:
    with path.open(encoding='utf-8') as f:
        translation_line = f.readline()
    m = re.search('^# (.+) translations ', translation_line)
    assert m
    return m[1]


def on_page_markdown(markdown: str, page: Page, config: MkDocsConfig, **kwargs) -> str | None:
    if page.file.src_uri == 'user-guide/choosing-your-theme.md':
        here = Path(config.config_file_path).parent

        def replacement(m: re.Match) -> str:
            lines = []
            for d in sorted(here.glob(m[2])):
                lang = _get_language_of_translation_file(Path(d, 'LC_MESSAGES', 'messages.po'))
                lines.append(f'{m[1]}`{d.name}`: {lang}')
            return '\n'.join(lines)

        return re.sub(
            r'^( *\* )\(see the list of existing directories `(.+)`\)$',
            replacement,
            markdown,
            flags=re.MULTILINE,
        )
