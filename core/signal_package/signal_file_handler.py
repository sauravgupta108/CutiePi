# Author: Saurav Gupta
# Date Created: Sep. 17, 2019

"""
This file handle all file operations where signals are logging.
"""

import tables as tb
import time
from os import environ as env, path

from ... import name_helper as nh
from . import CloudSignal, HardwareSignal


class SignalFileHandler:
    def __init__(self):
        pass

    @staticmethod
    def create_file():
        with tb.open_file(path.join(env["HOME"] + nh.SIGNAL_FILE), "w", nh.SIGNAL_FILE_TITLE) as signals_file:

            cloud_group = signals_file.create_group(signals_file.root,
                                                    nh.CLOUD_SIGNAL_GROUP_NAME,
                                                    nh.CLOUD_SIGNAL_GROUP_TITLE)
            hw_group = signals_file.create_group(signals_file.root,
                                                 nh.HARDWARE_SIGNAL_GROUP_NAME,
                                                 nh.HARDWARE_SIGNAL_GROUP_TITLE)

            cloud_signals = signals_file.create_table(cloud_group,
                                                      nh.CLOUD_SIGNAL_TABLE_NAME,
                                                      CloudSignal,
                                                      nh.CLOUD_SIGNAL_TABLE_TITLE)
            hw_signals = signals_file.create_table(hw_group,
                                                   nh.HARDWARE_SIGNAL_TABLE_NAME,
                                                   HardwareSignal,
                                                   nh.HARDWARE_SIGNAL_TABLE_TITLE)

    def save_cloud_signal(self, file, name=0, message="", protocol="mqtt", source_type="MQTT Broker"):
        cloud_signals = self._get_signal_table(file, nh.CLOUD_SIGNAL_GROUP_NAME)
        cloud_signal_record = cloud_signals.row

        cloud_signal_record["name"] = name
        cloud_signal_record["message"] = message
        cloud_signal_record["protocol"] = protocol
        cloud_signal_record["source_type"] = source_type
        cloud_signal_record["incoming_time"] = time.time()

        cloud_signal_record.append()
        file.flush()

    def save_hardware_signal(self, file, name=0, message="", protocol="Bluetooth", device_type="B/T"):
        hw_signals = self._get_signal_table(file, nh.HARDWARE_SIGNAL_GROUP_NAME)
        hw_signal_record = hw_signals.row

        hw_signal_record["name"] = name
        hw_signal_record["message"] = message
        hw_signal_record["protocol"] = protocol
        hw_signal_record["device_type"] = device_type
        hw_signal_record["incoming_time"] = time.time()

        hw_signal_record.append()
        file.flush()

    @staticmethod
    def _get_signal_table(file, group):
        """
        It will only work for Level 1 and one table per group.
        e.g. Hierarchy
        root:
            group-1:
                table-1.
            group-2:
                table-2.
            .
            .
        @param file: Database file (.h5 or similar) instance where all signals are saved.
        @param group: Group name (String)
        @return: Signal Table child of signal_group
        """

        for signal_group_name, signal_group_instance in file.root._v_children.items():
            if signal_group_name == group:
                signal_tables = signal_group_instance._v_children.values()
                if len(signal_tables) == 1 and isinstance(list(signal_tables)[0], tb.Table):
                    return list(signal_tables)[0]
                break

        return None
