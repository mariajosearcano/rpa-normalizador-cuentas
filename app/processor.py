"""
Procesador de normalización de cuentas
"""
import csv
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
from dateutil import parser

from app.infra.dsi_logger import logger
from app.models import ProcessingMetrics


class CuentasProcessor:
    """Procesador de normalización de archivos CSV de cuentas"""
    
    ESTADOS_VALIDOS = {"PENDIENTE", "ENVIADA", "APROBADA", "RECHAZADA"}
    
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.registros_validos: List[Dict] = []
        self.registros_invalidos: List[Dict] = []
    
    def normalize_id_cuenta(self, id_cuenta: str) -> Tuple[bool, str]:
        """Normaliza id_cuenta: strip, mayúsculas, alfanumérico no vacío"""
        try:
            normalized = id_cuenta.strip().upper()
            if not normalized or not normalized.replace("-", "").replace("_", "").isalnum():
                return False, ""
            return True, normalized
        except Exception as e:
            logger.error("NORMALIZE_ID", f"Error normalizando id: {e}")
            return False, ""
    
    def normalize_fecha(self, fecha: str) -> Tuple[bool, str]:
        """Parsea fecha a ISO YYYY-MM-DD"""
        try:
            # Intentar parsear la fecha
            #dt = parser.parse(fecha, dayfirst=False)
            if "-" in fecha:
                dt = parser.parse(fecha, dayfirst=True)
            else:
                # Usar el comportamiento por defecto (que funciona bien con YYYY/MM/DD)
                dt = parser.parse(fecha)
            
            # Validar que la fecha sea válida (ej: no abril 31)
            if dt.day > 28 and dt.month == 2:
                return False, ""
            if dt.day > 30 and dt.month in [4, 6, 9, 11]:
                return False, ""
            if dt.day > 31:
                return False, ""
            
            return True, dt.strftime("%Y-%m-%d")
        except Exception as e:
            logger.error("NORMALIZE_FECHA", f"Error parseando fecha '{fecha}': {e}")
            return False, ""
    
    def normalize_monto(self, monto: str) -> Tuple[bool, float]:
        """Convierte monto a float positivo"""
        try:
            # Reemplazar comas por puntos
            monto_str = str(monto).strip().replace(",", ".")
            monto_float = float(monto_str)
            
            # Debe ser positivo
            if monto_float <= 0:
                return False, 0.0
            
            return True, round(monto_float, 2)
        except Exception as e:
            logger.error("NORMALIZE_MONTO", f"Error normalizando monto '{monto}': {e}")
            return False, 0.0
    
    def normalize_estado(self, estado: str) -> Tuple[bool, str]:
        """Normaliza estado a mayúsculas y valida contra lista"""
        try:
            normalized = estado.strip().upper()
            if normalized not in self.ESTADOS_VALIDOS:
                return False, ""
            return True, normalized
        except Exception as e:
            logger.error("NORMALIZE_ESTADO", f"Error normalizando estado: {e}")
            return False, ""
    
    def process_row(self, row: Dict, row_num: int) -> bool:
        """Procesa una fila individual. Retorna True si es válida"""
        # Validar id_cuenta
        valid_id, id_cuenta = self.normalize_id_cuenta(row.get("id_cuenta", ""))
        if not valid_id:
            logger.info("INVALID_ROW", f"Fila {row_num}: id_cuenta inválido", row=row)
            self.registros_invalidos.append({**row, "row_num": row_num, "reason": "id_cuenta_invalido"})
            return False
        
        # Validar fecha_emision
        valid_fecha, fecha = self.normalize_fecha(row.get("fecha_emision", ""))
        if not valid_fecha:
            logger.info("INVALID_ROW", f"Fila {row_num}: fecha_emision inválida", row=row)
            self.registros_invalidos.append({**row, "row_num": row_num, "reason": "fecha_invalida"})
            return False
        
        # Validar monto
        valid_monto, monto = self.normalize_monto(row.get("monto", ""))
        if not valid_monto:
            logger.info("INVALID_ROW", f"Fila {row_num}: monto inválido", row=row)
            self.registros_invalidos.append({**row, "row_num": row_num, "reason": "monto_invalido"})
            return False
        
        # Validar estado
        valid_estado, estado = self.normalize_estado(row.get("estado", ""))
        if not valid_estado:
            logger.info("INVALID_ROW", f"Fila {row_num}: estado inválido", row=row)
            self.registros_invalidos.append({**row, "row_num": row_num, "reason": "estado_invalido"})
            return False
        
        # Todos los campos son válidos
        self.registros_validos.append({
            "id_cuenta": id_cuenta,
            "fecha_emision": fecha,
            "monto": monto,
            "estado": estado
        })
        return True
    
    def process_file(self, filepath: str, umbral_error: float) -> ProcessingMetrics:
        """Procesa el archivo CSV completo"""
        start_time = time.time()
        
        logger.info("READ_CSV", f"Leyendo archivo: {filepath}")
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                
                for idx, row in enumerate(reader, start=1):
                    self.process_row(row, idx)
            
            # Calcular métricas
            total = len(self.registros_validos) + len(self.registros_invalidos)
            porcentaje_invalidos = len(self.registros_invalidos) / total if total > 0 else 0
            duracion_ms = (time.time() - start_time) * 1000
            
            logger.info("PROCESS_COMPLETE", 
                       f"Procesamiento completado: {len(self.registros_validos)} válidos, {len(self.registros_invalidos)} inválidos",
                       total=total,
                       validos=len(self.registros_validos),
                       invalidos=len(self.registros_invalidos),
                       porcentaje_invalidos=f"{porcentaje_invalidos:.2%}")
            
            # Verificar umbral de error
            if porcentaje_invalidos > umbral_error:
                raise ValueError(
                    f"Umbral de error excedido: {porcentaje_invalidos:.2%} > {umbral_error:.2%}"
                )
            
            # Guardar archivos de salida
            self.save_output()
            
            # Crear métricas
            metrics = ProcessingMetrics(
                run_id=self.run_id,
                totales=total,
                validos=len(self.registros_validos),
                invalidos=len(self.registros_invalidos),
                porcentaje_invalidos=round(porcentaje_invalidos * 100, 2),
                duracion_ms=round(duracion_ms, 2)
            )
            
            return metrics
            
        except Exception as e:
            logger.error("PROCESS_ERROR", f"Error procesando archivo: {e}")
            raise
    
    def save_output(self):
        """Guarda archivos de salida"""
        out_dir = Path("out")
        out_dir.mkdir(exist_ok=True)
        
        # Guardar CSV normalizado
        if self.registros_validos:
            output_file = out_dir / "cuentas_normalizadas.csv"
            logger.info("SAVE_OUTPUT", f"Guardando {len(self.registros_validos)} registros en {output_file}")
            
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                fieldnames = ["id_cuenta", "fecha_emision", "monto", "estado"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.registros_validos)