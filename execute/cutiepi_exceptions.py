# Author: Saurav Gupta
# Date Created: Sep. 12, 2019

"""
File for custom Exceptions
"""


class CutiePiError(Exception):
    """ Base class for custom Exceptions. """
    pass


class InitiationError(CutiePiError):
    """Base class for initiation errors."""
    pass


class MonitorInitiationError(InitiationError):
    """Raised when there is problem in Initiation of Monitor Components."""
    pass


class CloudInitiationError(InitiationError):
    """Raised when there is problem with starting cloud signal receiver."""
    pass


class MonitorOperationError(CutiePiError):
    """Raised if there is any error during operations on monitor devices."""
    pass


class CloudConnectionError(CutiePiError):
    """Raised if there is any error with connection to MQTT broker."""
    pass


class InvalidObjectCreation(CutiePiError):
    """Raised when object is created not from intended place."""
    pass


class EncryptionError(CutiePiError):
    """Raised when any error occurred during encrypting signal."""
    pass


class DecryptionError(CutiePiError):
    """Raised when any error occurred during decrypting signal."""
    pass


class InvalidCloudSignal(CutiePiError):
    """Raised when received cloud signal is invalid."""
    pass


class InvalidHardwareSignal(CutiePiError):
    """Raised when received hardware signal is invalid"""
    pass

