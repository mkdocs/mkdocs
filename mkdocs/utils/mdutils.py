def get_markdown_title(markdown):
    """
    Get the title of a Markdown document. The title in this case is considered
    to be a H1 that occurs before any other content in the document.

    The procedure is then to iterate through the lines, stopping at the first
    non-whitespace content. If it is a title, return that, otherwise return
    None.
    """

    lines = markdown.replace('\r\n', '\n').replace('\r', '\n').split('\n')

    while lines:

        line = lines.pop(0).strip()

        if not line.strip():
            continue

        if not line.startswith('# '):
            return

        return line.lstrip('# ')
