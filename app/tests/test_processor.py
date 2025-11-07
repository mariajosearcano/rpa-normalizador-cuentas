"""
Tests para el procesador de cuentas
"""
import pytest
from app.processor import CuentasProcessor


def test_normalize_id_cuenta_valid():
    """Test normalización de ID válido"""
    processor = CuentasProcessor("test-run")
    
    valid, result = processor.normalize_id_cuenta(" cx-001 ")
    assert valid is True
    assert result == "CX-001"


def test_normalize_id_cuenta_invalid_empty():
    """Test normalización de ID vacío"""
    processor = CuentasProcessor("test-run")
    
    valid, result = processor.normalize_id_cuenta("   ")
    assert valid is False


def test_normalize_fecha_valid():
    """Test normalización de fecha válida"""
    processor = CuentasProcessor("test-run")
    
    valid, result = processor.normalize_fecha("2024/01/05")
    assert valid is True
    assert result == "2024-01-05"
    
    valid, result = processor.normalize_fecha("05-02-2024")
    assert valid is True
    assert result == "2024-02-05"


def test_normalize_fecha_invalid():
    """Test normalización de fecha inválida"""
    processor = CuentasProcessor("test-run")
    
    # Abril 31 no existe
    valid, result = processor.normalize_fecha("2024-04-31")
    assert valid is False
    
    # Fecha completamente inválida
    valid, result = processor.normalize_fecha("invalid-date")
    assert valid is False


def test_normalize_monto_valid():
    """Test normalización de monto válido"""
    processor = CuentasProcessor("test-run")
    
    valid, result = processor.normalize_monto("1000")
    assert valid is True
    assert result == 1000.0
    
    valid, result = processor.normalize_monto("2500,50")
    assert valid is True
    assert result == 2500.50


def test_normalize_monto_invalid_negative():
    """Test normalización de monto negativo"""
    processor = CuentasProcessor("test-run")
    
    valid, result = processor.normalize_monto("-50")
    assert valid is False


def test_normalize_estado_valid():
    """Test normalización de estado válido"""
    processor = CuentasProcessor("test-run")
    
    valid, result = processor.normalize_estado("enviada")
    assert valid is True
    assert result == "ENVIADA"
    
    valid, result = processor.normalize_estado(" APROBADA ")
    assert valid is True
    assert result == "APROBADA"


def test_normalize_estado_invalid():
    """Test normalización de estado inválido"""
    processor = CuentasProcessor("test-run")
    
    valid, result = processor.normalize_estado("estado_invalido")
    assert valid is False


def test_process_row_valid():
    """Test procesamiento de fila válida"""
    processor = CuentasProcessor("test-run")
    
    row = {
        "id_cuenta": "cx-001",
        "fecha_emision": "2024/01/05",
        "monto": "1000",
        "estado": "enviada"
    }
    
    result = processor.process_row(row, 1)
    assert result is True
    assert len(processor.registros_validos) == 1
    assert len(processor.registros_invalidos) == 0


def test_process_row_invalid():
    """Test procesamiento de fila inválida"""
    processor = CuentasProcessor("test-run")
    
    row = {
        "id_cuenta": "",
        "fecha_emision": "2024/01/05",
        "monto": "1000",
        "estado": "enviada"
    }
    
    result = processor.process_row(row, 1)
    assert result is False
    assert len(processor.registros_validos) == 0
    assert len(processor.registros_invalidos) == 1