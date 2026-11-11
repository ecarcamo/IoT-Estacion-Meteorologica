import json
import random
from dataclasses import dataclass

WIND_DIRECTIONS = ("N", "NO", "O", "SO", "S", "SE", "E", "NE")

TEMPERATURE_RANGE = (0.0, 110.0)
HUMIDITY_RANGE = (0, 100)
MEAN = 55.0
STANDARD_DEVIATION = 15.0


@dataclass(frozen=True)
class Reading:
    temperature: float
    humidity: int
    wind_direction: str

    def to_dict(self) -> dict:
        return {
            "temperatura": self.temperature,
            "humedad": self.humidity,
            "direccion_viento": self.wind_direction,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


class WeatherSensor:
    def __init__(self, seed: int | None = None):
        self._random = random.Random(seed)

    def read_temperature(self) -> float:
        value = self._random.gauss(MEAN, STANDARD_DEVIATION)
        return round(clamp(value, *TEMPERATURE_RANGE), 2)

    def read_humidity(self) -> int:
        value = self._random.gauss(MEAN, STANDARD_DEVIATION)
        return int(round(clamp(value, *HUMIDITY_RANGE)))

    def read_wind_direction(self) -> str:
        return self._random.choice(WIND_DIRECTIONS)

    def read(self) -> Reading:
        return Reading(
            temperature=self.read_temperature(),
            humidity=self.read_humidity(),
            wind_direction=self.read_wind_direction(),
        )
