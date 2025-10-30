"""
== Option 1 ==
To permit users to use `from blenderfea.src import MyOperator, MyPanel` add the following:

from .operators import MyOperator
from .panels import MyPanel

__all__ = ["MyOperator", "MyPanel"]  # Optional: for "from src import *"

== Option 2 ==



"""

import logging

# Create a logger for the package
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)  # Or another level like DEBUG

# Add a handler to send logs to the console (optional)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

log.info("BlenderFEA src package initialized")

# ==================

GRAVITY = 9.81 # m/s^2
PI = 3.14159

DEFAULT_UNITS = {
    'time': 's',
    'length': 'm',
    'mass': 'kg',
    'force': 'N',
    'pressure': 'Pa',
    'temperature': 'K',
    'velocity': 'm/s',
    'acceleration': 'm/s^2',
    'torque': 'N-m',
    'energy': 'J',
    'power': 'W',
    'angle': 'rad',
    }


def get_default_units():
    return DEFAULT_UNITS

