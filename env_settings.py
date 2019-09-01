# Author: Saurav Gupta
# Date Created: Sep. 01, 2019

"""
Environment settings file for sensitive data.
"""

from os import environ as env

# Home Directory (Linux Path not for windows)
env["HOME_DIR"] = "/opt/app/CutiePi"
env["LOG_HOME_DIR"] = "/opt/app/CutiePi/logs"
env["CONFIG_DIR"] = "/opt/app/CutiePi/code/config"

# MQTT Broker configurations
env["MQTT_HOST"] = "192.168.2.130"
env["MQTT_KEEPALIVE"] = 60
env["MQTT_USERNAME"] = "tech"
env["MQTT_PASSWORD"] = "mahindra"
env["MQTT_QOS"] = 0

# MQTT Signal Configurations
env["MQTT_SOURCE"] = "smacty_j>6@9P~B"
env["MQTT_MSG_SPLITTER"] = "/"
env["MQTT_TRANSMISSION_CHANNEL"] = "rpi_broker_tx"
env["MQTT_RECEPTION_CHANNEL"] = "rpi_broker_rx"

# Bluetooth Device Configurations (SrNo_type_property)
env["A_HC05_NAME"] = "HC-05"
env["A_HC05_DEVICE_ID"] = "98:D3:36:80:F3:72"
env["A_HC05_PORT"] = 1

# Bluetooth Signal Configurations
env["A_HC05_SIGNAL_LEN"] = 15
env["A_HC05_SIGNAL_PRE"] = "zSi3U"

# Secret Key (use for encryption and decryption)
env["SECRET_KEY"] = "W2kzcCetwfkns3koreNUzjUbE-r_pHYkd73FLl68x7M="
