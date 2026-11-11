import argparse
import json
from datetime import datetime

import matplotlib.pyplot as plt
from kafka import KafkaConsumer

from weather_station import codec
from weather_station.config import load_settings
from weather_station.plot import WeatherPlot
from weather_station.sensors import WIND_DIRECTIONS


def parse_message(value: bytes) -> dict:
    if not isinstance(value, bytes):
        raise ValueError("El mensaje no contiene bytes")
    data = codec.decode(value) if len(value) == codec.PAYLOAD_SIZE else json.loads(value)
    if not isinstance(data, dict):
        raise ValueError("La lectura debe ser un objeto")
    temperature = data.get("temperatura")
    humidity = data.get("humedad")
    if type(temperature) not in (int, float) or not 0 <= temperature <= 110:
        raise ValueError("Temperatura inválida")
    if type(humidity) is not int or not 0 <= humidity <= 100:
        raise ValueError("Humedad inválida")
    if data.get("direccion_viento") not in WIND_DIRECTIONS:
        raise ValueError("Dirección del viento inválida")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Consumidor de la estación meteorológica")
    parser.add_argument("--replay", action="store_true", help="relee el historial sin guardar offsets del grupo")
    parser.add_argument("--save", help="guarda la gráfica en PNG al cerrar")
    args = parser.parse_args()
    settings = load_settings()
    consumer = KafkaConsumer(
        settings.topic,
        **settings.client_options(),
        group_id=None if args.replay else f"{settings.topic}-grafica",
        auto_offset_reset="earliest",
        enable_auto_commit=not args.replay,
    )
    print(f"Leyendo el topic {settings.topic}. Ctrl+C para detener.")
    try:
        chart = WeatherPlot(settings.topic)
        plt.show(block=False)
        while plt.fignum_exists(chart.figure.number):
            changed = False
            for records in consumer.poll(timeout_ms=100, max_records=500).values():
                for record in records:
                    try:
                        data = parse_message(record.value)
                    except (ValueError, UnicodeError) as error:
                        print(f"Mensaje omitido: partición {record.partition}, offset {record.offset}: {error}")
                        continue
                    print(f"Partición {record.partition}, offset {record.offset}: {data}", flush=True)
                    timestamp = datetime.fromtimestamp(record.timestamp / 1000) if record.timestamp >= 0 else datetime.now()
                    chart.add(data, timestamp)
                    changed = True
            if changed:
                chart.refresh()
            plt.pause(0.1)
    except KeyboardInterrupt:
        print("\nDetenido por el usuario.")
    finally:
        consumer.close()
    if args.save:
        chart.figure.savefig(args.save, dpi=200)
    plt.close(chart.figure)


if __name__ == "__main__":
    main()
