# Author: Saurav Gupta
# Date Created: Sep. 17, 2019

"""
It runs as a parallel process (multiprocessing.Process).
It keeps on checking signals_to_process_queue, differentiate types of signals and
sends for further processing.
"""

from multiprocessing import Process

from ... import name_helper as nh


class OutputSignalQueueProcessor(Process):
    def __init__(self, queue_signals_to_process):
        """
        :param queue_signals_to_process: multiprocessing.Queue object
        """
        self._queue_signals_to_process = queue_signals_to_process
        Process.__init__(self)

    def run(self):
        while True:
            signal_from_queue = self._queue_signals_to_process.get()
            if signal_from_queue[0].strip() == nh.CLOUD_SIGNAL_PREFIX:
                from .process_signal import ProcessCloudSignal
                ProcessCloudSignal().process_signal(signal_from_queue[1])

            elif signal_from_queue[0].strip() == nh.HARDWARE_SIGNAL_PREFIX:
                from .process_signal import ProcessHardwareSignal
                ProcessHardwareSignal().process_signal(signal_from_queue[1])

            else:
                # TODO: Log invalid signal got from queue
                pass

    def terminate(self):
        self.terminate()
