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

## Consumidor y gráfica

En otra terminal, con el mismo entorno virtual activo:

```bash
python consumer.py
python consumer.py --replay --save docs/screenshots/kafka.png
```

Se muestran temperatura, humedad y conteos de viento. El consumidor acepta JSON
y mensajes compactos mezclados, imprime partición y offset y omite mensajes
inválidos sin cerrar la gráfica. Para salir, cierra la ventana o presiona Ctrl+C.
`--save` exporta la figura a 200 dpi al salir; la carpeta de destino debe existir.

El grupo normal es `<topic>-grafica`: continúa desde sus offsets guardados.
`earliest` solo aplica si no hay un offset válido guardado. `--replay` usa un
consumidor sin grupo ni commits para releer desde el principio del historial
retenido. No se garantiza orden global entre particiones; el eje usa la hora
del mensaje y la key `sensor1` mantiene los datos del productor en una partición.

Para la evidencia final, deja el productor con sus intervalos normales de 15–30 s.
Primero ejecuta `python producer.py` y luego prueba `python producer.py --compact`.
No publiques `.env`: SASL_PLAINTEXT autentica, pero no cifra la conexión.

## Presentación y evidencia

Las respuestas están en `docs/producer-answers.md` y `docs/consumer-answers.md`.
Las láminas están en `docs/presentation.html` y `docs/presentation.pdf` es lo que
se entrega. Para regenerar el PDF después de editar el HTML:

```bash
chromium --headless --no-pdf-header-footer --print-to-pdf=docs/presentation.pdf docs/presentation.html
```

Las capturas reales contra el broker están en `docs/screenshots/`; su README
explica qué muestra cada una.
