"""Telemetry Generator."""
import time
import numpy as np
from typing import Dict, Any

from src.edge_simulator.config import SupplierProfile, EquipmentProfile, ProductLineProfile

class TelemetryGenerator:
    """Generates synthetic but realistic telemetry data."""

    def __init__(self, profile: SupplierProfile, product_line: ProductLineProfile, equipment: EquipmentProfile, speed_factor: float = 1.0, anomaly_mode: bool = False):
        """Initialize generator."""
        self.profile = profile
        self.product_line = product_line
        self.equipment = equipment
        self.speed_factor = speed_factor
        self.anomaly_mode = anomaly_mode
        self.current_time_ms = int(time.time() * 1000)
        self.step_count = 0

        # Base properties with slight random initialization
        self.temp_base = equipment.base_temperature_c
        self.pressure_base = equipment.base_pressure_psi
        self.vib_base = equipment.base_vibration_mm_s
        self.power_base = equipment.base_power_kw

        # For stateful drift and autocorrelation
        self.temp_offset = 0.0
        
    def generate(self) -> Dict[str, Any]:
        """Generate one telemetry event."""
        self.step_count += 1
        
        # Advance time based on cycle time and speed factor
        cycle_time = self.product_line.base_cycle_time_sec / self.speed_factor
        self.current_time_ms += int(cycle_time * 1000)

        # Base noise
        temp_noise = np.random.normal(0, 0.5)
        pressure_noise = np.random.normal(0, 1.0)
        vib_noise = np.random.normal(0, 0.1)
        
        # Drift
        self.temp_offset += np.random.normal(0, 0.05)
        # Bounded drift
        self.temp_offset = np.clip(self.temp_offset, -5.0, 5.0)

        # Anomalies
        is_anomaly = self.anomaly_mode or (np.random.random() < self.profile.anomaly_rate)
        
        anomaly_multiplier = 1.0
        if is_anomaly:
            anomaly_multiplier = np.random.uniform(1.2, 1.5)
            self.temp_offset += np.random.uniform(2.0, 5.0) # spike

        temperature_c = self.temp_base + self.temp_offset + temp_noise
        
        # Correlation: Pressure slightly correlates with temperature
        pressure_psi = self.pressure_base + (temperature_c - self.temp_base) * 0.5 + pressure_noise
        
        # Vibration correlates strongly with anomalies
        vibration_mm_s = self.vib_base * anomaly_multiplier + vib_noise
        
        # Power relates to cycle time efficiency and anomalies
        power_consumption_kw = self.power_base * (1.0 + (temperature_c - self.temp_base) * 0.01) * anomaly_multiplier
        
        # Yield and units
        units_produced = max(1, int(np.random.normal(self.product_line.capacity_per_hour / (3600 / self.product_line.base_cycle_time_sec), 0.5)))
        
        # Base yield rate is affected by anomalies
        current_yield = self.product_line.base_yield_rate
        if is_anomaly:
            current_yield *= 0.8
            
        units_passed = int(units_produced * current_yield)
        
        # Make sure passed isn't more than produced
        units_passed = min(units_produced, units_passed)

        return {
            "supplier_code": self.profile.supplier_code,
            "equipment_code": self.equipment.equipment_code,
            "product_line_code": self.product_line.line_code,
            "timestamp_ms": self.current_time_ms,
            "cycle_time_seconds": float(self.product_line.base_cycle_time_sec + np.random.normal(0, 0.5)),
            "units_produced": int(units_produced),
            "units_passed": int(units_passed),
            "temperature_c": float(temperature_c),
            "pressure_psi": float(pressure_psi),
            "vibration_mm_s": float(max(0, vibration_mm_s)),
            "power_consumption_kw": float(power_consumption_kw),
            "process_params": {
                "operator_id": f"OP_{np.random.randint(100, 999)}",
                "batch_id": f"BATCH_{self.step_count // 100}",
                "anomaly_flag": str(is_anomaly).lower()
            }
        }
