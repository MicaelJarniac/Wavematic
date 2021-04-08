from abc import ABC, abstractmethod
from copy import copy
from typing import List, Literal, Optional

import numpy as np
import pandas as pd
from noise import pnoise1
from scipy import signal


class MissingTimeAxis(Exception):
    pass


class IncompatibleTimeAxisRates(Exception):
    pass


class TimeAxis:
    """Generates a time axis.

    Args:
        duration:
            Length, in units of time. Non-negative.
        rate:
            Sampling rate (points per unit of time). Non-negative.
        start:
            Initial time.
    """

    def __init__(self, duration: float, rate: float, start: float = 0.0):
        if duration < 0:
            raise ValueError("`duration` must be non-negative.")
        if rate < 0:
            raise ValueError("`rate` must be non-negative.")

        self.duration = duration
        self.rate = rate
        self.start = start

    def get(self) -> pd.Series:
        """Generate the time axis.

        Returns:
            Generated time axis.
        """

        start = self.start
        t = self.duration
        stop = start + t
        r = self.rate
        return pd.Series(np.linspace(start, stop, int(r * t)))

    def __repr__(self) -> str:
        base_args = {
            "duration": self.duration,
            "rate": self.rate,
            "start": self.start,
        }
        args_list = [f"{k}={repr(v)}" for k, v in base_args.items()]
        return f"{self.__class__.__name__}({', '.join(args_list)})"


class Signal(ABC):
    """Base class for signals.

    Args:
        ta:
            Time axis.
        name:
            Name to give to the signal.
    """

    def __init__(self, ta: Optional[TimeAxis] = None, name: Optional[str] = None):
        self.ta = ta
        self.name = name

    @abstractmethod
    def get(self, ta: Optional[TimeAxis] = None) -> pd.Series:
        pass


class Noise(Signal):
    """Generates noise.

    Args:
        ta:
            Time axis.
        amp:
            Amplitude.
        seed:
            Noise seed. Using the same seed generates the same noise
            signal.
        name:
            Name to give to the noise signal.
    """

    octaves = 20
    persistence = 5.0
    lacunarity = 2.0  # 1.5
    repeat = 1024

    def __init__(
        self,
        ta: Optional[TimeAxis] = None,
        amp: float = 0.0,
        seed: int = 0,
        name: str = "Noise",
    ):
        self.ta = ta
        self.amp = amp
        self.seed = seed
        self.name = name

    def get(self, ta: Optional[TimeAxis] = None) -> pd.Series:
        """Generate the noise signal.

        Args:
            ta:
                Time axis to use.

        Returns:
            Generated noise signal.
        """

        if ta is None:
            if self.ta is not None:
                ta = self.ta
            else:
                raise MissingTimeAxis(
                    "A `TimeAxis` must be either provided or set to `self.ta`."
                )
        ta_ser = ta.get()
        out = ta_ser.apply(
            lambda v: pnoise1(
                v,
                octaves=self.octaves,
                persistence=self.persistence,
                lacunarity=self.lacunarity,
                repeat=self.repeat,
                base=self.seed,
            )
            * self.amp
        )
        out.index = ta_ser
        out.name = self.name
        return out

    def __repr__(self) -> str:
        base_args = {
            "ta": self.ta,
            "amp": self.amp,
            "seed": self.seed,
            "name": self.name,
        }
        args_list = [f"{k}={repr(v)}" for k, v in base_args.items()]
        return f"{self.__class__.__name__}({', '.join(args_list)})"


class Wave(Signal):
    """Generates a waveform.

    Args:
        ta:
            Time axis.
        freq:
            Frequency (shouldn't be higher than half of the "sampling rate" on
            the time axis).
        amp:
            Amplitude.
        phase:
            Phase, in Pi (between 0.0 and 2.0).
        disp:
            Displacement.
        kind:
            The kind of wave to generate.
        name:
            The name to give to the wave signal.
        **kwargs:
            Extra arguments to be sent to the generator function.
            If `kind="square"`, `duty` can be given.
            If `kind="sawtooth"`, `width` can be given.
    """

    def __init__(
        self,
        ta: Optional[TimeAxis] = None,
        freq: float = 0.0,
        amp: float = 0.0,
        phase: float = 0.0,
        disp: float = 0.0,
        kind: Literal["sine", "square", "sawtooth"] = "sine",
        name: Optional[str] = None,
        **kwargs,
    ):
        self.ta = ta
        self.freq = freq
        self.amp = amp
        self.phase = phase
        self.disp = disp
        self.kind = kind
        self.name = name
        self.kwargs = kwargs

    def get(self, ta: Optional[TimeAxis] = None) -> pd.Series:
        """Generate the wave signal.

        Args:
            ta:
                Time axis to use. If not provided, `self.ta` will be used.

        Returns:
            Generated wave signal.
        """

        if ta is None:
            if self.ta is not None:
                ta = self.ta
            else:
                raise MissingTimeAxis(
                    "A `TimeAxis` must be either provided or set to `self.ta`."
                )
        ta_ser = ta.get()
        f = self.freq
        a = self.amp
        p = self.phase
        d = self.disp
        kind = self.kind
        name = self.name
        kwargs = self.kwargs

        pi = np.pi

        funcs = {
            "sine": np.sin,
            "square": signal.square,
            "sawtooth": signal.sawtooth,
        }

        base = (2 * pi * f * ta_ser) + (pi * p)

        func = funcs[kind]
        w = (func(base, **kwargs) * a) + d
        out = pd.Series(np.array(w), index=ta_ser)
        if name is not None:
            out.name = name
        return out

    def copy(self) -> "Wave":
        """Create a shallow copy of itself."""
        return copy(self)

    def __repr__(self) -> str:
        base_args = {
            "ta": self.ta,
            "freq": self.freq,
            "amp": self.amp,
            "phase": self.phase,
            "disp": self.disp,
            "kind": self.kind,
            "name": self.name,
        }
        base_args.update(self.kwargs)
        args_list = [f"{k}={repr(v)}" for k, v in base_args.items()]
        return f"{self.__class__.__name__}({', '.join(args_list)})"


class Wavematic:
    """Combines multiple signals.

    Args:
        ta:
            Base time axis.
        name:
            The name to give to the resulting signal.
    """

    ensure_compatible: bool = True
    force_self_ta: bool = False

    def __init__(self, ta: Optional[TimeAxis] = None, name: Optional[str] = None):
        self.signals: List[Signal] = []

        self.ta = ta
        self.name = name

    def copy(self) -> "Wavematic":
        """Create a shallow copy of itself."""
        return copy(self)

    def add_signal(self, sig: Signal) -> "Wavematic":
        """Add a signal.

        Args:
            sig:
                The signal to add.

        Returns:
            Reference to self.
        """

        if self.ensure_compatible and not self.check_compatible(sig):
            raise IncompatibleTimeAxisRates(
                "All `TimeAxis` must have the same `rate`, "
                "unless `self.ensure_compatible` is set to `False`."
            )
        self.signals.append(sig)
        return self

    def check_compatible(self, sig) -> bool:
        """Checks if the time axis of a given signal is compatible.

        Args:
            sig:
                The signal whose time axis should be checked.

        Returns:
            `False` if the given signal contains an incompatible
            time axis, `True` otherwise.
        """

        if sig.ta is not None:
            rate = sig.ta.rate
            rates = [s.ta.rate for s in self.signals if s.ta is not None]
            if self.ta is not None:
                rates.append(self.ta.rate)
            if rates.count(rate) != len(rates):
                return False
        return True

    def __iadd__(self, sig: Signal) -> "Wavematic":
        """Shortcut to add a signal."""
        self.add_signal(sig)
        return self

    def __add__(self, sig: Signal) -> "Wavematic":
        """Generate new Wavematic instance with added signal."""
        out = self.copy()
        out += sig
        return out

    def all_signals(self) -> pd.DataFrame:
        """Group all signals."""
        out = pd.DataFrame()
        for i, sig in enumerate(self.signals):
            force_self_ta = self.force_self_ta
            kwargs = dict()
            if sig.ta is None:
                force_self_ta = True
            if force_self_ta:
                kwargs["ta"] = self.ta
            s = sig.get(**kwargs)
            if s.name is None:
                s.name = i
            out = out.join(s, how="outer")
        return out

    def get(self) -> pd.Series:
        """Generate the signal resulting from the addition of contained signals."""
        out = self.all_signals().sum(axis=1)
        name = self.name
        if name is not None:
            out.name = name
        return out

    def __repr__(self) -> str:
        base_args = {
            "ta": self.ta,
            "name": self.name,
        }
        args_list = [f"{k}={repr(v)}" for k, v in base_args.items()]
        return f"{self.__class__.__name__}({', '.join(args_list)})"
