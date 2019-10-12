# Author: Saurav Gupta
# Date Created: Sep. 01, 2019
"""
This gives the power to send or receive radio signals at 433 Mhz.
"""
import time
import json
import os
from collections import namedtuple

from RPi import GPIO

MAX_CHANGES = 67

Protocol = namedtuple('Protocol', ['pulselength', 'sync_high', 'sync_low', 'zero_high',
                                   'zero_low', 'one_high', 'one_low'])
PROTOCOLS = (None,
             Protocol(350, 1, 31, 1, 3, 3, 1),
             Protocol(650, 1, 10, 1, 2, 2, 1),
             Protocol(100, 30, 71, 4, 11, 9, 6),
             Protocol(380, 1, 6, 1, 3, 3, 1),
             Protocol(500, 6, 14, 1, 2, 2, 1),
             Protocol(200, 1, 10, 1, 5, 1, 1))


class RadioSignalClient:
    """Representation of a GPIO RF device."""

    def __init__(self, tx_proto=1, tx_pulselength=None, tx_repeat=3, tx_length=24, rx_tolerance=80):
        """Initialize the RF device."""
        self.target_pin = None
        self.tx_enabled = False
        self.tx_proto = tx_proto
        self.tx_pulselength = tx_pulselength if tx_pulselength else PROTOCOLS[tx_proto].pulselength

        self.tx_repeat = tx_repeat
        self.tx_length = tx_length
        self.rx_enabled = False
        self.rx_tolerance = rx_tolerance
        # internal values
        self._rx_timings = [0] * (MAX_CHANGES + 1)
        self._rx_last_timestamp = 0
        self._rx_change_count = 0
        self._rx_repeat_count = 0
        # successful RX values
        self.rx_code = None
        self.rx_code_timestamp = None
        self.rx_proto = None
        self.rx_bitlength = None
        self.rx_pulselength = None

    def enable_transmission(self):
        """
        Enables the transmission of rf signal.
        :return: True/False depending on if transmission is enabled or not.
        """
        if self.rx_enabled:
            return False
        if not self.tx_enabled:
            with open(os.path.join(os.environ["CONFIG_DIR"], 'rf433_config.json')) as rf_conn:
                rf_config = json.load(rf_conn)
                self.target_pin = int(rf_config["tx_pin"])
                GPIO.setup(self.target_pin, GPIO.OUT)
                self.tx_enabled = True
        return self.tx_enabled

    def _disable_transmission(self):
        """Disable TX, reset GPIO."""
        if self.tx_enabled:
            # set up GPIO pin as input for safety
            GPIO.setup(self.target_pin, GPIO.IN)
            self.tx_enabled = False
        return not self.tx_enabled

    def transmit_code(self, code, tx_proto=None, tx_pulselength=None, tx_length=None):
        """
        Send a decimal code.
        Optionally set protocol, pulselength and code length.
        When none given reset to default protocol, default pulselength and set code length to 24 bits.
        """
        if tx_proto:
            self.tx_proto = tx_proto
        else:
            self.tx_proto = 1
        if tx_pulselength:
            self.tx_pulselength = tx_pulselength
        elif not self.tx_pulselength:
            self.tx_pulselength = PROTOCOLS[self.tx_proto].pulselength
        if tx_length:
            self.tx_length = tx_length
        elif self.tx_proto == 6:  # May be I need this protocol or tx_length
            self.tx_length = 32
        elif code > 16777216:
            self.tx_length = 32
        else:
            self.tx_length = 24

        raw_binary_str = "{0:b}".format(code).zfill(self.tx_length)

        if self.tx_proto == 6:
            nexa_code = ""
            for bit in raw_binary_str:
                if bit == '0':
                    nexa_code = nexa_code + "01"
                if bit == '1':
                    nexa_code = nexa_code + "10"
            raw_binary_str = nexa_code
            self.tx_length = 64
        return self._transmit_binary(raw_binary_str)

    def _transmit_binary(self, raw_binary_str):
        """Send a binary code."""
        for _ in range(0, self.tx_repeat):
            if self.tx_proto == 6:
                if not self._tx_sync():
                    return False
            for byte in range(0, self.tx_length):
                if raw_binary_str[byte] == '0':
                    if not self._tx_l0():
                        return False
                else:
                    if not self._tx_l1():
                        return False
            if not self._tx_sync():
                return False
        return True

    def _tx_l0(self):
        """Send a '0' bit."""
        if not 0 < self.tx_proto < len(PROTOCOLS):
            return False
        return self._tx_waveform(PROTOCOLS[self.tx_proto].zero_high,
                                 PROTOCOLS[self.tx_proto].zero_low)

    def _tx_l1(self):
        """Send a '1' bit."""
        if not 0 < self.tx_proto < len(PROTOCOLS):
            return False
        return self._tx_waveform(PROTOCOLS[self.tx_proto].one_high,
                                 PROTOCOLS[self.tx_proto].one_low)

    def _tx_sync(self):
        """Send a sync."""
        if not 0 < self.tx_proto < len(PROTOCOLS):
            return False
        return self._tx_waveform(PROTOCOLS[self.tx_proto].sync_high,
                                 PROTOCOLS[self.tx_proto].sync_low)

    def _tx_waveform(self, highpulses, lowpulses):
        """Send basic waveform."""
        if not self.tx_enabled:
            return False
        GPIO.output(self.target_pin, GPIO.HIGH)
        self._sleep((highpulses * self.tx_pulselength) / 1000000)
        GPIO.output(self.target_pin, GPIO.LOW)
        self._sleep((lowpulses * self.tx_pulselength) / 1000000)
        return True

    # For Reception....
    def enable_reception(self):
        """Enable RX, set up GPIO and add event detection."""
        if self.tx_enabled:
            return False
        if not self.rx_enabled:
            with open(os.path.join(os.environ["CONFIG_DIR"], 'rf433_config.json')) as rf_conn:
                rf_config = json.load(rf_conn)
                self.target_pin = int(rf_config["rx_pin"])
                GPIO.setup(self.target_pin, GPIO.OUT)
                self.rx_enabled = True
        return self.rx_enabled

    def _disable_reception(self):
        """Disable RX, remove GPIO event detection."""
        if self.rx_enabled:
            GPIO.remove_event_detect(self.target_pin)
            self.rx_enabled = False
        return True

    def rx_callback(self, target_pin):
        """RX callback for GPIO event detection. Handle basic signal detection."""
        timestamp = int(time.perf_counter() * 1000000)
        duration = timestamp - self._rx_last_timestamp

        if duration > 5000:
            if abs(duration - self._rx_timings[0]) < 200:
                self._rx_repeat_count += 1
                self._rx_change_count -= 1
                if self._rx_repeat_count == 2:
                    for pnum in range(1, len(PROTOCOLS)):
                        if self._rx_waveform(pnum, self._rx_change_count, timestamp):
                            break
                    self._rx_repeat_count = 0
            self._rx_change_count = 0

        if self._rx_change_count >= MAX_CHANGES:
            self._rx_change_count = 0
            self._rx_repeat_count = 0
        self._rx_timings[self._rx_change_count] = duration
        self._rx_change_count += 1
        self._rx_last_timestamp = timestamp

    def _rx_waveform(self, pnum, change_count, timestamp):
        """Detect waveform and format code."""
        code = 0
        delay = int(self._rx_timings[0] / PROTOCOLS[pnum].sync_low)
        delay_tolerance = delay * self.rx_tolerance / 100

        for i in range(1, change_count, 2):
            if (abs(self._rx_timings[i] - delay * PROTOCOLS[pnum].zero_high) < delay_tolerance and
               abs(self._rx_timings[i + 1] - delay * PROTOCOLS[pnum].zero_low) < delay_tolerance):
                code <<= 1
            elif (abs(self._rx_timings[i] - delay * PROTOCOLS[pnum].one_high) < delay_tolerance and
                  abs(self._rx_timings[i + 1] - delay * PROTOCOLS[pnum].one_low) < delay_tolerance):
                code <<= 1
                code |= 1
            else:
                return False

        if self._rx_change_count > 6 and code != 0:
            self.rx_code = code
            self.rx_code_timestamp = timestamp
            self.rx_bitlength = int(change_count / 2)
            self.rx_pulselength = delay
            self.rx_proto = pnum
            return True

        return False

    def cleanup(self):
        """Disable TX and RX and clean up GPIO."""
        if self.tx_enabled:
            self._disable_transmission()
        if self.rx_enabled:
            self._disable_reception()

    @staticmethod
    def _sleep(delay):
        _delay = delay / 100
        end = time.time() + delay - _delay
        while time.time() < end:
            time.sleep(_delay)
