from click import ClickException


class MkDocsException(ClickException):
    """Base exceptions for all MkDocs Exceptions"""


class ConfigurationError(MkDocsException):
    """Error in configuration"""


class BuildError(MkDocsException):
    """Error during the build process"""


class PluginError(BuildError):
    """Error in a plugin"""
