import argparse
import random
import time
from datetime import datetime

from kafka import KafkaProducer

from weather_station import codec
from weather_station.config import load_settings
from weather_station.sensors import Reading, WeatherSensor


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Nodo IoT de la estación meteorológica (Kafka Producer)")
    parser.add_argument("--min-interval", type=float, default=15.0, help="segundos mínimos entre envíos")
    parser.add_argument("--max-interval", type=float, default=30.0, help="segundos máximos entre envíos")
    parser.add_argument("--count", type=int, default=0, help="cantidad de envíos; 0 envía hasta Ctrl+C")
    parser.add_argument("--key", default="sensor1", help="key de los mensajes")
    parser.add_argument("--compact", action="store_true", help="envía cada lectura codificada en 3 bytes")
    return parser.parse_args()


def encode_reading(reading: Reading, compact: bool) -> bytes:
    if compact:
        return codec.encode(reading.to_dict())
    return reading.to_json().encode("utf-8")


def main() -> None:
    args = parse_args()
    settings = load_settings()
    producer = KafkaProducer(**settings.client_options(), acks="all")
    sensor = WeatherSensor()
    mode = "compacto (3 bytes)" if args.compact else "JSON"
    print(f"Enviando al topic {settings.topic} en {settings.bootstrap_servers}, modo {mode}. Ctrl+C para detener.")
    sent = 0
    try:
        while args.count == 0 or sent < args.count:
            reading = sensor.read()
            payload = encode_reading(reading, args.compact)
            metadata = producer.send(settings.topic, key=args.key.encode("utf-8"), value=payload).get(timeout=30)
            sent += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(
                f"[{timestamp}] #{sent} {reading.to_json()} -> {payload.hex(' ') if args.compact else 'JSON'} "
                f"({len(payload)} bytes, partición {metadata.partition}, offset {metadata.offset})"
            )
            if args.count == 0 or sent < args.count:
                time.sleep(random.uniform(args.min_interval, args.max_interval))
    except KeyboardInterrupt:
        print("\nDetenido por el usuario.")
    finally:
        producer.flush()
        producer.close()


if __name__ == "__main__":
    main()
