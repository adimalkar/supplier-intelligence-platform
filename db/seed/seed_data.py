
"""
SIE Analytics — Seed Data.

Populates the database with 5 realistic supplier profiles, their product lines,
equipment, and defect type definitions.

Usage:
    python -m db.seed.seed_data

Run after: make db-migrate
"""

from __future__ import annotations

import logging
import sys
from datetime import date
from pathlib import Path

# Add project root to path so we can import src.common
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.common.db.connection import get_session, init_session_factory
from src.common.db.models import DimDefectType, DimEquipment, DimProductLine, DimSupplier

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SUPPLIER PROFILES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUPPLIERS = [
    {
        "supplier_code": "PREC_MOTORS",
        "name": "Precision Motors Co.",
        "location": "Shanghai, China",
        "tier": "tier_1",
        "contact_info": {
            "primary": "wei.zhang@precmotors.com",
            "phone": "+86-21-5555-0101",
            "quality_lead": "li.chen@precmotors.com",
        },
        "product_lines": [
            {
                "line_code": "PREC_LINE_A",
                "name": "Drive Motor Assembly Line A",
                "product_type": "electric_motor",
                "specifications": {
                    "capacity_per_hour": 120,
                    "target_oee": 0.88,
                    "target_yield": 0.97,
                },
                "equipment": [
                    {"code": "PREC_SMT_01", "type": "smt_machine", "manufacturer": "Siemens", "install_date": "2023-01-15"},
                    {"code": "PREC_WIND_01", "type": "winding_machine", "manufacturer": "Nidec", "install_date": "2023-02-01"},
                    {"code": "PREC_AOI_01", "type": "aoi_inspector", "manufacturer": "Koh Young", "install_date": "2023-03-10"},
                ],
            },
            {
                "line_code": "PREC_LINE_B",
                "name": "Drive Motor Assembly Line B",
                "product_type": "electric_motor",
                "specifications": {
                    "capacity_per_hour": 100,
                    "target_oee": 0.85,
                    "target_yield": 0.96,
                },
                "equipment": [
                    {"code": "PREC_SMT_02", "type": "smt_machine", "manufacturer": "Siemens", "install_date": "2023-06-01"},
                    {"code": "PREC_WIND_02", "type": "winding_machine", "manufacturer": "Nidec", "install_date": "2023-06-15"},
                    {"code": "PREC_TEST_01", "type": "end_of_line_tester", "manufacturer": "National Instruments", "install_date": "2023-07-01"},
                ],
            },
        ],
    },
    {
        "supplier_code": "SILK_PCB",
        "name": "SilkBoard PCB Ltd.",
        "location": "Taipei, Taiwan",
        "tier": "tier_1",
        "contact_info": {
            "primary": "jason.wu@silkpcb.tw",
            "phone": "+886-2-5555-0202",
            "quality_lead": "mei.lin@silkpcb.tw",
        },
        "product_lines": [
            {
                "line_code": "SILK_LINE_ML",
                "name": "Multi-Layer PCB Production",
                "product_type": "pcb_multilayer",
                "specifications": {
                    "capacity_per_hour": 200,
                    "target_oee": 0.82,
                    "target_yield": 0.94,
                    "layers": 12,
                },
                "equipment": [
                    {"code": "SILK_DRILL_01", "type": "cnc_drill", "manufacturer": "Schmoll", "install_date": "2022-09-01"},
                    {"code": "SILK_ETCH_01", "type": "etching_machine", "manufacturer": "Atotech", "install_date": "2022-09-15"},
                    {"code": "SILK_AOI_01", "type": "aoi_inspector", "manufacturer": "Orbotech", "install_date": "2022-10-01"},
                    {"code": "SILK_PRESS_01", "type": "lamination_press", "manufacturer": "Burkle", "install_date": "2022-10-15"},
                ],
            },
            {
                "line_code": "SILK_LINE_FX",
                "name": "Flex PCB Production",
                "product_type": "pcb_flex",
                "specifications": {
                    "capacity_per_hour": 80,
                    "target_oee": 0.78,
                    "target_yield": 0.92,
                },
                "equipment": [
                    {"code": "SILK_LASER_01", "type": "laser_cutter", "manufacturer": "LPKF", "install_date": "2023-01-20"},
                    {"code": "SILK_COAT_01", "type": "coating_machine", "manufacturer": "Nordson", "install_date": "2023-02-05"},
                ],
            },
        ],
    },
    {
        "supplier_code": "THERM_SYS",
        "name": "ThermalTech Systems",
        "location": "Fremont, CA, USA",
        "tier": "tier_2",
        "contact_info": {
            "primary": "david.kumar@thermaltech.com",
            "phone": "+1-510-555-0303",
            "quality_lead": "sarah.johnson@thermaltech.com",
        },
        "product_lines": [
            {
                "line_code": "THERM_LINE_HP",
                "name": "Heat Pipe Assembly",
                "product_type": "thermal_management",
                "specifications": {
                    "capacity_per_hour": 50,
                    "target_oee": 0.90,
                    "target_yield": 0.98,
                    "thermal_rating_w": 150,
                },
                "equipment": [
                    {"code": "THERM_BRAZE_01", "type": "brazing_furnace", "manufacturer": "Ipsen", "install_date": "2022-05-01"},
                    {"code": "THERM_TEST_01", "type": "thermal_tester", "manufacturer": "Mentor Graphics", "install_date": "2022-05-15"},
                    {"code": "THERM_LEAK_01", "type": "leak_detector", "manufacturer": "Inficon", "install_date": "2022-06-01"},
                ],
            },
        ],
    },
    {
        "supplier_code": "VOLT_BATT",
        "name": "VoltEdge Batteries",
        "location": "Nagoya, Japan",
        "tier": "tier_1",
        "contact_info": {
            "primary": "takeshi.honda@voltedge.jp",
            "phone": "+81-52-555-0404",
            "quality_lead": "yuki.tanaka@voltedge.jp",
        },
        "product_lines": [
            {
                "line_code": "VOLT_LINE_MOD",
                "name": "Battery Module Assembly",
                "product_type": "battery_module",
                "specifications": {
                    "capacity_per_hour": 60,
                    "target_oee": 0.92,
                    "target_yield": 0.99,
                    "cell_chemistry": "NMC811",
                },
                "equipment": [
                    {"code": "VOLT_WELD_01", "type": "laser_welder", "manufacturer": "Trumpf", "install_date": "2023-03-01"},
                    {"code": "VOLT_FORM_01", "type": "formation_cycler", "manufacturer": "Arbin", "install_date": "2023-03-15"},
                    {"code": "VOLT_XRAY_01", "type": "xray_inspector", "manufacturer": "Nikon", "install_date": "2023-04-01"},
                    {"code": "VOLT_EOL_01", "type": "end_of_line_tester", "manufacturer": "Chroma", "install_date": "2023-04-15"},
                ],
            },
            {
                "line_code": "VOLT_LINE_PACK",
                "name": "Battery Pack Assembly",
                "product_type": "battery_pack",
                "specifications": {
                    "capacity_per_hour": 20,
                    "target_oee": 0.88,
                    "target_yield": 0.995,
                },
                "equipment": [
                    {"code": "VOLT_STACK_01", "type": "stacking_machine", "manufacturer": "Custom", "install_date": "2023-08-01"},
                    {"code": "VOLT_BMS_01", "type": "bms_programmer", "manufacturer": "dSPACE", "install_date": "2023-08-15"},
                ],
            },
        ],
    },
    {
        "supplier_code": "CLEAR_OPT",
        "name": "ClearVision Optics",
        "location": "Shenzhen, China",
        "tier": "tier_2",
        "contact_info": {
            "primary": "anna.wong@clearvision.cn",
            "phone": "+86-755-555-0505",
            "quality_lead": "peter.liu@clearvision.cn",
        },
        "product_lines": [
            {
                "line_code": "CLEAR_LINE_CAM",
                "name": "Camera Module Assembly",
                "product_type": "camera_module",
                "specifications": {
                    "capacity_per_hour": 150,
                    "target_oee": 0.84,
                    "target_yield": 0.95,
                    "resolution_mp": 8,
                },
                "equipment": [
                    {"code": "CLEAR_PLACE_01", "type": "die_bonder", "manufacturer": "ASM Pacific", "install_date": "2023-05-01"},
                    {"code": "CLEAR_ALIGN_01", "type": "active_alignment", "manufacturer": "AMS", "install_date": "2023-05-15"},
                    {"code": "CLEAR_AOI_01", "type": "aoi_inspector", "manufacturer": "Cognex", "install_date": "2023-06-01"},
                    {"code": "CLEAR_MTF_01", "type": "mtf_tester", "manufacturer": "Trioptics", "install_date": "2023-06-15"},
                    {"code": "CLEAR_CLEAN_01", "type": "cleanroom_unit", "manufacturer": "Daikin", "install_date": "2023-05-01"},
                ],
            },
        ],
    },
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DEFECT TYPES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DEFECT_TYPES = [
    {"code": "SCRATCH", "name": "Surface Scratch", "severity": "minor", "category": "visual", "description": "Visible scratch on component surface"},
    {"code": "MISALIGN", "name": "Component Misalignment", "severity": "major", "category": "dimensional", "description": "Component placed outside tolerance"},
    {"code": "SOLDER_BRIDGE", "name": "Solder Bridge", "severity": "critical", "category": "electrical", "description": "Unintended solder connection between pads"},
    {"code": "MISSING_COMP", "name": "Missing Component", "severity": "critical", "category": "visual", "description": "Component absent from expected position"},
    {"code": "COLD_SOLDER", "name": "Cold Solder Joint", "severity": "major", "category": "electrical", "description": "Insufficient solder wetting"},
    {"code": "CRACK", "name": "Substrate Crack", "severity": "critical", "category": "mechanical", "description": "Crack in PCB substrate or component"},
    {"code": "DISCOLOR", "name": "Discoloration", "severity": "minor", "category": "visual", "description": "Abnormal coloration indicating thermal damage"},
    {"code": "DELAMINATION", "name": "Layer Delamination", "severity": "major", "category": "mechanical", "description": "Separation between PCB layers"},
    {"code": "VOID", "name": "Solder Void", "severity": "minor", "category": "electrical", "description": "Air pocket in solder joint (>25% void ratio)"},
    {"code": "CONTAM", "name": "Foreign Contamination", "severity": "major", "category": "visual", "description": "Foreign material on component or substrate"},
    {"code": "DIM_OOT", "name": "Dimensional Out-of-Tolerance", "severity": "major", "category": "dimensional", "description": "Measured dimension outside specification"},
    {"code": "WELD_DEFECT", "name": "Weld Defect", "severity": "critical", "category": "mechanical", "description": "Weld penetration or strength below specification"},
]


def seed_database() -> None:
    """Seed the database with supplier profiles, product lines, equipment, and defect types."""
    init_session_factory()

    with get_session() as session:
        # Check if already seeded
        existing = session.query(DimSupplier).first()
        if existing:
            logger.info("Database already seeded (found supplier: %s). Skipping.", existing.name)
            return

        # ── Seed Defect Types ──
        logger.info("Seeding defect types...")
        for defect_data in DEFECT_TYPES:
            session.add(DimDefectType(**defect_data))
        session.flush()
        logger.info("  → %d defect types created", len(DEFECT_TYPES))

        # ── Seed Suppliers + Product Lines + Equipment ──
        total_lines = 0
        total_equipment = 0

        for supplier_data in SUPPLIERS:
            product_lines_data = supplier_data.pop("product_lines")

            supplier = DimSupplier(
                supplier_code=supplier_data["supplier_code"],
                name=supplier_data["name"],
                location=supplier_data["location"],
                tier=supplier_data["tier"],
                contact_info=supplier_data["contact_info"],
            )
            session.add(supplier)
            session.flush()  # Get supplier_id
            logger.info("  → Created supplier: %s (%s)", supplier.name, supplier.supplier_code)

            for line_data in product_lines_data:
                equipment_list = line_data.pop("equipment")

                product_line = DimProductLine(
                    supplier_id=supplier.supplier_id,
                    line_code=line_data["line_code"],
                    name=line_data["name"],
                    product_type=line_data["product_type"],
                    specifications=line_data.get("specifications", {}),
                )
                session.add(product_line)
                session.flush()  # Get product_line_id
                total_lines += 1

                for equip_data in equipment_list:
                    equipment = DimEquipment(
                        product_line_id=product_line.product_line_id,
                        equipment_code=equip_data["code"],
                        equipment_type=equip_data["type"],
                        manufacturer=equip_data["manufacturer"],
                        install_date=date.fromisoformat(equip_data["install_date"]),
                        maintenance_schedule={
                            "preventive_interval_days": 30,
                            "last_maintenance": None,
                        },
                    )
                    session.add(equipment)
                    total_equipment += 1

        logger.info(
            "✅ Seed complete: %d suppliers, %d product lines, %d equipment, %d defect types",
            len(SUPPLIERS),
            total_lines,
            total_equipment,
            len(DEFECT_TYPES),
        )


if __name__ == "__main__":
    seed_database()
