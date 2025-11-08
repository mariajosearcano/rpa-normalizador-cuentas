"""
DSI Logger - Sistema de logging estructurado para observabilidad
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class DSILogger:
    """Logger estructurado que escribe en consola y archivo JSONL"""
    
    def __init__(self):
        self.bot_name: Optional[str] = None
        self.run_id: Optional[str] = None
        self.log_file: Optional[Path] = None
    
    def init(self, bot_name: str, run_id: str) -> None:
        """Inicializa el logger con nombre de bot y run_id"""
        self.bot_name = bot_name
        self.run_id = run_id
        
        # Crear directorio de logs
        log_dir = Path("out")
        log_dir.mkdir(exist_ok=True)
        
        self.log_file = log_dir / "logs.jsonl"
        
        self.info("INIT", f"Logger inicializado para {bot_name}", run_id=run_id)
    
    def _write_log(self, level: str, step: str, message: str, **kv) -> None:
        """Escribe log en consola y archivo"""
        log_entry = {
            #"ts": datetime.utcnow().isoformat() + "Z",
            "ts": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "bot_name": self.bot_name,
            "run_id": self.run_id,
            "level": level,
            "step": step,
            "message": message,
            **kv
        }
        
        # Consola con formato legible
        console_msg = f"[{level}] [{step}] {message}"
        if kv:
            console_msg += f" | {kv}"
        print(console_msg)
        
        # Archivo JSONL
        if self.log_file:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def info(self, step: str, message: str, **kv) -> None:
        """Log de nivel INFO"""
        self._write_log("INFO", step, message, **kv)
    
    def error(self, step: str, message: str, **kv) -> None:
        """Log de nivel ERROR"""
        self._write_log("ERROR", step, message, **kv)
    
    def metric(self, name: str, value: float, **labels) -> None:
        """Registra una métrica"""
        self._write_log("METRIC", "METRICS", f"{name}={value}", **labels)


# Instancia global del logger
logger = DSILogger()