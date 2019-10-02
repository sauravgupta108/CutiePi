# Author: Saurav Gupta
# Date Created: Sep. 01, 2019

"""
Helper Module. Main functionality includes encrypting/decrypting messages for MQTT Broker, logging the events etc.
"""

from cryptography.fernet import Fernet
from os import environ as env

from .execute import EncryptionError, DecryptionError


# Encrypt the Signal to transmit to cloud
def encrypt_signal_for_cloud(raw_signal):
    if not raw_signal:
        raise EncryptionError("Invalid signal to encrypt.")

    signal = str(raw_signal)
    return Fernet(env["SECRET_KEY"].encode()).encrypt(signal.encode()).decode()


# Decrypt the signal received from cloud
def decrypt_signal_from_cloud(encrypted_signal):
    if not isinstance(encrypted_signal, str):
        raise DecryptionError("Invalid signal type received. Can not decrypt")

    return Fernet(env["SECRET_KEY"]).decrypt(encrypted_signal).decode()


# Decode signal from hardware
def decode_hardware_signal(encoded_signal):
    pass
