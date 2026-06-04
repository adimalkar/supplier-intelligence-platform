# Data Dictionary

## Dimensions
- **dim_suppliers**: Information about manufacturing suppliers.
- **dim_product_lines**: Production lines mapped to suppliers.
- **dim_equipment**: Machines on a product line.
- **dim_defect_types**: Master list of defect categories.

## Facts
- **fact_production_runs**: Aggregated performance per run (OEE, Yield).
- **fact_quality_inspections**: Individual defect detection events from visual or CV inspections.
- **fact_equipment_events**: Raw telemetry down-sampled into events (temperature, pressure, etc).
