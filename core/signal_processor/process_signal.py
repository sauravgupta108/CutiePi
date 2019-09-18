# Author: Saurav Gupta
# Date Created: Sep. 17, 2019

"""
This module provides functionality to process cloud signals, change to hardware format and vice versa.
"""

from os import environ as env

from helper import decrypt_signal_from_cloud as decrypt, decode_hardware_signal as decode
import name_helper as nh


class ProcessCloudSignal:
    """
    It processes cloud signal. It decrypts, converts format and sends for transmission to hardware.
    """

    def process_signal(self, signal):
        """
        :param signal: dict type
        :return: None
        """
        decrypted_signal = decrypt(signal["message"])
        formatted_signal_for_hardware = self.__create_signal_for_hw(decrypted_signal)
        # transmit new signal to hardware.

    def __create_signal_for_hw(self, signal):
        is_valid_signal, signal_parts = self._is_valid_signal(signal)
        if is_valid_signal:
            signal_for_hardware = _SignalConversion().create_hardware_signal(signal_parts)
            return signal_for_hardware
        return None

    @staticmethod
    def _is_valid_signal(signal):
        signal_parts = signal.split("/")
        if signal_parts[0] == env["CLOUD_SOURCE"] and len(signal_parts) > nh.CLOUD_SIGNAL_NO_OF_PARTS:
            return True, signal_parts
        return False, None


class ProcessHardwareSignal:
    """
    It processes signal received from hardware. It decodes the signal, converts format for cloud
    and send for transmission.
    """

    def process_signal(self, signal):
        """
        :param signal: dict type
        :return: None
        """
        from cloud_engine import CloudSignal

        decoded_signal = decode(signal["message"])
        formatted_signal = self.__create_signal_for_cloud(decoded_signal)

        # Transmit signal to cloud
        CloudSignal().transmit_signal(formatted_signal)

    def __create_signal_for_cloud(self, signal):
        # TODO: Add code to create signal for cloud from hardware signal.
        return signal


class _SignalConversion:
    def __init__(self):
        pass

    def create_hardware_signal(self, cloud_signal_parts):
        """
        :param cloud_signal_parts: List of parts of signal
        e.g. [<zone>, <entity>, <id or group>, <action>]
        :return: command to send to hardware
        """
        # TODO: need to convert string data into stream of 0s & 1s for sending command to hardware.
        return ""

    def create_cloud_signal(self, hw_signal_parts):
        """
        :param hw_signal_parts:
        :return:  signal to transmit to cloud.
        e.g. <source>/<zone>/<entity>/<id or group>/<status>
        """
        return "%s/<zone>/<entity>/<id>/<status>" % env["CLOUD_SOURCE"]
