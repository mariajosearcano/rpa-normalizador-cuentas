# RPA Normalizador de Cuentas - Operational Handbook

## 🎯 Objetivo

Bot RPA que normaliza archivos CSV de cuentas bancarias, validando y estandarizando campos clave (ID, fechas, montos, estados) según reglas de negocio del holding DSI.

## 📋 Justificación

Automatizar el proceso de limpieza y normalización de datos contables para:
- Reducir errores humanos en la captura de datos
- Estandarizar formatos de fechas, montos e identificadores
- Garantizar calidad de datos antes de integración con sistemas core
- Proporcionar trazabilidad completa mediante logs estructurados

## 🏗️ Arquitectura

```
n8n/Power Automate → RabbitMQ → Python Bot → CSV Normalizado + Métricas + Logs
```

**Componentes:**
1. **Orquestador (n8n)**: Expone webhook y publica mensaje a RabbitMQ
2. **RabbitMQ**: Cola de mensajería para desacoplar productor/consumidor
3. **Bot Python**: Consumidor que procesa el CSV
4. **Loki + Grafana**: Stack de observabilidad para logs y métricas

## 🚀 Inicio del Proceso

El bot se activa al recibir un mensaje JSON en la cola `rpa.cuentas.normalizar.v1`:

```json
{
  "run_id": "uuid-generado",
  "archivo": "data/cuentas.csv",
  "operacion": "normalizar",
  "umbral_error": 0.15,
  "meta": {"solicitante": "qa@dsi.local", "fuente": "demo"}
}
```

## 📁 Estructura del Proyecto

```
rpa-normalizador-cuentas/
├── app/
│   ├── main.py              # Entrypoint
│   ├── consumer.py          # Consumidor RabbitMQ
│   ├── processor.py         # Lógica de normalización
│   ├── models.py            # Modelos Pydantic
│   ├── infra/
│   │   ├── dsi_logger.py    # Logger estructurado
│   │   └── mq.py            # Utilidades RabbitMQ
│   └── tests/               # Tests unitarios
├── tools/
│   └── publish.py           # Script para publicar mensajes
├── data/
│   └── cuentas.csv          # Archivo de entrada
├── out/                     # Salidas generadas
├── docker-compose.yml       # Infraestructura
├── requirements.txt         # Dependencias Python
└── Documentación RPAs/      # Documentación técnica
```

## ⚙️ Despliegue

### Opción A: Docker Local (Recomendado)

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd rpa-normalizador-cuentas

# 2. Crear archivo .env
cp .env.example .env

# 3. Levantar infraestructura
docker compose up -d

# 4. Crear entorno virtual e instalar dependencias
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 5. Ejecutar consumidor
python -m app.main
```

### Opción B: Nube Gratuita

**RabbitMQ**: CloudAMQP (plan Little Lemur - gratuito)
**n8n**: n8n Desktop o n8n Cloud (community)

Configurar variables en `.env`:
```bash
AMQP_URL=amqp://usuario:password@host:5672/vhost
```

## 🔧 Configuración de n8n

1. Acceder a n8n: `http://localhost:5678` (usuario: admin, password: admin123)
2. Crear nuevo workflow
3. Agregar nodo **Webhook** (método POST)
4. Agregar nodo **RabbitMQ** configurando:
   - Exchange: `rpa.direct`
   - Routing Key: `rpa.cuentas.normalizar.v1`
   - Message: JSON del payload
5. Activar workflow

## 📊 Configuración de Grafana + Loki

1. Acceder a Grafana: `http://localhost:3000` (admin/admin123)
2. Agregar Loki como data source: `http://loki:3100`
3. Importar dashboard para visualizar logs del RPA
4. Query ejemplo: `{bot_name="RPA-Normalizador-Cuentas"}`

## ▶️ Ejecución

### Método 1: Via n8n
1. Ejecutar webhook desde n8n UI
2. Monitorear logs del consumidor en consola

### Método 2: Via script
```bash
# Terminal 1: Consumidor
python -m app.main

# Terminal 2: Publicador
python tools/publish.py --file data/cuentas.csv --umbral 0.15
```

## 📈 Monitoreo

### Logs en Consola
```
[INFO] [START_PROCESSING] Iniciando procesamiento de data/cuentas.csv
[INFO] [READ_CSV] Leyendo archivo: data/cuentas.csv
[INFO] [PROCESS_COMPLETE] Procesamiento completado: 7 válidos, 3 inválidos
```

### Logs Estructurados (out/logs.jsonl)
```json
{"ts": "2024-11-07T10:30:00Z", "bot_name": "RPA-Normalizador-Cuentas", "run_id": "abc-123", "level": "INFO", "step": "PROCESS_COMPLETE", "message": "Procesamiento completado"}
```

### Métricas (out/metrics.json)
```json
{
  "run_id": "abc-123",
  "totales": 10,
  "validos": 7,
  "invalidos": 3,
  "porcentaje_invalidos": 30.0,
  "duracion_ms": 1234.56
}
```

### Archivos de Salida
- `out/cuentas_normalizadas.csv`: Registros válidos
- `out/metrics.json`: Métricas del procesamiento
- `out/logs.jsonl`: Logs estructurados
- `out/error_report.json`: Reporte de errores (solo si falla)

## 🚨 Manejo de Fallas

### Error: Umbral de errores excedido
**Síntoma**: `error_report.json` generado, mensaje rechazado

**Solución**:
1. Revisar `error_report.json` para identificar causa
2. Corregir datos en CSV fuente
3. Ajustar `umbral_error` si es necesario (max 1.0)
4. Re-publicar mensaje

### Error: Archivo no encontrado
**Solución**: Verificar que la ruta en el payload sea correcta

### Error: Conexión a RabbitMQ fallida
**Solución**:
1. Verificar que RabbitMQ esté corriendo: `docker ps`
2. Verificar variables en `.env`
3. Reiniciar: `docker compose restart rabbitmq`

### Error: Formato de fecha inválido
**Logs**: `[ERROR] [NORMALIZE_FECHA] Error parseando fecha`

**Solución**: El bot rechaza automáticamente registros con fechas inválidas

## 🧪 Pruebas

```bash
# Ejecutar tests
pytest app/tests/ -v

# Con cobertura
pytest app/tests/ --cov=app --cov-report=html
```

## 🔐 Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| AMQP_URL | URL de RabbitMQ | `amqp://admin:admin123@localhost:5672/` |
| RABBITMQ_QUEUE | Nombre de la cola | `rpa.cuentas.normalizar.v1` |
| RABBITMQ_EXCHANGE | Exchange directo | `rpa.direct` |
| RABBITMQ_ROUTING_KEY | Routing key | `rpa.cuentas.normalizar.v1` |
| LOKI_URL | URL de Loki | `http://localhost:3100` |

## 📝 Reglas de Normalización

1. **id_cuenta**: Strip, mayúsculas, alfanumérico (permite guiones)
2. **fecha_emision**: Parse a ISO YYYY-MM-DD, validar fechas reales
3. **monto**: Float positivo, reemplazar comas por puntos
4. **estado**: Uno de {PENDIENTE, ENVIADA, APROBADA, RECHAZADA}

## 🎬 Demo

Ver video demostrativo en: `Documentación RPAs/RPA-Normalizador-Cuentas/Product Design Document/Video/demo.mp4`

## 📞 Soporte

En caso de problemas:
1. Revisar logs en `out/logs.jsonl`
2. Consultar `error_report.json` si existe
3. Verificar conectividad a RabbitMQ
4. Contactar al equipo DSI Factory

---

**"DSI no opera. DSI orquesta."**