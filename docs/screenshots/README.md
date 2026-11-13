# Evidencia de la gráfica

Capturas reales contra el broker `161.35.11.141:9092`, topic `23016`, tomadas el 10 de noviembre de 2026.

| Archivo | Qué muestra |
|---|---|
| `sensors-and-tests.png` | Lecturas simuladas en JSON con su codificación de 3 bytes, y las 20 pruebas aprobadas |
| `live-desktop.png` | Escritorio con la terminal del productor, la del consumidor y la gráfica en vivo, todo corriendo a la vez |
| `live-producer-terminal.png` | Terminal del productor: 5 envíos JSON y 5 de 3 bytes, cada uno con partición y offset |
| `live-consumer-terminal.png` | Terminal del consumidor: cada mensaje recibido y decodificado con su offset |
| `live-consumer-offsets-20-29.png` | Recorte del consumidor con los offsets 20–29, los mismos que envió el productor |
| `live-plot-window.png` | Ventana de la gráfica en vivo |
| `kafka-json.png` | Figura de 20:36–20:39: 8 lecturas JSON (offsets 4–11) más el historial anterior |
| `kafka-compact.png` | Figura de 20:39–20:42: 8 lecturas de 3 bytes (offsets 12–19) más el historial anterior |
| `local-mixed.png` | Prueba local sin broker (24 lecturas simuladas con horas artificiales); no es evidencia de Kafka |

Para repetirlas, con la contraseña en `.env`:

```bash
python producer.py
python consumer.py
```
