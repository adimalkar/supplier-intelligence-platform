import pytest
from src.pipeline.transforms.telemetry import clean_telemetry

def test_clean_telemetry_null_handling():
    payload = {
        "temperature_c": None,
        "pressure_psi": None,
        "vibration_mm_s": None,
        "power_consumption_kw": None,
    }
    cleaned = clean_telemetry(payload)
    assert cleaned["temperature_c"] == 0.0
    assert cleaned["pressure_psi"] == 0.0
    assert cleaned["vibration_mm_s"] == 0.0
    assert cleaned["power_consumption_kw"] == 0.0

def test_clean_telemetry_clipping():
    payload = {
        "temperature_c": 3000.0,
        "pressure_psi": -50.0,
        "vibration_mm_s": -10.0,
        "power_consumption_kw": 100.0,
    }
    cleaned = clean_telemetry(payload)
    assert cleaned["temperature_c"] == 2000.0
    assert cleaned["pressure_psi"] == 0.0
    assert cleaned["vibration_mm_s"] == 0.0
    assert cleaned["power_consumption_kw"] == 100.0
