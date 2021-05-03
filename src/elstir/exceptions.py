from click import ClickException, echo


class elstirException(ClickException):
    """Base exceptions for all elstir Exceptions"""


class Abort(elstirException):
    """Abort the build"""
    def show(self, **kwargs):
        echo(self.format_message())


class ConfigurationError(elstirException):
    """Error in configuration"""


class BuildError(elstirException):
    """Error during the build process"""


class PluginError(BuildError):
    """Error in a plugin"""

