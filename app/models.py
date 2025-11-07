"""
Modelos de datos y validaciones
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class MessagePayload(BaseModel):
    """Estructura del mensaje recibido desde RabbitMQ"""
    run_id: str
    archivo: str
    operacion: str
    umbral_error: float = Field(ge=0.0, le=1.0)
    meta: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('umbral_error')
    @classmethod
    def validate_umbral(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("umbral_error debe estar entre 0 y 1")
        return v


class CuentaRow(BaseModel):
    """Modelo de una fila de cuenta"""
    id_cuenta: str
    fecha_emision: str
    monto: float
    estado: str


class ProcessingMetrics(BaseModel):
    """Métricas del procesamiento"""
    run_id: str
    totales: int
    validos: int
    invalidos: int
    porcentaje_invalidos: float
    duracion_ms: float
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ErrorReport(BaseModel):
    """Reporte de error estructurado"""
    run_id: str
    timestamp: str
    mensaje: str
    stacktrace_resumido: str
    metricas: Optional[Dict[str, Any]] = None
    contexto: Optional[Dict[str, Any]] = None