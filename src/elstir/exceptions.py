from click import ClickException


class elstirException(ClickException):
    """Base exceptions for all elstir Exceptions"""


class ConfigurationError(elstirException):
    """Error in configuration"""
