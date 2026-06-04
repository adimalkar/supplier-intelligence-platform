import numpy as np
from src.edge_simulator.config import get_supplier_profile
from src.edge_simulator.generators.telemetry import TelemetryGenerator

def test_telemetry_generation():
    profile = get_supplier_profile("PREC_MOTORS")
    pl = profile.product_lines[0]
    eq = pl.equipment[0]
    
    generator = TelemetryGenerator(profile, pl, eq)
    
    data = generator.generate()
    assert data["supplier_code"] == "PREC_MOTORS"
    assert data["equipment_code"] == eq.equipment_code
    assert "timestamp_ms" in data
    assert 0 <= data["units_passed"] <= data["units_produced"]
    assert "temperature_c" in data
    assert "pressure_psi" in data
    assert "vibration_mm_s" in data
    assert "power_consumption_kw" in data

def test_anomaly_injection():
    profile = get_supplier_profile("PREC_MOTORS")
    pl = profile.product_lines[0]
    eq = pl.equipment[0]
    
    generator = TelemetryGenerator(profile, pl, eq, anomaly_mode=True)
    data = generator.generate()
    
    assert data["process_params"]["anomaly_flag"] == "true"
    assert data["vibration_mm_s"] >= eq.base_vibration_mm_s

def test_correlation():
    profile = get_supplier_profile("PREC_MOTORS")
    pl = profile.product_lines[0]
    eq = pl.equipment[0]
    
    generator = TelemetryGenerator(profile, pl, eq)
    
    temps = []
    pressures = []
    
    for _ in range(100):
        data = generator.generate()
        temps.append(data["temperature_c"])
        pressures.append(data["pressure_psi"])
        
    correlation = np.corrcoef(temps, pressures)[0, 1]
    assert correlation > 0.0  # Should be positively correlated
