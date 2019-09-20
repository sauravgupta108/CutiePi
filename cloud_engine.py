# Author: Saurav Gupta
# Date Created: Sep. 01, 2019

"""
This module publishes and subscribes data form and to MQTT Broker. In other words, sends and receive data to/from
MQTT broker.
(MQTT Broker: Mode of exchanging messages between end user app and hardware.)
"""

from threading import Thread

from execute.cutiepi_exceptions import CloudConnectionError


class CloudClient(Thread):
    """
    This class should only be accessed from "CloudSignal" class defined below this class.
    This class is used to create threads which eventually transmit and receive signals to cloud.
    """

    def __init__(self, name, mode):
        """
        :param name: Name of client
        :param mode: Type of client "SEND" or "RECEIVE
        """
        import inspect
        from paho.mqtt import client as mqtt
        from libraries.mqtt_engine import MqttClient
        from execute.cutiepi_exceptions import InvalidObjectCreation

        '''
        Get class name of caller method
        For python 3.5+
        inspect.stack() : A list of named tuples FrameInfo(frame, filename, lineno, function, code_context, index)
        inspect.stack()[1][0]: Frame object of caller.
        '''

        caller_frame_info = inspect.stack()[1]
        caller_id = caller_frame_info[0].f_locals['self'].__class__.__name__ + "." + caller_frame_info[3]
        if caller_id not in ["CloudSignal.transmit_signal", "CloudSignal.start_reception"]:
            # TODO: Need to think some alternative to hard coding the caller's <class>.<method> value.
            raise InvalidObjectCreation("Can not create object of class.")

        self.__CLOUD_CLIENT = MqttClient(mqtt.Client(client_id=name))
        self.__signal = None
        self.__channel = None

        if mode.strip() not in ('SEND', 'RECEIVE'):
            raise ValueError("Invalid Mode. Mode should be 'SEND' or 'RECEIVE'.")
        else:
            self.__client_type = mode

        Thread.__init__(self)

    def __set_channel(self):
        from os import environ as env
        if self.__client_type == 'SEND':
            self.__channel = env['MQTT_TRANSMISSION_CHANNEL']
        else:
            self.__channel = env['MQTT_RECEPTION_CHANNEL']

    def transmit(self, signal=""):
        assert (signal != "" and len(signal) > 0, "Not a valid signal %s" % signal)
        self.__set_channel()
        self.__signal = signal

        Thread.start(self)

    def receive(self, reception_queue):
        self.__set_channel()
        self.__CLOUD_CLIENT.set_output_queue(reception_queue)
        Thread.start(self)

    def run(self):
        if self.__client_type == "SEND":
            # This part runs the mqtt client (Thread) as Publisher (Transmitter).
            try:
                self.__CLOUD_CLIENT.transmit_signal(self.__channel, self.__signal)
            except CloudConnectionError:
                # TODO: Log error while transmitting signal
                self.disconnect()

        elif self.__client_type == "RECEIVE":
            # This part runs the mqtt client (Thread) as Subscriber (Receptor).
            try:
                self.__CLOUD_CLIENT.receive_signal(self.__channel)
            except CloudConnectionError:
                # TODO: Log Error during reception of signal from Cloud.
                self.disconnect()
        else:
            raise CloudConnectionError("Not a valid type of Cloud connector (It should be SEND or RECEIVE)")

    def is_published(self):
        # return self._CLOUD_CLIENT._pub_result
        pass

    def get_subscribed_messages(self):
        # return self._CLOUD_CLIENT._sub_msgs
        pass

    def disconnect(self):  # Use it only for subscriber, not for publisher.
        self.__CLOUD_CLIENT.disconnect_from_cloud()


class CloudSignal:
    """
    This class will actually send or receive signals via CloudClient class defined above.
    It encrypts the signal before transmission. It also decrypts the signal after reception and
    sends for further processing.
    """

    def __init__(self):
        self.__cloud_client = None

    def transmit_signal(self, signal):
        """
        It encrypts the Signal and then transmit over a respective channel.
        :param signal: signal to transmit
        :return: None
        """
        if not signal:
            raise ValueError("Invalid signal inputted.")

        from helper import encrypt_signal_for_cloud as encrypt
        self.__cloud_client = CloudClient(name="Cloud_Tx", mode="SEND")
        self.__cloud_client.transmit(encrypt(signal))

    def start_reception(self, output_queue):
        """
        This starts the reception of cloud signal on decided channel and
        starts a respective thread.
        :param output_queue: multiprocessing.Queue object, where to put messages after reception.
        :return: None
        """
        self.__cloud_client = CloudClient(name="Cloud_Tx", mode="RECEIVE")
        self.__cloud_client.receive(output_queue)
