"""
== Option 1 ==
To permit users to use `from blenderfea.src import MyOperator, MyPanel` add the following:

from .operators import MyOperator
from .panels import MyPanel

__all__ = ["MyOperator", "MyPanel"]  # Optional: for "from src import *"

== Option 2 ==



"""

from .. import bl_info
__all__ = ['bl_info']


GRAVITY = 9.81 # m/s^2
PI = 3.14159

DEFAULT_UNITS = {
    'time': 's',
    'length': 'm',
    'mass': 'kg',
    'force': 'N',
    'moment': 'Nm',
    'pressure': 'Pa',
    'temperature': 'K',
    'velocity': 'm/s',
    'acceleration': 'm/s^2',
    'energy': 'J',
    'power': 'W',
    'angle': 'rad',
    }


def get_default_units():
    return DEFAULT_UNITS

