# Evidencia de la gráfica

`local-mixed.png` es una prueba local, no una captura de datos recibidos por Kafka.
Se usaron 24 lecturas de `WeatherSensor(seed=23016)`, alternando JSON y compacto
con `encode_reading`, `parse_message` y `WeatherPlot`. Las horas son de prueba:
11 de noviembre de 2026 a las 12:00, con pasos de 20 segundos, sin espera real.
La imagen tiene 2400 × 1800 píxeles. Se comprobó que las dos líneas tienen 24
puntos y que las barras suman 24 lecturas.

Falta la evidencia real de F4: en este equipo no está configurada la contraseña
del broker. Para obtenerla, completar `.env` sin subirlo al repositorio, ejecutar
el productor con los intervalos predeterminados de 15–30 s y abrir:

```bash
python consumer.py --replay --save docs/screenshots/kafka-json.png
```

Después de varios mensajes, cerrar la ventana para guardar. Repetir con el
productor en modo `--compact` y guardar como `kafka-compact.png`. Conservar también
los offsets de consola para distinguir los mensajes nuevos del historial.
Reemplazar la evidencia local en la presentación por estas capturas antes de
entregar. El código no se ha subido a Canvas desde este equipo.
