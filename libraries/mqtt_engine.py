# Author: Saurav Gupta
# Date Created: Sep. 01, 2019

"""
This module provides a way to publish and subscribe messages using MQTT protocol.
"cloud" here means remote MQTT Broker.
"""

import time
import os

from ..execute.cutiepi_exceptions import CloudConnectionError


class MqttClient:
    """
    It deals with MQTT Broker directly.
    """

    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.__connection_ok = False
        self.__msg_sent = False
        self.__sub_result = False
        self.__sub_msgs = []
        self.__qos = 0
        self.__output_queue = None

    def set_output_queue(self, output_queue):
        self.__output_queue = output_queue

    def __on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            raise CloudConnectionError("MQTT Broker connection failed.")
        else:
            self.__connection_ok = True

    def __on_disconnect(self, client, userdata, flags):
        self.mqtt_client.loop_stop()

    def __on_log(self, client, userdata, level, buf):
        # self.logger.debug("Client: %s -- %s" % client, buf)
        pass

    def __on_transmit(self, *args):
        self.__msg_sent = True

    def __on_reception(self, *args):
        self.__sub_result = True

    def __on_message(self, client, userdata, message):
        """
        It puts the received messages onto output_queue.
        :param message: Message received from Broker.
        :return: None
        """
        self.__sub_msgs.append(str(message.payload))
        signal_received = {
            "message": message.payload.decode(),
            "protocol": "MQTT",
            "source_type": "Remote_MQTT_Broker"
        }
        if self.__output_queue:
            self.__output_queue.put(signal_received)

    def __connect_to_cloud(self):
        """
        Connects to MQTT broker and returns a MQTT Client object.
        """

        self.mqtt_client.username_pw_set(os.environ['MQTT_USERNAME'], os.environ['MQTT_PASSWORD'])

        self.mqtt_client.on_connect = self.__on_connect
        self.mqtt_client.on_disconnect = self.__on_disconnect
        self.mqtt_client.on_publish = self.__on_transmit
        self.mqtt_client.on_subscribe = self.__on_reception
        self.mqtt_client.on_message = self.__on_message
        self.mqtt_client.on_log = self.__on_log

        try:
            self.mqtt_client.connect(
                os.environ['MQTT_HOST'],
                int(os.environ['MQTT_PORT']),
                int(os.environ['MQTT_KEEPALIVE'])
            )
        except:
            raise CloudConnectionError("MQTT Broker connection failed.")

        time.sleep(0.2)

    def transmit_signal(self, channel, message):
        self.__connect_to_cloud()

        try:
            self.mqtt_client.loop_start()
            time.sleep(0.5)
            self.mqtt_client.publish(topic=channel, payload=str(message), qos=self.__qos)
            time.sleep(0.1)
            self.disconnect_from_cloud()
        except:
            self.disconnect_from_cloud()
            raise CloudConnectionError("Error occurred during transmission of signal to channel: ", channel)

    def receive_signal(self, channel):
        self.__connect_to_cloud()
        try:
            self.mqtt_client.subscribe(channel, qos=self.__qos)
            self.mqtt_client.loop_forever()
        except:
            self.disconnect_from_cloud()
            raise CloudConnectionError("Error occurred during reception of signal from channel: ", channel)

    def disconnect_from_cloud(self):
        self.mqtt_client.disconnect()
        time.sleep(0.1)
