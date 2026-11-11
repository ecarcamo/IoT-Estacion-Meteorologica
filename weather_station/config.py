import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class KafkaSettings:
    bootstrap_servers: str
    topic: str
    security_protocol: str
    sasl_mechanism: str
    username: str
    password: str

    def client_options(self) -> dict:
        return {
            "bootstrap_servers": self.bootstrap_servers,
            "security_protocol": self.security_protocol,
            "sasl_mechanism": self.sasl_mechanism,
            "sasl_plain_username": self.username,
            "sasl_plain_password": self.password,
        }


def load_settings() -> KafkaSettings:
    load_dotenv()
    missing = [name for name in ("KAFKA_USERNAME", "KAFKA_PASSWORD") if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Faltan variables en .env: {', '.join(missing)}")
    return KafkaSettings(
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "161.35.11.141:9092"),
        topic=os.getenv("KAFKA_TOPIC", "23016"),
        security_protocol=os.getenv("KAFKA_SECURITY_PROTOCOL", "SASL_PLAINTEXT"),
        sasl_mechanism=os.getenv("KAFKA_SASL_MECHANISM", "PLAIN"),
        username=os.environ["KAFKA_USERNAME"],
        password=os.environ["KAFKA_PASSWORD"],
    )
