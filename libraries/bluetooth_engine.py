# Author: Saurav Gupta
# Date Created: Sep. 01, 2019

"""
This file provides various methods which can be used to harness the capability of Bluetooth.
"""

from os import environ as env
from time import sleep
import bluetooth as bt

import name_helper as nh


class BluetoothClient:
    def __init__(self):
        self.bt_sock = bt.BluetoothSocket(bt.RFCOMM)
        self.__output_queue = None

    def set_output_queue(self, output_queue):
        self.__output_queue = output_queue

    def _put_signal_onto_queue(self, signal):
        """
        It accepts the raw signal string received and convert to dict format with additional info
        and puts the formatted signal onto the queue for further processing.
        :param signal: raw signal string or sting in form of bytes.
        :return: None
        """
        signal = {
            "message": signal.decode(),
            "protocol": "BLUETOOTH",
            "source_type": "Bluetooth_Device"
        }
        self.__output_queue.put(signal)

    def _connect_to_hardware(self):
        try:
            self.bt_sock.connect((env["A_HC05_DEVICE_ID"], int(env["A_HC05_PORT"])))
            return True
        except bt.btcommon.BluetoothError:
            # TODO: Log bluetooth connection error
            return False

    @staticmethod
    def _is_valid_signal_received(signal):
        """
        It validates signal received from hardware via Bluetooth.
        :param signal: signal received from hardware.
        :return: True or False
        """
        try:
            return len(signal.decode()) == nh.HARDWARE_SIGNAL_LENGTH
        except AttributeError:
            return len(signal) == nh.HARDWARE_SIGNAL_LENGTH

    def receive_signal(self):
        if self._connect_to_hardware():
            while True:
                try:
                    signal_received = self.bt_sock.recv(nh.BLUETOOTH_SIGNAL_LIMIT)
                    self._put_signal_onto_queue(signal_received) if self._is_valid_signal_received(
                        signal_received) else ""
                    sleep(nh.BLUETOOTH_SIGNAL_WAIT_TIME)

                except bt.btcommon.BluetoothError:
                    # TODO: Log error while receiving signal over bluetooth
                    self.terminate_connection()
        else:
            # TODO: Log error in attempting Bluetooth connection.
            pass

    def terminate_connection(self):
        self.bt_sock.close()
