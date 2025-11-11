import pytest
from pydantic import ValidationError
from app.models import MessagePayload, ProcessingMetrics, CuentaRow


def test_messagepayload_valid():
    mp = MessagePayload(run_id="1", archivo="a.csv", operacion="proc", umbral_error=0.2)
    assert mp.umbral_error == 0.2


def test_messagepayload_umbral_invalid():
    with pytest.raises(ValidationError):
        MessagePayload(run_id="1", archivo="a.csv", operacion="proc", umbral_error=1.5)


def test_processingmetrics_timestamp_default():
    m = ProcessingMetrics(run_id="r", totales=1, validos=1, invalidos=0, porcentaje_invalidos=0.0, duracion_ms=10.0)
    assert isinstance(m.timestamp, str) and len(m.timestamp) > 0


def test_cuentarow_basic():
    c = CuentaRow(id_cuenta="CX1", fecha_emision="2025-01-01", monto=100.0, estado="PENDIENTE")
    assert c.monto == 100.0