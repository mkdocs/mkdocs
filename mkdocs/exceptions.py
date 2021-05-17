from click import ClickException, echo


class MkDocsException(ClickException):
    """Base exceptions for all MkDocs Exceptions"""


class Abort(MkDocsException):
    """Abort the build"""
    def show(self, **kwargs):
        echo(self.format_message())


class ConfigurationError(MkDocsException):
    """Error in configuration"""


class BuildError(MkDocsException):
    """Error during the build process"""


class PluginError(BuildError):
    """Error in a plugin"""
