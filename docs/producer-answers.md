# Respuestas de la parte del productor (Esteban)

Borrador para las láminas de la presentación (entrega del 12 de noviembre).

## 3.1 Simulación del sensor

**Qué se hizo.** `weather_station/sensors.py` simula los tres sensores:

- Temperatura: normal con media 55 y desviación estándar 15 (varianza 225), recortada a [0, 110] y redondeada a 2 decimales.
- Humedad: normal con media 55 y desviación estándar 15, recortada a [0, 100] y redondeada a entero.
- Dirección del viento: uniforme entre {N, NO, O, SO, S, SE, E, NE}.

Con σ = 15, cerca del 99.7 % de las muestras cae en 55 ± 45 = [10, 100], así que casi nunca se recorta y la gráfica muestra variación visible.

Cada lectura se serializa a JSON: `{"temperatura": 56.32, "humedad": 51, "direccion_viento": "SO"}`.

### ¿A qué capa pertenece JSON/SOAP según el modelo OSI y por qué?

A la **capa 6, Presentación**. JSON (y el XML que usa SOAP) define **cómo se representan y serializan los datos**: su sintaxis, sus tipos y su codificación en texto UTF-8. No define cómo se transportan ni qué significan para la aplicación. Es justo lo que hace la capa de presentación: traducir entre la representación interna de cada sistema (un objeto de Python, un `struct` en C) y un formato común que ambos extremos entienden.

Matiz: SOAP, como protocolo de mensajería (sobre HTTP, con sobre, headers y body), también suele ubicarse en la **capa 7, Aplicación**. Su parte de codificación XML sigue siendo función de presentación. En el modelo TCP/IP, ambos quedan dentro de la capa de aplicación.

### ¿Qué beneficios tiene utilizar un formato como JSON/SOAP?

- **Interoperabilidad:** es independiente del lenguaje y de la plataforma. El productor en Python y un consumidor en Java o JS leen lo mismo.
- **Autodescriptivo y legible:** cada valor viaja con su nombre, así que se puede depurar leyendo el mensaje.
- **Extensible:** se pueden agregar campos (timestamp, id del sensor) sin romper a los consumidores que los ignoran.
- **Desacoplamiento y modularidad:** productor y consumidor solo comparten el contrato del mensaje, no el código.
- **Herramientas estándar:** hay parsers en todos los lenguajes, y validación con JSON Schema o XSD (SOAP/WSDL).

Costo: es verboso. Nuestra lectura en JSON pesa **63 bytes**, contra **3 bytes** en el formato compacto de la sección 3.4.

## 3.2 Envío de datos al servidor Edge

**Qué se hizo.** `producer.py` crea un `KafkaProducer` hacia `161.35.11.141:9092` con `SASL_PLAINTEXT` y `PLAIN` (credenciales en `.env`). Publica en el topic **23016** con key `sensor1`, espera un tiempo aleatorio de 15 a 30 s entre envíos y corre hasta Ctrl+C.

- `acks="all"`: el broker confirma cada mensaje. El productor imprime la partición y el offset de cada uno, que sirve como evidencia para las capturas.
- Con la misma key, todos los mensajes caen en la misma partición y se conserva el orden.

Comandos:

```bash
python producer.py
python producer.py --compact
python producer.py --count 5 --min-interval 1 --max-interval 2
```

## 3.4 IoT en entornos con restricciones

**Qué se hizo.** `weather_station/codec.py` implementa `encode` (de JSON a 3 bytes) y `producer.py --compact` envía las lecturas codificadas.

Distribución de los 24 bits (big-endian):

```
 bit 23 ............ 10 | 9 ....... 3 | 2 .. 0
   temperatura × 100    |   humedad   | viento
        14 bits         |   7 bits    | 3 bits
```

- Viento: índice en `(N, NO, O, SO, S, SE, E, NE)`, de 0 a 7.
- Ejemplo: `{"temperatura": 56.32, "humedad": 51, "direccion_viento": "SO"}` → 5632 << 10 | 51 << 3 | 3 = `0x58019B` → bytes `58 01 9B`.

### ¿Qué complejidades introduce el tener un payload restringido (pequeño)?

- **El mensaje deja de ser autodescriptivo.** Productor y consumidor tienen que compartir exactamente el mismo esquema de bits. Si uno cambia el orden o el tamaño de un campo y el otro no, el consumidor decodifica basura sin darse cuenta.
- **Versionado difícil:** no sobra ni un bit para indicar versión, así que agregar un campo obliga a rediseñar el formato y actualizar todos los nodos a la vez.
- **Pérdida de precisión o de rango:** hay que cuantizar (punto fijo) y recortar valores, y decidir qué precisión se sacrifica.
- **No hay espacio para metadatos:** ni timestamp, ni id del sensor, ni checksum o CRC. Un bit corrupto cambia el valor y no hay forma de detectarlo en el payload.
- **Más lógica y más fuentes de error:** máscaras, corrimientos, orden de bytes (endianness) y validación de rangos antes de codificar.
- **Depuración más difícil:** `65 75 4c` no se entiende a simple vista, a diferencia de un JSON.

### ¿Cómo podemos hacer que el valor de temperatura quepa en 14 bits?

Con **punto fijo**: como la temperatura tiene 2 decimales y su máximo es 110.00, se multiplica por 100 y se guarda como entero (56.32 → 5632). El máximo es 11000, menor que 2^14 − 1 = 16383, así que cabe en 14 bits sin perder precisión. Al decodificar se divide entre 100. Un `float` de 4 bytes (32 bits) no es necesario porque el rango y la resolución son conocidos y pequeños.

### ¿Qué sucedería si ahora la humedad también es tipo float con un decimal? ¿Qué decisiones tendríamos que tomar?

La humedad pasaría a tener 1001 valores posibles (0.0 a 100.0, es decir 0 a 1000 en punto fijo), que necesitan **10 bits** (2^10 = 1024). El total sería 14 + 10 + 3 = **27 bits**, que no caben en 24. Habría que decidir entre:

1. **Bajar la resolución de la temperatura a 1 decimal:** 0 a 1100 cabe en **11 bits**, y 11 + 10 + 3 = **24 bits exactos**. Es la opción más limpia si 0.1 °C de precisión es aceptable.
2. **Mantener la humedad entera** y sacrificar su decimal.
3. **Reducir el rango útil** con un offset (por ejemplo, si la estación nunca baja de 0 °C ni sube de 60 °C, el rango real es menor y necesita menos bits).
4. **Mandar los campos en mensajes alternados** (uno con temperatura, otro con humedad), a costa de más mensajes y de usar algunos bits para indicar el tipo.
5. **Pedir más payload** (4 bytes) si la red lo permite.

La decisión depende de qué precisión necesita realmente el consumidor de los datos.
