from weather_station.sensors import WIND_DIRECTIONS

PAYLOAD_SIZE = 3
TEMPERATURE_BITS = 14
HUMIDITY_BITS = 7
WIND_BITS = 3
TEMPERATURE_SCALE = 100

HUMIDITY_SHIFT = WIND_BITS
TEMPERATURE_SHIFT = HUMIDITY_BITS + WIND_BITS

TEMPERATURE_MASK = (1 << TEMPERATURE_BITS) - 1
HUMIDITY_MASK = (1 << HUMIDITY_BITS) - 1
WIND_MASK = (1 << WIND_BITS) - 1


def encode(data: dict) -> bytes:
    temperature = round(data["temperatura"] * TEMPERATURE_SCALE)
    humidity = data["humedad"]
    wind = WIND_DIRECTIONS.index(data["direccion_viento"])
    if not 0 <= temperature <= 110 * TEMPERATURE_SCALE:
        raise ValueError(f"Temperatura fuera de rango: {data['temperatura']}")
    if not 0 <= humidity <= 100:
        raise ValueError(f"Humedad fuera de rango: {humidity}")
    packed = (temperature << TEMPERATURE_SHIFT) | (humidity << HUMIDITY_SHIFT) | wind
    return packed.to_bytes(PAYLOAD_SIZE, "big")
