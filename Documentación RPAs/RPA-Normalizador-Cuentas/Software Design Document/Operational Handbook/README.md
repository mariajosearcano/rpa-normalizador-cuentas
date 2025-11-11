# 🧩 RPA Normalizador de Cuentas — Operational Handbook

## 🎯 Objetivo  
Bot RPA que **normaliza archivos CSV de cuentas bancarias** recibidos por RabbitMQ. Estandariza y valida campos clave para garantizar calidad de datos contables del holding **DSI Factory**, con trazabilidad completa mediante **logs estructurados y observabilidad con Grafana/Loki**.

---

## 📋 Justificación  
Este RPA automatiza el proceso de limpieza y normalización de datos financieros para:
- Reducir errores humanos en digitación.
- Homogeneizar formatos de fechas, montos y estados.
- Controlar umbrales de error por corrida.
- Centralizar métricas y logs en una capa de observabilidad integrada.
- Facilitar auditorías y depuración mediante reportes estructurados.

---

## ⚙️ Arquitectura

```
n8n → RabbitMQ → Bot Python → CSV Normalizado + Métricas + Logs → Loki → Grafana
```

### Componentes
| Capa | Tecnología | Descripción |
|------|-------------|-------------|
| **Orquestación** | n8n | Expone webhook y publica mensajes JSON a RabbitMQ. |
| **Broker** | RabbitMQ | Cola `rpa.cuentas.normalizar.v1` (exchange directo). |
| **Procesamiento** | Python (Pydantic, Pandas) | Consume, valida y normaliza registros. |
| **Observabilidad** | Loki + Promtail + Grafana | Centraliza logs y métricas del bot. |
| **Infraestructura** | Docker + docker-compose | Contenedores reproducibles localmente. |

---

## 🧠 Flujo de Proceso

1. **n8n** recibe una petición (manual o desde alguna herramienta como Postman) en un webhook.
2. Genera un `run_id` y construye un payload JSON:
   ```json
    return {
      json: {
        run_id: $execution.id,
        archivo: "data/cuentas.csv",
        operacion: "normalizar",
        umbral_error: 0.15,
        meta: {
          solicitante: "qa@dsi.local",
          fuente: "demo"
        }
      }
    };
   ```
3. Publica el mensaje en RabbitMQ (`exchange=rpa.direct`, `queue=rpa.cuentas.normalizar.v1`).
4. El bot Python consume el mensaje, valida el payload y procesa el CSV.
5. Si hay errores:
   - Guarda `out/error_report.json` con detalles.
   - Envía NACK a la cola.
6. Si todo es correcto:
   - Guarda `out/cuentas_normalizadas.csv` y `out/metrics.json`.
   - Envía ACK a RabbitMQ.
7. **Promtail** ingiere logs JSONL y los envía a **Loki**, visibles en **Grafana**.

---

## 🧱 Estructura del Proyecto

```
rpa-normalizador-cuentas/
├── app/
│   ├── main.py              # Entrypoint
│   ├── consumer.py          # Consumidor RabbitMQ
│   ├── processor.py         # Normalización y métricas
│   ├── models.py            # Modelos y validaciones Pydantic
│   ├── infra/
│   │   ├── dsi_logger.py    # Logging estructurado
│   │   └── mq.py            # Utilidades RabbitMQ
│   └── tests/               # Pruebas unitarias
├── tools/publish.py         # Publicador de mensajes de prueba
├── data/cuentas.csv         # Archivo de entrada
├── out/                     # Salidas generadas (gitignored)
├── docker-compose.yml       # Stack completo (n8n, RMQ, Loki, Grafana)
├── Dockerfile               # Imagen del bot
├── promtail-config.yaml     # Config de Promtail
└── Documentación RPAs/
    └── RPA-Normalizador-Cuentas/
        └── Software Design Document/
            └── Operational Handbook/
                └── README.md (este documento)
```

## 🐍 Preparación del Entorno Python (Desarrollo Local)

Esta sección aplica solo si se desea ejecutar el bot o sus herramientas auxiliares (`tools/publish.py`, pruebas unitarias) **directamente en el sistema operativo anfitrión**, sin usar Docker.

### 1. Crear y Activar el Entorno Virtual

Se recomienda usar un entorno virtual para aislar las dependencias del proyecto.

```bash
# Crear el entorno virtual (llamado 'venv' por convención)
python3 -m venv venv

# Activar el entorno virtual
# En macOS/Linux
source venv/bin/activate
# En Windows (Command Prompt)
venv\Scripts\activate.bat
# En Windows (PowerShell)
venv\Scripts\Activate.ps1

# Con el entorno virtual activo, instala todas las dependencias
pip install -r requirements.txt
```

---

## 🚀 Despliegue Local (Docker Compose)

### 1. Clonar y preparar entorno
```bash
git clone https://github.com/mariajosearcano/rpa-normalizador-cuentas
cd rpa-normalizador-cuentas
```

### 2. Crear archivo `.env` en la raiz
```bash
AMQP_URL=amqp://admin:admin123@rabbitmq:5672/
RABBITMQ_QUEUE=rpa.cuentas.normalizar.v1
RABBITMQ_EXCHANGE=rpa.direct
RABBITMQ_ROUTING_KEY=rpa.cuentas.normalizar.v1
LOKI_URL=http://loki:3100
```

### 3. Levantar infraestructura
```bash
docker compose up -d
```
Servicios incluidos:
- `rabbitmq`: cola y panel `http://localhost:15672`
- `n8n`: orquestador `http://localhost:5678`
- `loki`: almacenamiento de logs `http://localhost:3100`
- `promtail`: ingesta de logs
- `grafana`: dashboard `http://localhost:3000`
- `rpa-bot`: consumidor Python

---

## 🧩 Ejecución

### Opción A — Desde n8n
1. Abre `http://localhost:5678`.
2. Importa el flujo `definitions/n8n-workflow.json`.
3. Activa el workflow y lanza el webhook manualmente.
4. Monitorea en tiempo real desde Grafana.

### Opción B — Desde Postman
1. Método: `POST`
2. URL: `http://localhost:5678/webhook/51c2e836-b004-44fc-83c0-06908bc87f88`
3. Body (raw / JSON):
   ```json
   {
     "archivo": "data/cuentas.csv",
     "umbral_error": 0.15
   }
   ```
4. Verifica que el bot consuma el mensaje (logs en consola o Grafana).

### Opción C — Script manual
```bash
python tools/publish.py --file data/cuentas.csv --umbral 0.15
```
*Nota: Para el uso manual sin ayuda del orquestador, hay que descomentar los archivos que estan en app/infra/ y tools/*

---

## 📈 Monitoreo y Observabilidad

| Elemento | Ubicación | Descripción |
|-----------|------------|--------------|
| **Logs en consola** | `docker logs rpa-bot` | Eventos estructurados (INFO/ERROR). |
| **Logs JSONL** | `out/logs.jsonl` | Listo para Promtail/Loki. |
| **Dashboard Grafana** | `http://localhost:3000` | Panel: *RPA Normalizador de Cuentas – Logs*. |
| **Consultas Loki** | `{job="rpa-normalizador-cuentas"}` | Filtrado de eventos por run_id o nivel. |

Ejemplo de log:
```json
{
  "ts": "2025-11-10T22:35:23Z",
  "bot_name": "RPA-Normalizador-Cuentas",
  "run_id": "abc-123",
  "level": "INFO",
  "step": "PROCESS_COMPLETE",
  "message": "Procesamiento completado"
}
```

---

## ⚠️ Manejo de Errores

| Escenario | Resultado | Archivo generado |
|------------|------------|------------------|
| Archivo no encontrado | NACK | `error_report.json` |
| % inválidos > umbral | NACK | `error_report.json` |
| Excepción inesperada | NACK | `error_report.json` |

**Estructura del reporte:**
```json
{
  "run_id": "uuid",
  "timestamp": "2025-11-10T23:00:00Z",
  "mensaje": "Umbral de error excedido",
  "stacktrace_resumido": "...",
  "contexto": {"payload": {...}}
}
```

---

## 🧪 Pruebas Unitarias
```bash
pytest app/tests/ -v
```

**Cobertura mínima esperada:** validaciones de fecha, monto y métricas.  
**Framework:** `pytest` con configuración en `pytest.ini`.

---

## 🧰 Tecnologías Utilizadas

| Categoría | Tecnología |
|------------|-------------|
| Lenguaje | Python slim |
| Orquestación | n8n |
| Mensajería | RabbitMQ |
| Observabilidad | Loki, Promtail, Grafana |
| Infraestructura | Docker, Docker Compose |
| Testing | pytest |
| API Client | Postman |
| Documentación | Markdown + Mermaid |

---

## 🧭 Buenas Prácticas Aplicadas
- Separación clara por capas (`app/`, `infra/`, `tests/`).
- Validaciones declarativas con **Pydantic**.
- Logs estructurados JSONL listos para ingestión.
- Manejo de **ACK/NACK** con control de errores.
- Ejecución idempotente por `run_id`.
- Tipado estático y docstrings PEP8.
- Integración directa con observabilidad (Loki/Grafana).

---

## 🗺️ Diagramas

### Arquitectura
Ubicado en `Documentación RPAs/RPA-Normalizador-Cuentas/Software Design Document/Diagrama de arquitectura/arquitectura.png` o en formato Mermaid en `definitions/arquitectura.mermaid`

### Flujo de Proceso
Ubicado en `Documentación RPAs/RPA-Normalizador-Cuentas/Software Design Document/Diagrama de flujo/flujo.png` o en formato Mermaid en `definitions/flujo.mermaid`

Visualizan el recorrido desde el webhook hasta la salida en `out/`.

---

## 📦 Resultados Esperados
- `out/cuentas_normalizadas.csv` → registros válidos  
- `out/metrics.json` → métricas de ejecución  
- `out/logs.jsonl` → logs estructurados  
- `out/error_report.json` → errores críticos  

---

## 🧭 Guía Rápida

```bash
# 1. Levantar stack
docker compose up -d

# 2. Publicar mensaje (vía script)
## para n8n mediante herramientas como Postman
python tools/publish.py --file data/cuentas.csv --umbral 0.15

# 3. Ver resultados
cat out/metrics.json
```

---

## 📖 Límites y Recomendaciones
- **RabbitMQ local**: persistencia en volumen `rabbitmq_data`.
- **Loki/Grafana**: stack observabilidad solo retiene logs recientes (<24h por defecto).
- **n8n Desktop**: ejecutar como `localhost:5678`.
- **Postman**: alternativa a webhook visual para pruebas rápidas.

---

## 🧾 Créditos
Desarrollado por **María José Arcila Cano**  
Rol: *Computer Engineering (Prueba Técnica DSI Factory)*  
Versión del documento: **v1.0 — Noviembre 2025**
