from pandas._testing import assert_series_equal

from wavematic import Noise, TimeAxis

from ..data import data


def test_noise():
    ta = TimeAxis(duration=1.0, rate=100.0, start=0.0)
    noise = Noise(ta=ta, amp=1.0, seed=0, name="Foo")
    noise_ser = noise.get()
    ta_ser = ta.get()
    assert len(noise_ser) == 100
    assert noise_ser.name == "Foo"
    assert_series_equal(ta_ser, noise_ser.index.to_series().reset_index(drop=True))
    assert_series_equal(noise_ser, data["noise1"])
