import pytest

from weather_station.codec import PAYLOAD_SIZE, encode
from weather_station.sensors import WeatherSensor


def test_example_from_assignment():
    assert encode({"temperatura": 56.32, "humedad": 51, "direccion_viento": "SO"}) == bytes([0x58, 0x01, 0x9B])


def test_extremes_fit_in_three_bytes():
    assert encode({"temperatura": 0.0, "humedad": 0, "direccion_viento": "N"}) == b"\x00\x00\x00"
    assert encode({"temperatura": 110.0, "humedad": 100, "direccion_viento": "NE"}) == (
        (11000 << 10) | (100 << 3) | 7
    ).to_bytes(3, "big")


def test_every_simulated_reading_is_three_bytes():
    sensor = WeatherSensor(seed=4)
    for _ in range(5000):
        assert len(encode(sensor.read().to_dict())) == PAYLOAD_SIZE


@pytest.mark.parametrize(
    "data",
    [
        {"temperatura": 110.01, "humedad": 50, "direccion_viento": "N"},
        {"temperatura": 50.0, "humedad": 101, "direccion_viento": "N"},
        {"temperatura": 50.0, "humedad": 50, "direccion_viento": "NNE"},
    ],
)
def test_rejects_out_of_range_values(data):
    with pytest.raises(ValueError):
        encode(data)
