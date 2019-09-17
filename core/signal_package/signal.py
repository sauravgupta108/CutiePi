# Author: Saurav Gupta
# Date Created: Sep. 17, 2019

"""
This file provides schema for different signals
"""

import tables as tb


class BaseSignal(tb.IsDescription):
    """
    Base class for signals
    """
    name = tb.UInt64Col()
    message = tb.StringCol(128)
    protocol = tb.StringCol(32)
    incoming_time = tb.Time64Col()


class CloudSignal(BaseSignal):
    """
    Cloud signal schema.
    Defines additional fields to BaseSignal
    """
    source_type = tb.StringCol(64)


class HardwareSignal(BaseSignal):
    """
    Hardware signal schema.
    Defines additional fields to BaseSignal
    """
    device_type = tb.StringCol(64)
