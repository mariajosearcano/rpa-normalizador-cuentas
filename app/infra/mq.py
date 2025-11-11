# """
# Utilidades para RabbitMQ
# """
# import pika
# import os
# from typing import Optional
# from app.infra.dsi_logger import logger


# class RabbitMQConnection:
#     """Gestiona la conexión a RabbitMQ"""
    
#     def __init__(self):
#         self.connection: Optional[pika.BlockingConnection] = None
#         self.channel: Optional[pika.channel.Channel] = None
#         self.amqp_url = os.getenv("AMQP_URL", "amqp://admin:admin123@localhost:5672/")
#         self.queue_name = os.getenv("RABBITMQ_QUEUE", "rpa.cuentas.normalizar.v1")
#         self.exchange_name = os.getenv("RABBITMQ_EXCHANGE", "rpa.direct")
#         self.routing_key = os.getenv("RABBITMQ_ROUTING_KEY", "rpa.cuentas.normalizar.v1")
    
#     def connect(self) -> pika.channel.Channel:
#         """Establece conexión con RabbitMQ"""
#         try:
#             logger.info("MQ_CONNECT", f"Conectando a RabbitMQ: {self.amqp_url}")
            
#             # Parsear URL
#             params = pika.URLParameters(self.amqp_url)
#             params.socket_timeout = 10
#             params.heartbeat = 600
            
#             # Crear conexión
#             self.connection = pika.BlockingConnection(params)
#             self.channel = self.connection.channel()
            
#             # Declarar exchange
#             self.channel.exchange_declare(
#                 exchange=self.exchange_name,
#                 exchange_type='direct',
#                 durable=True
#             )
            
#             # Declarar cola
#             self.channel.queue_declare(
#                 queue=self.queue_name,
#                 durable=True
#             )
            
#             # Bind
#             self.channel.queue_bind(
#                 exchange=self.exchange_name,
#                 queue=self.queue_name,
#                 routing_key=self.routing_key
#             )
            
#             # Configurar QoS
#             self.channel.basic_qos(prefetch_count=1)
            
#             logger.info("MQ_CONNECT", "Conexión establecida exitosamente")
#             return self.channel
            
#         except Exception as e:
#             logger.error("MQ_CONNECT", f"Error conectando a RabbitMQ: {e}")
#             raise
    
#     def close(self):
#         """Cierra la conexión"""
#         if self.connection and not self.connection.is_closed:
#             logger.info("MQ_CLOSE", "Cerrando conexión")
#             self.connection.close()
    
#     def publish_message(self, message: str):
#         """Publica un mensaje en la cola"""
#         if not self.channel:
#             raise RuntimeError("No hay conexión activa")
        
#         self.channel.basic_publish(
#             exchange=self.exchange_name,
#             routing_key=self.routing_key,
#             body=message,
#             properties=pika.BasicProperties(
#                 delivery_mode=2,  # Mensaje persistente
#                 content_type='application/json'
#             )
#         )
#         logger.info("MQ_PUBLISH", f"Mensaje publicado en {self.queue_name}")