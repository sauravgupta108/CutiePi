# Author: Saurav Gupta
# Date Created: Sep. 01, 2019

"""
With the help of this we can display data on the 16*2 LCD.
"""

import json
import os
import time

import RPi.GPIO as GPIO

from execute.cutiepi_exceptions import MonitorOperationError


class LcdEngine:
    def __init__(self):
        with open(os.path.join(os.environ["CONFIG_DIR"], 'lcd_connections.json')) as lcd_conn:
            self.__pins = json.load(lcd_conn)
        for pin in self.__pins.keys():
            GPIO.setup(int(self.__pins[pin]), GPIO.OUT)

    def prepare(self):
        if self.lcd_start() and self.lcd_clear() and self.cursor_blink() and self.go_to_first_line():
            return True
        return False

    def command(self, command):
        GPIO.output(int(self.__pins["rs"]), False)
        write_ok = self.write_to_lcd_8_bits(bin(command))
        self.signal_green()
        return write_ok

    def display_message(self, message):
        message = str(message)  # Making message string explicitly.
        self.lcd_clear()  # Clear LCD screen before displaying any message.
        count_chars = 0
        for i in message:
            if count_chars == 16:
                self.go_to_second_line()
            if count_chars == 32:
                self.go_to_first_line()
                count_chars = 0

            if self.display_char(i):
                count_chars += 1
            else:
                raise MonitorOperationError("Error occurred during message display on LCD.")

    def display_char(self, char):
        assert len(char) == 1
        GPIO.output(int(self.__pins["rs"]), True)
        disp_ok = self.write_to_lcd_8_bits(bin(ord(char)))
        self.signal_green()
        return disp_ok

    def write_to_lcd_8_bits(self, bits):
        bits = self.pad_bits(bits)
        bits = bits[::-1]
        for i in range(8):
            GPIO.output(int(self.__pins["d" + str(i)]), bool(int(bits[i])))
        return True

    @staticmethod
    def pad_bits(bits):
        raw_bits = bits.lstrip('0b')
        assert (8 - len(raw_bits)) >= 0
        return '0' * (8 - len(raw_bits)) + raw_bits

    def signal_green(self):
        GPIO.output(int(self.__pins["en"]), True)
        time.sleep(0.01)
        GPIO.output(int(self.__pins["en"]), False)

    # Utility methods.
    def lcd_start(self):
        return self.command(0x38)

    def lcd_clear(self):
        return self.command(0x01)

    def cursor_blink(self):
        return self.command(0x0c)

    def go_to_first_line(self):
        return self.command(0x80)

    def go_to_second_line(self):
        return self.command(0xc0)

    def right_shift(self):
        return self.command(0x1c)

    def left_shift(self):
        return self.command(0x18)

    @staticmethod
    def clean():
        GPIO.cleanup()
