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
        self._mode = mode
        self._signal = None
        self._output_queue = None
        Thread.__init__(self)

    def receive(self, output_queue):
        self._output_queue = output_queue
        Thread.start(self)

    def transmit(self, signal=""):
        assert (signal != "" and len(signal) > 0, "Not a valid signal %s" % signal)
        try:
            self._signal = int(signal)
            Thread.start(self)
        except ValueError:
            pass
            # TODO: Log invalid signal for hardware.

    def run(self):
        if self._mode == "RECEIVE":
            from libraries import BluetoothClient
            bt_client = BluetoothClient()
            bt_client.set_output_queue(self._output_queue)
            bt_client.receive_signal()

        elif self._mode == "SEND":
            """Signal transmits via rf433 transmitter."""
            from libraries import RadioSignalClient
            rf_client = RadioSignalClient()
            rf_client.enable_transmission()
            rf_client.transmit_code(self._signal)
            rf_client.cleanup()

        else:
            # TODO: Log error of invalid hardware operation.
            pass


class HardwareSignal:
    def __init__(self):
        self.__hardware_client = None

    def transmit(self, signal):
        self.__hardware_client = _HardwareClient(name="hardware_tx", mode="SEND")
        self.__hardware_client.transmit(signal)

    def start_reception(self, output_queue):
        self.__hardware_client = _HardwareClient(name="hardware_rx", mode="RECEIVE")
        self.__hardware_client.receive(output_queue)
