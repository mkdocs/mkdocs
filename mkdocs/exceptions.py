from __future__ import unicode_literals
from click import ClickException


class MkDocsException(ClickException):
    """Base exceptions for all MkDocs Exceptions"""


class ConfigurationError(MkDocsException):
    """Error in configuration"""


class MarkdownNotFound(MkDocsException):
    """A linked local Markdown file isn't found in the table of contents."""
