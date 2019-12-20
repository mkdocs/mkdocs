from click import ClickException


class MkDocsException(ClickException):
    """Base exceptions for all MkDocs Exceptions"""


class ConfigurationError(MkDocsException):
    """Error in configuration"""
