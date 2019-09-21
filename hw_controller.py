# Author: Saurav Gupta
# Date Created Created: Sep. 01, 2019

"""
This is entry point for sensors and actuators (or bridge between Pi and Arduino).
Module which is responsible for controlling and monitoring actuators and sensors.
"""

from threading import Thread


class _HardwareClient(Thread):
    def __init__(self, name, mode):
        self._name = name
        Thread.__init__(self)

    def run(self):
        pass


class HardwareSignal:
    def __init__(self):
        pass

    def transmit(self, signal):
        pass

    def receive(self):
        pass
