from dataclasses import dataclass, field
from typing import List

@dataclass
class EquipmentProfile:
    equipment_code: str
    base_temperature_c: float
    base_pressure_psi: float
    base_vibration_mm_s: float
    base_power_kw: float

@dataclass
class ProductLineProfile:
    line_code: str
    equipment: List[EquipmentProfile]
    base_cycle_time_sec: float
    base_yield_rate: float
    capacity_per_hour: int

@dataclass
class SupplierProfile:
    supplier_code: str
    product_lines: List[ProductLineProfile]
    failure_rate: float = 0.05
    anomaly_rate: float = 0.02


SUPPLIER_PROFILES = [
    SupplierProfile(
        supplier_code="PREC_MOTORS",
        product_lines=[
            ProductLineProfile(
                line_code="PREC_LINE_A",
                equipment=[
                    EquipmentProfile("PREC_SMT_01", 45.0, 100.0, 2.5, 12.0),
                    EquipmentProfile("PREC_WIND_01", 60.0, 80.0, 3.0, 15.0),
                    EquipmentProfile("PREC_AOI_01", 30.0, 50.0, 1.0, 5.0),
                ],
                base_cycle_time_sec=30.0,
                base_yield_rate=0.97,
                capacity_per_hour=120,
            ),
            ProductLineProfile(
                line_code="PREC_LINE_B",
                equipment=[
                    EquipmentProfile("PREC_SMT_02", 46.0, 101.0, 2.6, 12.5),
                    EquipmentProfile("PREC_WIND_02", 61.0, 81.0, 3.1, 15.5),
                    EquipmentProfile("PREC_TEST_01", 35.0, 60.0, 1.5, 8.0),
                ],
                base_cycle_time_sec=36.0,
                base_yield_rate=0.96,
                capacity_per_hour=100,
            ),
        ],
        failure_rate=0.03,
        anomaly_rate=0.01,
    ),
    SupplierProfile(
        supplier_code="SILK_PCB",
        product_lines=[
            ProductLineProfile(
                line_code="SILK_LINE_ML",
                equipment=[
                    EquipmentProfile("SILK_DRILL_01", 55.0, 120.0, 4.5, 20.0),
                    EquipmentProfile("SILK_ETCH_01", 70.0, 110.0, 2.0, 18.0),
                    EquipmentProfile("SILK_AOI_01", 30.0, 50.0, 1.0, 5.0),
                    EquipmentProfile("SILK_PRESS_01", 150.0, 300.0, 5.0, 50.0),
                ],
                base_cycle_time_sec=18.0,
                base_yield_rate=0.94,
                capacity_per_hour=200,
            ),
            ProductLineProfile(
                line_code="SILK_LINE_FX",
                equipment=[
                    EquipmentProfile("SILK_LASER_01", 80.0, 90.0, 2.0, 25.0),
                    EquipmentProfile("SILK_COAT_01", 60.0, 80.0, 1.5, 15.0),
                ],
                base_cycle_time_sec=45.0,
                base_yield_rate=0.92,
                capacity_per_hour=80,
            ),
        ],
        failure_rate=0.04,
        anomaly_rate=0.02,
    ),
    SupplierProfile(
        supplier_code="THERM_SYS",
        product_lines=[
            ProductLineProfile(
                line_code="THERM_LINE_HP",
                equipment=[
                    EquipmentProfile("THERM_BRAZE_01", 800.0, 50.0, 1.0, 100.0),
                    EquipmentProfile("THERM_TEST_01", 40.0, 40.0, 0.5, 10.0),
                    EquipmentProfile("THERM_LEAK_01", 35.0, 20.0, 0.5, 5.0),
                ],
                base_cycle_time_sec=72.0,
                base_yield_rate=0.98,
                capacity_per_hour=50,
            ),
        ],
        failure_rate=0.02,
        anomaly_rate=0.01,
    ),
    SupplierProfile(
        supplier_code="VOLT_BATT",
        product_lines=[
            ProductLineProfile(
                line_code="VOLT_LINE_MOD",
                equipment=[
                    EquipmentProfile("VOLT_WELD_01", 120.0, 80.0, 2.0, 30.0),
                    EquipmentProfile("VOLT_FORM_01", 50.0, 30.0, 1.0, 20.0),
                    EquipmentProfile("VOLT_XRAY_01", 30.0, 20.0, 0.5, 8.0),
                    EquipmentProfile("VOLT_EOL_01", 25.0, 20.0, 0.5, 5.0),
                ],
                base_cycle_time_sec=60.0,
                base_yield_rate=0.99,
                capacity_per_hour=60,
            ),
            ProductLineProfile(
                line_code="VOLT_LINE_PACK",
                equipment=[
                    EquipmentProfile("VOLT_STACK_01", 40.0, 60.0, 1.5, 10.0),
                    EquipmentProfile("VOLT_BMS_01", 30.0, 20.0, 0.5, 5.0),
                ],
                base_cycle_time_sec=180.0,
                base_yield_rate=0.995,
                capacity_per_hour=20,
            ),
        ],
        failure_rate=0.01,
        anomaly_rate=0.005,
    ),
    SupplierProfile(
        supplier_code="CLEAR_OPT",
        product_lines=[
            ProductLineProfile(
                line_code="CLEAR_LINE_CAM",
                equipment=[
                    EquipmentProfile("CLEAR_PLACE_01", 35.0, 40.0, 1.0, 8.0),
                    EquipmentProfile("CLEAR_ALIGN_01", 30.0, 30.0, 0.5, 5.0),
                    EquipmentProfile("CLEAR_AOI_01", 30.0, 50.0, 1.0, 5.0),
                    EquipmentProfile("CLEAR_MTF_01", 25.0, 20.0, 0.5, 4.0),
                    EquipmentProfile("CLEAR_CLEAN_01", 22.0, 15.0, 0.2, 10.0),
                ],
                base_cycle_time_sec=24.0,
                base_yield_rate=0.95,
                capacity_per_hour=150,
            ),
        ],
        failure_rate=0.03,
        anomaly_rate=0.02,
    ),
]

def get_supplier_profile(code: str) -> SupplierProfile:
    for profile in SUPPLIER_PROFILES:
        if profile.supplier_code == code:
            return profile
    raise ValueError(f"Supplier code {code} not found.")
