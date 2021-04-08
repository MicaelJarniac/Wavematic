import pytest
from pytest import raises


from wavematic import TimeAxis

"""
ta = TimeAxis(duration=0.2, rate=1600.0, start=0.0)
sample = Wavematic(ta)
sample.add_signal(Wave(freq=10.0, amp=0.8, phase=0.0))
sample.add_signal(Wave(freq=20.0, amp=0.2, phase=0.5))
sample.add_signal(Wave(freq=25.0, amp=0.2, phase=0.5))
sample.add_signal(Wave(freq=45.0, amp=0.2, phase=0.5))
sample.add_signal(Wave(freq=120.0, amp=0.2, phase=0.0))
sig_noise = Noise(amp=0.5)
sample.add_signal(sig_noise)
sample.add_signal(Wave(disp=1.0, name="Displacement"))

sample.all_signals().plot()

sample.get().plot()

sig_noise.amp = 0.0
sample.get().plot()

wa = Wave(ta=ta, freq=20, amp=1.0, phase=0.0, disp=0.0, duty=0.1, kind="square")
wa.get().plot()
print(repr(wa))
"""


def test_timeaxis():
    ta = TimeAxis(duration=2.0, rate=10.0)
    ta_ser = ta.get()
    assert len(ta_ser) == 20
    assert ta_ser.iloc[0] == 0.0
    assert ta_ser.iloc[-1] == 2.0
    assert repr(ta) == "TimeAxis(duration=2.0, rate=10.0, start=0.0)"

    ta.start = 5.0
    ta_ser = ta.get()
    assert len(ta_ser) == 20
    assert ta_ser.iloc[0] == 5.0
    assert ta_ser.iloc[-1] == 7.0
    assert repr(ta) == "TimeAxis(duration=2.0, rate=10.0, start=5.0)"

    with raises(TypeError):
        ta = TimeAxis(duration="bad", rate=1.0, start=1.0)
        ta.get()

    with raises(TypeError):
        ta = TimeAxis(duration=1.0, rate="bad", start=1.0)
        ta.get()

    with raises(TypeError):
        ta = TimeAxis(duration=1.0, rate=1.0, start="bad")
        ta.get()

    with raises(TypeError):
        ta = TimeAxis(duration="bad", rate="bad", start=1.0)
        ta.get()

    with raises(TypeError):
        ta = TimeAxis(duration="bad", rate=1.0, start="bad")
        ta.get()

    with raises(TypeError):
        ta = TimeAxis(duration=1.0, rate="bad", start="bad")
        ta.get()

    with raises(TypeError):
        ta = TimeAxis(duration="bad", rate="bad", start="bad")
        ta.get()

    with raises(ValueError):
        ta = TimeAxis(duration=-1.0, rate=1.0, start=1.0)

    with raises(ValueError):
        ta = TimeAxis(duration=1.0, rate=-1.0, start=1.0)

    with raises(ValueError):
        ta = TimeAxis(duration=-1.0, rate=-1.0, start=1.0)

    ta = TimeAxis(duration=1.0, rate=10.0, start=-1.0)
    ta_ser = ta.get()
    assert len(ta_ser) == 10
    assert ta_ser.iloc[0] == -1.0
    assert ta_ser.iloc[-1] == 0.0
    assert repr(ta) == "TimeAxis(duration=1.0, rate=10.0, start=-1.0)"


values = [0.0, 0.1, 1.0, 10.0]


@pytest.mark.parametrize("start", values)
@pytest.mark.parametrize("rate", values)
@pytest.mark.parametrize("duration", values)
def test_timeaxis_multi(duration, rate, start):
    ta = TimeAxis(duration=duration, rate=rate, start=start)
    assert ta is not None
    assert ta.get() is not None
