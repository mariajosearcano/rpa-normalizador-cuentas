"""
Script para publicar mensajes de prueba a RabbitMQ
"""
import json
import uuid
import argparse
from pathlib import Path
from dotenv import load_dotenv

from app.infra.mq import RabbitMQConnection


def main():
    """Publica un mensaje de prueba"""
    parser = argparse.ArgumentParser(description="Publica mensaje a RabbitMQ")
    parser.add_argument("--file", default="data/cuentas.csv", help="Ruta del archivo CSV")
    parser.add_argument("--run-id", default=None, help="Run ID (se genera si no se provee)")
    parser.add_argument("--umbral", type=float, default=0.15, help="Umbral de error (0-1)")
    
    args = parser.parse_args()
    
    # Cargar variables de entorno
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv(env_file)
    
    # Generar run_id si no se provee
    run_id = args.run_id or str(uuid.uuid4())
    
    # Crear payload
    payload = {
        "run_id": run_id,
        "archivo": args.file,
        "operacion": "normalizar",
        "umbral_error": args.umbral,
        "meta": {
            "solicitante": "qa@dsi.local",
            "fuente": "demo"
        }
    }
    
    print(f"\n=== Publicando Mensaje ===")
    print(f"Run ID: {run_id}")
    print(f"Archivo: {args.file}")
    print(f"Umbral: {args.umbral}")
    print(f"\nPayload:")
    print(json.dumps(payload, indent=2))
    
    # Conectar y publicar
    mq = RabbitMQConnection()
    channel = mq.connect()
    mq.publish_message(json.dumps(payload))
    
    print(f"\n✓ Mensaje publicado exitosamente en {mq.queue_name}")
    print(f"✓ Ahora ejecuta el consumidor con: python -m app.main\n")
    
    mq.close()


if __name__ == "__main__":
    main()