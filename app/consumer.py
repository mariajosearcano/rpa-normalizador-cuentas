"""
Consumidor de mensajes RabbitMQ
"""
import json
import traceback
from pathlib import Path
from datetime import datetime

from app.infra.mq import RabbitMQConnection
from app.infra.dsi_logger import logger
from app.models import MessagePayload, ErrorReport
from app.processor import CuentasProcessor


class RabbitMQConsumer:
    """Consumidor que procesa mensajes de normalización"""
    
    def __init__(self):
        self.mq = RabbitMQConnection()
    
    def callback(self, ch, method, properties, body):
        """Callback ejecutado al recibir un mensaje"""
        run_id = None
        payload_dict = None
        
        try:
            # Parsear mensaje
            payload_dict = json.loads(body)
            logger.info("MESSAGE_RECEIVED", "Mensaje recibido", payload=payload_dict)
            
            # Validar payload
            payload = MessagePayload(**payload_dict)
            run_id = payload.run_id
            
            # Inicializar logger con run_id
            logger.init("RPA-Normalizador-Cuentas", run_id)
            
            logger.info("START_PROCESSING", 
                       f"Iniciando procesamiento de {payload.archivo}",
                       operacion=payload.operacion,
                       umbral_error=payload.umbral_error)
            
            # Verificar que el archivo existe
            filepath = Path(payload.archivo)
            if not filepath.exists():
                raise FileNotFoundError(f"Archivo no encontrado: {payload.archivo}")
            
            # Procesar archivo
            processor = CuentasProcessor(run_id)
            metrics = processor.process_file(str(filepath), payload.umbral_error)
            
            # Guardar métricas
            self.save_metrics(metrics)
            
            logger.info("END_PROCESSING", 
                       "Procesamiento completado exitosamente",
                       metricas=metrics.model_dump())
            
            # ACK del mensaje
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info("MESSAGE_ACK", "Mensaje confirmado")
            
        except Exception as e:
            logger.error("PROCESSING_ERROR", f"Error durante el procesamiento: {e}")
            
            # Crear reporte de error
            self.create_error_report(run_id, e, payload_dict)
            
            # NACK del mensaje (no requeue para evitar loops infinitos)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            logger.error("MESSAGE_NACK", "Mensaje rechazado")
    
    def save_metrics(self, metrics):
        """Guarda métricas en archivo JSON"""
        out_dir = Path("out")
        out_dir.mkdir(exist_ok=True)
        
        metrics_file = out_dir / "metrics.json"
        
        with open(metrics_file, "w", encoding="utf-8") as f:
            json.dump(metrics.model_dump(), f, indent=2, ensure_ascii=False)
        
        logger.info("SAVE_METRICS", f"Métricas guardadas en {metrics_file}")
    
    def create_error_report(self, run_id, exception, payload):
        """Crea reporte de error en archivo"""
        out_dir = Path("out")
        out_dir.mkdir(exist_ok=True)
        
        error_report = ErrorReport(
            run_id=run_id or "unknown",
            timestamp=datetime.utcnow().isoformat() + "Z",
            mensaje=str(exception),
            stacktrace_resumido=traceback.format_exc()[:1000],
            metricas=None,
            contexto={"payload": payload} if payload else None
        )
        
        error_file = out_dir / "error_report.json"
        
        with open(error_file, "w", encoding="utf-8") as f:
            json.dump(error_report.model_dump(), f, indent=2, ensure_ascii=False)
        
        logger.error("ERROR_REPORT", f"Reporte de error guardado en {error_file}")
    
    def start_consuming(self):
        """Inicia el consumo de mensajes"""
        try:
            channel = self.mq.connect()
            
            logger.info("CONSUMER_START", 
                       f"Consumidor iniciado. Esperando mensajes en {self.mq.queue_name}...")
            
            channel.basic_consume(
                queue=self.mq.queue_name,
                on_message_callback=self.callback,
                auto_ack=False
            )
            
            print("\n=== RPA Normalizador de Cuentas ===")
            print(f"Escuchando cola: {self.mq.queue_name}")
            print("Presiona CTRL+C para detener\n")
            
            channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("CONSUMER_STOP", "Consumidor detenido por usuario")
            self.mq.close()
        except Exception as e:
            logger.error("CONSUMER_ERROR", f"Error en consumidor: {e}")
            self.mq.close()
            raise
