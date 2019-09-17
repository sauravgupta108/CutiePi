# Author: Saurav Gupta
# Date Created: Sep. 17, 2019

"""
This module provides functionality to process cloud signals, change to hardware format and vice versa.
"""

from helper import decrypt_signal_from_cloud as decrypt, decode_hardware_signal as decode


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
        # TODO: Add code to create signal for hardware according to cloud
        return signal


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
