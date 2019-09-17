# Author: Saurav Gupta
# Date Created: Sep. 17, 2019

"""
File to record all received signals from both cloud and hardware.
It uses Process from multiprocessing module.
It keeps on checking queues for signals received, store to .h5 file and
puts the messages (in distinguishable format) to signals_to_process_queue.
"""

from multiprocessing import Process, Queue
import tables as tb
from os import environ as env, path

import name_helper as nh


class ReceivedSignalsLogger(Process):
    def __init__(self, from_cloud_queue, from_hardware_queue, to_process_queue):
        self._file = path.join(env["HOME"], nh.SIGNAL_FILE)
        self._from_cloud_queue = from_cloud_queue
        self._from_hardware_queue = from_hardware_queue
        self._to_process_queue = to_process_queue
        Process.__init__(self)

    def run(self):
        from .signal_package import SignalFileHandler
        signal_handler = SignalFileHandler()
        while True:
            with tb.open_file(self._file, "r+") as signals_file:
                try:
                    cloud_signal = self._from_cloud_queue.get(timeout=nh.QUEUE_WAIT_TIME)
                    signal_handler.save_cloud_signal(signals_file,
                                                     1,  # TODO: Need to provide dynamic Serial Number
                                                     cloud_signal["message"],
                                                     cloud_signal["protocol"],
                                                     cloud_signal["source_type"]
                                                     )
                    self._to_process_queue.put((nh.CLOUD_SIGNAL_PREFIX, cloud_signal))
                except Queue.Empty:
                    pass

                try:
                    hw_signal = self._from_hardware_queue.get(timeout=nh.QUEUE_WAIT_TIME)
                    signal_handler.save_hardware_signal(signals_file,
                                                        2,  # TODO: Need to provide dynamic Serial Number
                                                        hw_signal["message"],
                                                        hw_signal["protocol"],
                                                        hw_signal["source_type"]
                                                        )
                    self._to_process_queue.put((nh.HARDWARE_SIGNAL_PREFIX, hw_signal))
                except Queue.Empty:
                    pass

    def terminate(self):
        Process.terminate(self)
