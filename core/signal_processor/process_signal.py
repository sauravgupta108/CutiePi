# Author: Saurav Gupta
# Date Created: Sep. 17, 2019

"""
This module provides functionality to process cloud signals, change to hardware format and vice versa.
"""

from os import environ as env

from helper import decrypt_signal_from_cloud as decrypt, decode_hardware_signal as decode
from execute.cutiepi_exceptions import InvalidCloudSignal, DecryptionError
from execute.cutiepi_exceptions import InvalidHardwareSignal, CloudConnectionError
import name_helper as nh
import message_conversion_helper as msg_hlp


class ProcessCloudSignal:
    """
    It processes cloud signal. It decrypts, converts format and sends for transmission to hardware.
    """

    def process_signal(self, signal):
        """
        :param signal: dict type
        :return: None
        """
        try:
            decrypted_signal = decrypt(signal["message"])
            formatted_signal_for_hardware = self.__create_signal_for_hw(decrypted_signal)
            # TODO: transmit new signal to hardware.
        except DecryptionError:
            # TODO: Log error while decrypting signal received from cloud.
            pass
        except InvalidCloudSignal:
            # TODO: Log error while concerting cloud signal to command for hardware.
            pass

    def __create_signal_for_hw(self, signal):
        is_valid_signal, signal_parts = self._is_valid_signal(signal)
        if is_valid_signal:
            return _SignalConversion().create_hardware_signal(signal_parts)
        return None

    @staticmethod
    def _is_valid_signal(signal):
        try:
            signal_parts = signal.split("/")
            if signal_parts[0] == env["CLOUD_SOURCE"] and len(signal_parts) == nh.CLOUD_SIGNAL_NO_OF_PARTS:
                return True, signal_parts
            return False, None
        except AttributeError:
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

        try:
            decoded_signal = decode(signal["message"])
            formatted_signal = self.__create_signal_for_cloud(decoded_signal)

            # Transmit signal to cloud
            CloudSignal().transmit_signal(formatted_signal)
        except InvalidHardwareSignal:
            # TODO: Log error while converting hardware signal to signal for cloud.
            pass
        except CloudConnectionError:
            # TODO: Log error while transmitting signal to cloud.
            pass

    def __create_signal_for_cloud(self, signal):
        is_valid_signal, signal_in_parts = self._is_valid(signal)
        if is_valid_signal:
            return _SignalConversion().create_cloud_signal(signal_in_parts)
        return None

    @staticmethod
    def _is_valid(signal):
        try:
            signal_parts = signal.split("&")
            if signal_parts[0] == env["HARDWARE_SOURCE"] and len(signal_parts[1]) == nh.HARDWARE_SIGNAL_LENGTH:
                return True, signal_parts
            return False, None
        except AttributeError:
            return False, None


class _SignalConversion:
    def __init__(self):
        pass

    @staticmethod
    def create_hardware_signal(cloud_signal_parts):
        """
        Format of Hardware Signal: zoneEntityAll_or_idIdAction (String of numbers)
            zone: 00-99 (2-digit zone number (1- Invalid, 01- Valid)
            Entity: {a, b} where a and b are 1-digit number representing Entity (i.e. Light or Motor)
                as defined in name_helper.py file.
            All_or_id: {0, 1} (where 0 means all and 1 means id)
            Id: 3-digit decimal number (where 000 means all and 001-999 id number)
                (1, 12, 54, etc. Invalid values, 001, 012, 054, 456, etc. Valid values)
            Action: {0, 1} (where 0 means off and 1 means on)

        :param cloud_signal_parts: List of parts of signal
        e.g. [<source>, <zone>, <entity>, <id or all>, <action>]
        :return: command to send to hardware (Controlling purpose)
        """

        try:
            zone = int(cloud_signal_parts[1])
        except ValueError:
            # TODO: Log Error
            raise InvalidCloudSignal("Invalid Zone Number. An Integer between 1 and 99 expected.")

        try:
            all_or_id_part = int(cloud_signal_parts[3])
        except ValueError:
            raise InvalidCloudSignal("Invalid Entity ID.")

        if not 0 < zone <= msg_hlp.MAX_ZONES:
            raise InvalidCloudSignal("Invalid Zone.")
        else:
            zone = str(zone).zfill(msg_hlp.ZONE_NUMBERS_PADDING)

        if cloud_signal_parts[2] not in [nh.CLOUD_SIGNAL_LIGHT_ENTITY, nh.CLOUD_SIGNAL_MOTOR_ENTITY]:
            raise InvalidCloudSignal("Invalid Entity name received.")
        else:
            if cloud_signal_parts[2] == nh.CLOUD_SIGNAL_LIGHT_ENTITY:
                entity_no = nh.CLOUD_SIGNAL_LIGHT_ENTITY_NUMBER
            else:
                entity_no = nh.CLOUD_SIGNAL_MOTOR_ENTITY_NUMBER

        if not 0 <= all_or_id_part <= msg_hlp.MAX_ENTITY_ID:
            raise InvalidCloudSignal("Invalid Entity id or group")
        else:
            entity_id = str(all_or_id_part).zfill(msg_hlp.ENTITY_ID_PADDING)
            all_or_id = str(0) if all_or_id_part == 0 else str(1)

        if cloud_signal_parts[4] not in [nh.ON, nh.OFF]:
            raise InvalidCloudSignal("Invalid action value received.")
        else:
            action = 1 if cloud_signal_parts[4] == nh.ON else 0

        return "%s%s%s%s%s" % (zone, str(entity_no), all_or_id, entity_id, action)

    @staticmethod
    def create_cloud_signal(hw_signal):
        """
        Format of actual signal from hardware (zzeiiivvv) :
            string of some specified length ( As specified in name_handler.py)
            zz: zone number (int between 1 and 99 with padding not 1 but 01)
            e: entity number (specific number representing entity as per name_handler.py)
            ii: 2 digit number representing id of the entity
                00: all ( 0, 1, 4, etc. invalid, 00, 01, 04, etc. valid)
            vvv: a three digit number representing analog value of entity between 000-999
                1, 52, 66, etc Invalid values, 001, 052, 066, etc. : Valid Values.
        :param hw_signal: List type ([source, signal])
        :return:  signal to transmit to cloud. (Monitoring Purpose)
        e.g. <source>/<zone>/<entity>/<id or group>/<status>
        """
        hw_signal_actual = hw_signal[1]
        try:
            zone = int(hw_signal_actual[:2])
            entity = int(hw_signal_actual[2])
            id_or_all = int(hw_signal_actual[3:6])
            value = int(hw_signal_actual[6:])
        except ValueError:
            # TODO: Log error
            raise InvalidHardwareSignal("Invalid signal from Hardware.")

        if not 0 < zone <= msg_hlp.MAX_ZONES:
            raise InvalidHardwareSignal("Invalid Zone Number")
        else:
            zone = str(zone).zfill(msg_hlp.ZONE_NUMBERS_PADDING)

        if entity not in [nh.CLOUD_SIGNAL_TANK_ENTITY_NUMBER, nh.CLOUD_SIGNAL_DUSTBIN_ENTITY_NUMBER]:
            raise InvalidHardwareSignal("Invalid entity.")
        else:
            if entity == nh.CLOUD_SIGNAL_TANK_ENTITY_NUMBER:
                entity = nh.CLOUD_SIGNAL_TANK_ENTITY
            else:
                entity = nh.CLOUD_SIGNAL_DUSTBIN_ENTITY

        if not 0 <= id_or_all <= msg_hlp.MAX_ENTITY_ID:
            raise InvalidHardwareSignal("Invalid entity ID.")
        else:
            if id_or_all == 0:
                id_or_all = "0".zfill(msg_hlp.ENTITY_ID_PADDING)
            else:
                id_or_all = str(id_or_all).zfill(msg_hlp.ENTITY_ID_PADDING)

        if not 0 <= value <= msg_hlp.MAX_ANALOG_VALUE:
            raise InvalidHardwareSignal("Invalid value.")
        else:
            value = str(value).zfill(msg_hlp.ANALOG_VALUE_PADDING)

        return "%s/%s/%s/%s/%s" % (env["CLOUD_SOURCE"], zone, entity, id_or_all, value)
