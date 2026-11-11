# Respuestas de la parte del consumidor (Felipe)

## 3.3 Consumo y gráfica de la telemetría

**Qué se hizo.** El consumidor lee el topic configurado, distingue los dos
formatos y muestra temperatura, humedad y frecuencia de cada dirección del
viento. Usamos `poll` con una espera corta y `plt.pause` para que la ventana siga
respondiendo aunque no lleguen mensajes. La hora viene del registro de Kafka;
el formato de tres bytes no incluye un timestamp propio.

El grupo guarda offsets para continuar después. Con `--replay` podemos volver
a leer el historial retenido sin modificar esos offsets. `earliest` por sí solo
no reinicia un grupo que ya tiene progreso guardado. Los mensajes inválidos se
reportan en consola y no se agregan a la gráfica.

### ¿Qué ventajas y desventajas tiene Pub/Sub con Kafka?

Nos permite separar el sensor de quienes usan sus datos: el productor publica
una vez y puede haber una gráfica, un sistema de alertas y otro de análisis,
cada uno con su propio grupo. Kafka conserva los mensajes según la retención
configurada, así que un consumidor puede ponerse al día o repetir un análisis.
Las particiones permiten repartir trabajo entre consumidores de un mismo grupo.

La desventaja es que necesitamos mantener el broker, configurar credenciales y
entender los offsets. Para una estación pequeña usa más recursos que una conexión
directa y añade un salto de red. El orden está garantizado dentro de una partición,
no en todo el topic. Tampoco tenemos entrega exactamente una vez en esta gráfica:
los commits automáticos y los reinicios pueden producir relecturas o dejar datos
fuera de la sesión visible. La gráfica mantiene sus datos solo en memoria.

### ¿Para qué aplicaciones tiene sentido Kafka y para cuáles no?

Lo usaríamos para muchas estaciones IoT, logs, análisis continuo, integración de
microservicios o eventos que varios sistemas necesitan procesar. La persistencia
y la capacidad de releer son útiles cuando un consumidor se desconecta.

No sería nuestra primera opción para una aplicación pequeña con pocos mensajes,
una cola sencilla o una consulta que necesita respuesta inmediata. Para sensores
con poca memoria o enlaces limitados, MQTT o CoAP suelen ajustarse mejor; un gateway
puede recibir esos mensajes y publicarlos en Kafka. Kafka puede conservar eventos,
pero usarlo para event sourcing requiere diseñar retención y reconstrucción del estado.

## 3.4 Mensajes de tres bytes

**Qué se hizo.** `decode` recupera la temperatura con un corrimiento de 10 bits,
una máscara de 14 bits y una división entre 100. La humedad usa los siguientes
7 bits y el viento los últimos 3. El ejemplo `58 01 9B` vuelve a 56.32 °C,
51 % y SO. Probamos ida y vuelta con 5000 lecturas sin cambiar sus valores.

### ¿Qué herramientas o parámetros ayudarían con restricciones mayores?

- `compression_type` en kafka-python (`compression.type` en Java) comprime lotes.
  gzip, snappy, lz4 o zstd pueden ayudar con muchos mensajes, pero comprimir solo
  tres bytes no garantiza ahorro y puede agregar sobrecarga.
- `batch_size` y `linger_ms` agrupan mensajes para aprovechar mejor cada solicitud.
  Ahorran tráfico a cambio de esperar más. Nuestro productor espera confirmación
  después de cada envío, así que habría que cambiar ese flujo para formar lotes.
- `max_request_size` limita la solicitud del productor, no solamente el valor de
  tres bytes. También hay cabeceras, key y sobrecarga de Kafka y de la red.
- Bajar `acks` reduce garantías de confirmación; no lo cambiaríamos sin aceptar
  antes el riesgo de perder datos. `acks="all"` espera las réplicas sincronizadas
  según la configuración del broker, no garantiza por sí solo ausencia de pérdidas.
- Acortar la key puede ahorrar bytes. Quitarla cambia cómo se reparten los mensajes
  y puede perderse el orden por sensor que buscamos con `sensor1`.
- Avro o Protobuf con Schema Registry ayudan a compartir y evolucionar contratos,
  pero su envoltura puede superar el límite estricto de tres bytes.
- Un gateway MQTT puede filtrar o agregar lecturas antes de enviarlas. Kafka Connect
  ayuda con integraciones; Kafka Streams procesa eventos en una aplicación conectada
  al cluster. Para ahorrar el enlace sensor–broker hay que reducir datos antes de
  ese enlace, no solo procesarlos después de que llegan a Kafka.

## Estado de las pruebas

La prueba local alternó 24 mensajes JSON y compactos y verificó las líneas y los
conteos. No demuestra autenticación ni entrega desde el broker. La captura real
y la prueba de cierre con la ventana conectada quedan pendientes de configurar
la contraseña en `.env`. No incluimos credenciales en las respuestas ni en Git.
