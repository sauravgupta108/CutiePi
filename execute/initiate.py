# Author: Saurav Gupta
# Date Created: Sep. 01, 2019

"""
This file initiate different parts.
"""

import RPi.GPIO as GPIO
from multiprocessing import Queue as que

from .cutiepi_exceptions import *
from monitor import LcdEngine
import env_settings as ev


class Initiation:
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        ev.set_env_variables()

        self.lcd = LcdEngine()

        # Set queues for different sections.
        self.__cloud_signal_receiver_queue = que()
        self.__hardware_signal_receiver_queue = que()
        self.__signals_to_process_queue = que()

        # Signal file create.
        from core.signal_package import SignalFileHandler
        file_handler = SignalFileHandler()
        file_handler.create_file()

    def __initiate_monitor(self):
        from monitor import SevenSegment, Led
        svn_seg = SevenSegment()
        led = Led()

        if self.lcd.prepare():
            self.lcd.display_message("Hello..! Welcome to the IoT world.")
        else:
            raise MonitorInitiationError("Error while initiating LCD.")
        # TODO: Initiate Seven segment display and LEDs
        return True

    def __start_signal_recorder(self):
        """
        It starts a parallel process for recording signals received from cloud and hardware.
        :return: None
        """
        from core import ReceivedSignalsLogger
        signal_recorder = ReceivedSignalsLogger(self.__cloud_signal_receiver_queue,
                                                self.__hardware_signal_receiver_queue,
                                                self.__signals_to_process_queue)
        signal_recorder.start()

    def __start_cloud_listener(self):
        """
        It starts a thread to receive signals from cloud.
        :return: None
        """
        from cloud_engine import CloudSignal
        cloud_signal_thread = CloudSignal()
        cloud_signal_thread.start_reception(self.__cloud_signal_receiver_queue)

    def __start_hardware_listener(self):
        """
        It starts a thread to receive signals from hardware via bluetooth.
        :return: None
        """
        from hw_controller import HardwareSignal
        hardware_signal_thread = HardwareSignal()
        hardware_signal_thread.start_reception(self.__hardware_signal_receiver_queue)

    def __start_signal_processor(self):
        """
        It starts parallel process to process signals in "signals_to_process_queue"
        :return: None
        """
        from core.signal_processor import OutputSignalQueueProcessor
        signal_processor = OutputSignalQueueProcessor(self.__signals_to_process_queue)
        signal_processor.start()

    def initiate(self):
        # Order of calling methods matters.
        self.__initiate_monitor()  # TODO: It could raise MonitorInitiationError. Need to handle
        self.__start_signal_recorder()
        self.__start_cloud_listener()
        self.__start_hardware_listener()
        self.__start_signal_processor()
