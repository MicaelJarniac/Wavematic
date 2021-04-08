"""Simple wave generator"""

__version__ = "0.1.1"

from .wave import (
    IncompatibleTimeAxisRates,
    MissingTimeAxis,
    Noise,
    TimeAxis,
    Wave,
    Wavematic,
)

__all_exports = [
    IncompatibleTimeAxisRates,
    MissingTimeAxis,
    Noise,
    TimeAxis,
    Wave,
    Wavematic,
]

for e in __all_exports:
    e.__module__ = __name__

__all__ = [e.__name__ for e in __all_exports]
