# Author: Saurav Gupta
# Date Created: Sep. 01, 2019

"""
File to be executed for starting the app.
For example:
    python /path/to/file/start.py
"""

import logging


from .env_settings import set_env_variables
from .execute import Initiation

if __name__ == "__main__":
    print("Hello..! Let's get started.")
    set_env_variables()  # It sets environment variables
    Initiation().initiate()  # Initiate different parts of system.

    while True:
        pass
