# 📝 Resumen de Batallas Ganadas, Aprendizajes y Decisiones Clave

## RPA: Normalizador de Cuentas (Mi Prueba Técnica para DSI Factory)

### 🚀 1. El Momento "¡Socorro!" y el Gran Logro Personal

Para ser totalmente honesta, cuando leí la prueba, sentí que me enfrentaba a un monstruo tecnológico. Nunca había montado una automatización con tanto cacharro a la vez: n8n, RabbitMQ, Python, Docker... ¡y yo terminé sumando la triada Grafana, Loki y Promtail! Al principio, mi cabeza estaba en blanco, no sabía ni por dónde jalar la cuerda, pero sabía que lo iba a sacar, sí o sí.

Mi gran satisfacción fue ver cómo, a punta de prueba y error y muchísima documentación, fui entendiendo cada pieza. Pasé de la confusión total a sentirme cómoda en el entorno. Lograr que no solo el workflow funcionara, sino también montar las visualizaciones, fue mi gran win personal. Y sí, ya puedo decir que esto de automatizar me ha encantado.

### 🛠️ 2. Las Piedras en el Camino y Cómo las Salté

Las mayores batallas no fueron el código, sino la puesta en marcha de la infraestructura.

1. La Parálisis del Inicio (Conceptual)

Problema Real: ¿Por dónde demonios se arranca esto? No sabía cómo conectar el mundo del messaging con el mundo Python.

Solución: Decidí simplificar y atacar por etapas: primero el corazón (el código Python de procesamiento y el logging estructurado), y luego le fui pegando el resto (RabbitMQ y el consumer).

1. El Enredo de Docker y Grafana

Problema Real: La configuración del docker-compose.yml para enlazar n8n, RabbitMQ y que todo hablara bien fue una pesadilla inicial. Peor aún fue montar el stack de Grafana/Loki/Promtail. Por inexperiencia, pensé que la visualización era obligatoria desde el inicio.

Solución: Tras dedicar tiempo a entender bien qué hacía Promtail y cómo etiquetaba los logs hacia Loki, todo hizo click. Aunque no era un requisito estricto, esa dificultad me sirvió para asegurar que los logs ya están perfectos y listos para la ingesta de Grafana. ¡Quedó con un nivel de observabilidad premium! 😉

### 💡 3. Las Decisiones que Hicieron que Esto Funcione

Hubo dos grandes cambios de rumbo que definieron la arquitectura final:

"¡Todo a Docker!": Empecé con Python local, pero rápidamente me di cuenta de que la única forma de garantizar que el bot, RabbitMQ y n8n coexistieran sin problemas era usar Docker Compose. La solución es ahora totalmente portátil.

Obsesión por la Observabilidad: Decidí mantener la implementación completa de Loki/Grafana. Esto demuestra que entendí que un RPA en DSI no solo debe procesar, sino ser totalmente transparente. Gracias a esto, la trazabilidad por run\_id en el dashboard es impecable.
