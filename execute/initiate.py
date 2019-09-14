# Author: Saurav Gupta
# Date Created: Sep. 01, 2019

"""
This file initiate different parts.
"""

import RPi.GPIO as GPIO

from .cutiepi_exceptions import *


class Initiation:
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

    def initiate_monitor(self):
        from monitor import LcdEngine, SevenSegment, Led
        lcd = LcdEngine()
        svn_seg = SevenSegment()
        led = Led()

        if lcd.prepare():
            lcd.display_message("Hello..! Welcome to IoT world.")
        else:
            raise MonitorInitiationError("Error while initiating LCD.")

        return True

    def initiate_cloud_listener(self):
        pass

    def initiate_controller(self):
        pass
