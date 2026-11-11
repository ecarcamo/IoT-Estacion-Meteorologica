# IoT-Estacion-Meteorologica

Estación meteorológica IoT simulada que publica su telemetría en Apache Kafka (CC3067 Redes, UVG).

## Uso

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
python producer.py
python producer.py --compact
pytest -q
```

En `.env` hay que poner la contraseña del broker que viene en el enunciado.
