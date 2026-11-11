import json
import statistics

from weather_station.sensors import WIND_DIRECTIONS, WeatherSensor


def test_readings_stay_in_range():
    sensor = WeatherSensor(seed=1)
    for _ in range(5000):
        reading = sensor.read()
        assert 0 <= reading.temperature <= 110
        assert round(reading.temperature, 2) == reading.temperature
        assert isinstance(reading.humidity, int)
        assert 0 <= reading.humidity <= 100
        assert reading.wind_direction in WIND_DIRECTIONS


def test_readings_are_centered_on_55():
    sensor = WeatherSensor(seed=2)
    readings = [sensor.read() for _ in range(5000)]
    assert abs(statistics.mean(r.temperature for r in readings) - 55) < 1
    assert abs(statistics.mean(r.humidity for r in readings) - 55) < 1


def test_json_uses_agreed_keys():
    payload = json.loads(WeatherSensor(seed=3).read().to_json())
    assert set(payload) == {"temperatura", "humedad", "direccion_viento"}
