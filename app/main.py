"""
Punto de entrada del RPA Normalizador de Cuentas
"""
import os
from pathlib import Path
from dotenv import load_dotenv

from app.consumer import RabbitMQConsumer


def main():
    """Función principal"""
    # Cargar variables de entorno
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv(env_file)
    
    # Crear directorio de salida
    Path("out").mkdir(exist_ok=True)
    
    # Iniciar consumidor
    consumer = RabbitMQConsumer()
    consumer.start_consuming()


if __name__ == "__main__":
    main()
